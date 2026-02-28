---
title: Ethernet Standards
image: bash
tags:
- Computer Networking
- IT Fundamentals
- CompTIA
- Network Plus
- OSI Model
- Cable Standards
---

Here's a breakdown of each of those Ethernet standards, what they are, and how they correlate to **media type**, **speed**, and **cable requirements**:

---

### ✅ **1. 1000BASE-T**
- **Speed**: 1 Gbps (Gigabit Ethernet)
- **Media Type**: Twisted-pair copper (Cat 5e or better)
- **Max Distance**: 100 meters
- **Connectors**: RJ-45
- **Common Use**: Most widely used Gigabit Ethernet standard in homes and offices  
- **OSI Layer**: Layer 1 (Physical)

---

### ✅ **2. 1000BASE-TX** *(Less common)*
- **Speed**: 1 Gbps
- **Media Type**: Twisted-pair copper (Cat 6)
- **Max Distance**: 100 meters
- **Connectors**: RJ-45
- **Difference from 1000BASE-T**: Uses **2 pairs** of wires instead of 4; was designed to reduce complexity but lost popularity due to higher cost and lack of compatibility  
- **Status**: Rarely used; considered obsolete in most environments

---

### ✅ **3. 1000BASE-FX** *(Actually a mix-up — likely meant to be 1000BASE-LX or SX)*
- **Speed**: 1 Gbps
- **Media Type**: **Fiber optic cable**
  - *1000BASE-SX* for **short-range (multimode fiber)**  
  - *1000BASE-LX* for **long-range (single-mode fiber)**
- **Max Distance**:
  - SX: ~550 meters  
  - LX: ~5–10 km
- **Use Case**: Data centers, inter-building links, or environments requiring high EMI resistance

---

### ✅ **4. 100BASE-TX**
- **Speed**: 100 Mbps (Fast Ethernet)
- **Media Type**: Twisted-pair copper (Cat 5 or better)
- **Max Distance**: 100 meters
- **Connectors**: RJ-45
- **Use Case**: Older networks (still found in legacy systems or very basic setups)

---

### 🔁 Quick Comparison Table

| Standard       | Speed    | Medium        | Max Distance | Cable Type   | Common Use        |
|----------------|----------|---------------|---------------|--------------|-------------------|
| 100BASE-TX     | 100 Mbps | Copper (UTP)  | 100m          | Cat 5        | Legacy networks   |
| 1000BASE-T     | 1 Gbps   | Copper (UTP)  | 100m          | Cat 5e+      | Modern LANs       |
| 1000BASE-TX    | 1 Gbps   | Copper (UTP)  | 100m          | Cat 6        | Rarely used       |
| 1000BASE-FX    | 1 Gbps   | **Fiber**     | 550m–10km     | MMF/SMF      | Inter-building / datacenter |

---

### ✅ **OSI Layer Correspondence**

All of the following standards — **1000BASE-T, 1000BASE-TX, 1000BASE-FX, and 100BASE-TX** — operate at:

> **📍 OSI Layer 1: The Physical Layer**

#### Why Layer 1?
Because these standards define:
- **Electrical signaling**
- **Media type (copper/fiber)**
- **Connector types**
- **Cable lengths**
- **Bit transmission mechanics**

They don’t handle addressing (Layer 2) or routing (Layer 3), just the actual movement of bits over physical media.

---

### ✅ **Networking Categories**

These Ethernet standards fall under the category of:

> **📂 Wired LAN Technologies (Local Area Network)**  
And more specifically:

| Standard        | Category                | Notes |
|-----------------|-------------------------|-------|
| **100BASE-TX**   | Fast Ethernet            | 100 Mbps copper |
| **1000BASE-T**   | Gigabit Ethernet         | Most common 1 Gbps standard for LAN |
| **1000BASE-TX**  | Gigabit Ethernet (Legacy)| Rare, proprietary |
| **1000BASE-FX**  | Gigabit Ethernet over Fiber | Not officially "FX", but refers to SX/LX fiber types |

---

### 🧠 Summary Cheat Sheet:

| Standard        | OSI Layer | Network Type        | Media         |
|-----------------|------------|----------------------|----------------|
| 100BASE-TX      | Layer 1    | Fast Ethernet (LAN)  | Cat 5 (Copper) |
| 1000BASE-T      | Layer 1    | Gigabit Ethernet      | Cat 5e+ (Copper) |
| 1000BASE-TX     | Layer 1    | Gigabit Ethernet (Legacy) | Cat 6 (Copper) |
| 1000BASE-FX     | Layer 1    | Gigabit Ethernet (Fiber) | MMF/SMF (Fiber) |

---
