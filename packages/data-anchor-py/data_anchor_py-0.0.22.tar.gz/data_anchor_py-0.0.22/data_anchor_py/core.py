import time
import struct
from abc import abstractmethod
from dataclasses import dataclass, field, asdict
from multiprocessing import Semaphore
from multiprocessing import Event as multiprocessingEvent
from multiprocessing.shared_memory import SharedMemory
from threading import Thread
from threading import Event as ThreadingEvent
import atexit


class DataAnchor:
    """Base class for shared memory-enabled functionality."""
    _HEADER_SIZE = 16 # Data Length (4) + Timestamp (8) + Sequence Counter (4)
    _instances = {}
    _write_semaphore = Semaphore(1)
    _read_semaphore = Semaphore()
    atexit.register(lambda: [instance.close_shared_memory() for instance in DataAnchor._instances.values()])
    def __new__(cls,*args, **kwargs) :
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls]=instance
        return cls._instances[cls]

    def __init__(self):
        
        if hasattr(self,"_initialized") and self._initialized:
            return
        self.shm: SharedMemory | None = None
        self.init_size = 128
        self.current_size = 0
        self.cleanBufferArray = bytes(self.init_size)  # Initialize the clean buffer
        self.shm = SharedMemory(name=self.__class__.__name__, create=True, size=self.init_size)
        self.update_timeout = 1000
        self.sequence_counter = 0
        self._initialized = True
        self.last_read_time = 0
    
    @classmethod
    def reset_instance(cls, *args, **kwargs):
        cls._instances.pop(cls, None)
        return cls(*args, **kwargs)
    
    
    def ensure_size(self, newSize:int) -> None:
        total_size = self._HEADER_SIZE + newSize
        if self.shm and total_size > len(self.shm.buf):
                try:
                    self.close_shared_memory()      
                    total_size+=self.init_size
                    self.cleanBufferArray = bytes(newSize)
                    self.shm = SharedMemory(name=self.__class__.__name__,create=True, size=newSize)
                except Exception as e:
                    self.close_shared_memory(e)
        else:
            # raise Exception("Shared Memory not initialized")
            pass
        
    @abstractmethod
    def to_bytes(self) -> bytes:
        """
        Convert attributes to bytes. SERIALIZE Data
        Override this method in the child class for custom serialization.
        """
        raise NotImplementedError("to_bytes must be implemented by subclasses.")

    @abstractmethod
    def from_bytes_dict(self, data: bytes):
        """
        Convert bytes to a dictionary. Deserialize Data
        Override this method in the child class for custom deserialization.
        """
        raise NotImplementedError("from_bytes must be implemented by subclasses.")
    
                
    def pull(self, blocking: bool = True):
        """Read data from shared memory."""
        if self.shm is None:
            return False

        read_acquired = self._read_semaphore.acquire(block=blocking)
        if not read_acquired:
            if not blocking:
                return False
            raise Exception("Failed to acquire read lock (blocking mode).")

        try:
            # Ensure no active writers
            with self._write_semaphore:
                cur_time = int(time.time() * 1e7)
                # Attempt to read shared memory
                # Read Meta Data
                data_length = struct.unpack(">I", self.shm.buf[0:4])[0]
                stored_timestamp = struct.unpack(">Q", self.shm.buf[4:12])[0]
                stored_sequence = struct.unpack(">I", self.shm.buf[12:16])[0]
                
                if not self._store_is_latest_(stored_timestamp,stored_sequence,self.last_read_time):
                    return None
                self.last_read_time = stored_timestamp
                # Read and Deserialize Data
                data_bytes =  bytes(self.shm.buf[self._HEADER_SIZE:self._HEADER_SIZE+data_length])

                # Deserialize data
                data = self.from_bytes_dict(data_bytes)
                self.__dict__.update(data)
                return True

        except Exception as e:
            raise
            
        finally:
            self._read_semaphore.release()

    
    def _store_is_latest_(self,stored_timestamp,stored_sequence,cur_time):
        return stored_timestamp >= cur_time and stored_sequence >= self.sequence_counter
    

    def push(self, blocking: bool = True, ensure_latest: bool = True):
        """Write data to shared memory."""
        if self.shm is None:
            self.close_shared_memory(exception=Exception("Shared Memory not initialized"))
            return False

        # Attempt to acquire the write semaphore
        write_acquired = self._write_semaphore.acquire(block=blocking)
        if not write_acquired:
            if not blocking:
                return False
            raise Exception("Failed to acquire write lock (blocking mode).")

        try:
            # Block new readers by acquiring the read semaphore
            with self._read_semaphore:
                cur_time = int(time.time() * 1e7)

                # Serialize the data
                data_bytes = self.to_bytes()
                data_length = len(data_bytes)

                # Ensure shared memory has enough space
                self.ensure_size(data_length)

                # Read the current metadata
                stored_timestamp = struct.unpack(">Q", self.shm.buf[4:12])[0]
                stored_sequence = struct.unpack(">I", self.shm.buf[12:16])[0]

                # Increment sequence counter
                self.sequence_counter = (self.sequence_counter + 1) % (2 ** 32)

                # Check if the data is the latest
                if self._store_is_latest_(
                    stored_timestamp=stored_timestamp,
                    stored_sequence=stored_sequence,
                    cur_time=cur_time
                ) and ensure_latest:
                    return False

                # Clear the buffer
                self.shm.buf[0:] = self.cleanBufferArray[:len(self.shm.buf)]

                # Write metadata
                self.shm.buf[0:4] = struct.pack(">I", data_length)
                self.shm.buf[4:12] = struct.pack(">Q", cur_time)
                self.shm.buf[12:16] = struct.pack(">I", self.sequence_counter)

                # Write the actual data
                self.shm.buf[self._HEADER_SIZE:self._HEADER_SIZE + data_length] = data_bytes

        except Exception as e:
            raise Exception(f"Failed to push data: {e}")
        finally:
            # Release the write semaphore
            self._write_semaphore.release()
            return True
            
    def close_shared_memory(self, exception: Exception | None = None):
        """Close and unlink shared memory."""
        if self.shm:
            try:
                self.shm.buf[:] = self.cleanBufferArray[:len(self.shm.buf)]
                self.shm.close()
                self.shm.unlink()
            except BufferError as be:
                raise be
            except Exception as e:
                raise e
            finally:
                self.shm = None
        if exception:
            raise exception
    
    def __del__(self):
        self.close_shared_memory()
        self._initialized = False

class LiveDataAnchor(DataAnchor):
    def __init__(self):
        super().__init__()
        self._time_out = 0.1
        self._stop_event = ThreadingEvent()
        self._update_event = ThreadingEvent()
        self._update_thread = Thread(target=self._watch_for_updates, daemon=True)
        self._update_thread.start()
    
    def _watch_for_updates(self):
        """Background thread to watch for updates."""
        while not self._stop_event.is_set():
            if self._update_event.wait(self._time_out):
                self._update_event.clear()
                try:
                    self.pull()
                except Exception as e:
                    raise e

    def sync(self, blocking: bool = True, ensure_latest: bool = True):
        """Synchronize the shared memory with the latest data."""
        if super().push(blocking, ensure_latest):
            self._update_event.set()
            return True
        return False
    
    def stop(self):
        """Stop the background thread."""
        self._stop_event.set()
        if self._update_thread.is_alive():
            self._update_thread.join()
    
    def __del__(self):
        try:
            self.stop()
        except Exception as e:
            pass
        finally:
            super().__del__()