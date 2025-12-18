# Virtual Memory Simulator (Python)

## Overview
This project is a Python-based **Virtual Memory Simulator** that models paging, address translation, and demand paging as implemented in modern operating systems.

The simulator supports:
- Virtual-to-physical page translation
- Demand paging with page fault handling
- Page replacement algorithms (FIFO, LRU)
- Translation Lookaside Buffer (TLB) with hit/miss tracking
- Read and write memory accesses with dirty bit management
- Execution using realistic memory access traces from text files

---

## Features
- **Logical to Physical Address Translation**
  - Translates logical addresses to physical addresses using page size.
  - Displays the translation mapping.

- **Demand Paging**  
  Pages are loaded into physical memory only when accessed.

- **Page Replacement Algorithms**
  - FIFO (First-In First-Out)
  - LRU (Least Recently Used)
  - Optimal (Replace page that will not be used for longest time)

- **Translation Lookaside Buffer (TLB)**
  - Caches recent page-to-frame translations
  - Tracks TLB hits and misses
  - Uses LRU replacement internally

- **Read / Write Operations**
  - Write operations mark pages as dirty
  - Dirty pages are detected on eviction

- **Trace-Driven Simulation**
  - Reads memory access traces from `.txt` files
  - Supports formats like:
    ```
    R 49156
    W 49160
    ```
  - Input addresses are treated as **Logical Addresses** and translated to Page Numbers and Physical Addresses.

---

## System Components

### 1. TLB (Translation Lookaside Buffer)
- Small cache that stores `(page → frame)` mappings
- Reduces access time by avoiding frequent page table lookups
- Uses LRU replacement policy

### 2. Page Table
- Stores metadata for each page:
  - Frame number
  - Dirty bit
- Acts as the authoritative source of memory mappings

### 3. Physical Memory (Frames)
- Fixed number of frames
- Stores currently loaded pages

### 4. Page Replacement Algorithms
- **FIFO**: Evicts the oldest loaded page
- **LRU**: Evicts the least recently used page
- **Optimal**: Evicts the page that will not be used for the longest period of time

### 5. Virtual Memory Manager
- Coordinates TLB, page table, frames, and replacement algorithms
- Handles page faults and memory accesses
- Collects simulation statistics

---

## Input Format (Trace File)

Each line represents one memory access:
