# Dynamic Multi-Party One-Time Pad Protocol

This repository implements **dynamic pad reallocation algorithms** for Multi-Party One-Time Pad (OTP) protocols. The system is designed to secure communication in asynchronous networks while **satisfying perfect secrecy**.

The core research addresses the distributed resource problem where multiple parties must consume shared cryptographic material (pads) from a finite sequence ($N$) without collisions, adapting to non-deterministic execution orders.

## 1. Algorithm Overview

In standard OTP usage, synchronization is trivial between two parties. However, in a multi-party setting (3+ nodes) where execution order is asynchronous, managing pad consumption becomes a complex distributed resource problem.

This implementation proves that perfect secrecy can be maintained through **adaptive resource reallocation**:

1.  **Dynamic Boundaries:** Parties track "Virtual Boundaries" to detect potential collisions before they occur.
2.  **State Reallocation:** If a party's required pad space is threatened by a neighbor, the algorithm shifts consumption ranges to available "whitespace" in the pad array.
3.  **Asynchronous Resilience:** The protocol guarantees correctness regardless of the message delivery order (up to a delay parameter $d$).

### 1.1 Mechanics (3-Party Topology)

The current version implements a **3-Party Linear Topology** (A - C - B) over a shared pad space of size $N$.

* **Pad Space ($N$):** A finite sequence of random pads indexed $1 \dots N$.
* **A (Left Node):** Consumes statically from the start ($1 \to N$).
* **B (Right Node):** Consumes statically from the end ($N \to 1$).
* **C (Middle Node):** Dynamically consumes from the center ($N/2$), expanding outwards.

### 1.2 Dynamic Reallocation Logic

The algorithm employs a **Passive Safety Boundary** strategy. 

* **Virtual Boundaries:** The protocol maintains `left_boundary` and `right_boundary` indices for the Middle Party (C).
* **Collision Detection:** As A and B consume inwards, the algorithm calculates the "gap" remaining between the static parties and the dynamic middle party.
* **The Shift:** If A's consumption approaches C's left boundary (within a threshold defined by delay $d$), C's state is effectively "frozen" on that side and reallocated to the largest available gap in the array. This allows C to "jump" over utilized sections or retreat into free space, ensuring $A \cap C = \emptyset$ and $B \cap C = \emptyset$ at all times.

### 1.3 Asynchrony & Constraints

The system is modeled to withstand network non-determinism:

* **Time ($t$):** Execution is divided into discrete time units (batches).
* **Shuffle (Network Latency):** Within a single time unit $t$, the order of execution is randomized. The protocol does not know if A, B, or C will attempt to send a message next.
* **Blocking Condition:** If a party requires a pad that has already been consumed, or if the Middle Party cannot find a contiguous free space $ > d$ to reallocate into, the protocol identifies a deadlock/exhaustion state and halts to preserve perfect secrecy.

---

## 2. Simulation & Visualizer

A web-based visualizer is included to empirically test the algorithm's efficiency, collision thresholds, and behavior under heavy load.

### 2.1 Running the Simulation

The simulation uses a Python backend for the algorithmic logic and a JavaScript frontend for visualization.

**Prerequisites:** Python 3.x

1.  **Start the API Server:**
    ```bash
    python server.py
    ```
2.  **Access the Interface:**
    Open your web browser and navigate to:
    `http://localhost:8000`

### 2.2 Simulation Parameters

* **$N$ (Pad Size):** The total amount of cryptographic material available.
* **$d$ (Delay):** The delay parameter. This simulates the maximum number of undelivered messages in the network. The algorithm requires a buffer of size $d$ to guarantee secrecy.
* **Randomization:** You can toggle "Randomize" to shuffle the execution order within a specific time batch, testing the algorithm's asynchronous resilience.

---

## 3. Project Structure

* `protocol.py`: **The Core.** Contains the `ThreePartyProtocol` class, state management, boundary logic, and reallocation algorithms.
* `server.py`: A lightweight HTTP API bridging the UI and the Python protocol logic.
* `index.html`: The client-side visualizer.
* `testing.py`: A headless CLI tool for running automated batches and stress tests.