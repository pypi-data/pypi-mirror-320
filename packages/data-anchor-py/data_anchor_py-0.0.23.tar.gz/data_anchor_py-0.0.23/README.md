# DataAnchor

**DataAnchor** is a Python library that enables seamless **shared memory synchronization** for Python dataclasses. 

It provides a thread-safe and process-safe mechanism to share data between processes and threads, making it ideal for lightweight **Inter-Process Communication (IPC)** scenarios. It's built to be simple to use: just inherit the `DataAnchor` class into your dataclass, and its attributes will automatically be shared across processes.

You can also customize how your data is serialized and deserialized—just ensure the deserialization results in a dictionary matching the class's attributes.

This library was born out of a personal need to solve the critical problem of sharing data between processes and threads in a way that minimizes complexity and avoids common headaches. I hope it can help you too!

While I'm currently using **DataAnchor** for distributed systems within the same program, I'm actively working on extending its capabilities to support communication across different programs and even networks.

The larger vision is to create a simple **PubSub system** using shared_memory as the transport for sharing data seamlessly across programs and machines.

---

## Key Features

- **Lightweight Shared Memory**:
  Use Python's `multiprocessing.shared_memory` to share data across processes with minimal overhead.
  
- **Thread and Process Safety**:
  Prevent race conditions with semaphores, ensuring synchronized reads and writes.

- **Dataclass Integration**:
  Enhance Python dataclasses with shared memory capabilities by inheriting from `DataAnchor`.

- **Custom Serialization**:
  Customize how your data is serialized and deserialized for flexible and efficient IPC.

- **Singleton Design**:
  Each shared dataclass instance uses a single shared memory region, ensuring consistent and synchronized access.

---

## Installation

Install the library using pip:

```bash
pip install data-anchor
