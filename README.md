# 🌊 Water Tank Card Game API

A robust, object-oriented backend microservice built with **Python** and **FastAPI**, turning a traditional procedural card game into a fully RESTful API with secure state management and an automated AI opponent.

## 🚀 Features & Architecture

* **Object-Oriented Design (`game_models.py`):** 
  * Utilizes **Abstract Base Classes (`ABC`)** and **Polymorphism** for extensible card hierarchies (`WaterCard` and `PowerCard`).
  * Implements Python **`@dataclass`** models with strict data validation (`__post_init__`) to prevent malformed game states.
  * Encapsulates pile management, shuffling, and recycling rules inside a dedicated `Deck` class.
* **FastAPI Backend (`main.py`):**
  * Manages multi-session state isolation using UUIDs and in-memory session tracking.
  * Provides automated turn resolution: executing player moves, managing deck draws, and triggering the computer's AI response in a single transaction.
* **Security & Information Hiding:**
  * Features secure state serialization that masks computer-controlled opponent cards to prevent client-side data leakage/cheating via API inspection.
* **Deterministic AI Strategy:**
  * Built-in AI that evaluates immediate winning conditions (`75 <= tank <= 80`) or calculates optimal utility deltas to maximize tactical advantage.

---

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Framework:** FastAPI
* **Server:** Uvicorn
* **Version Control:** Git / GitHub

---

## ⚙️ Getting Started Locally

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR-USERNAME/water-tank-backend-api.git](https://github.com/YOUR-USERNAME/water-tank-backend-api.git)
cd water-tank-backend-api