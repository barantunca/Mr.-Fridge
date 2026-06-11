<div align="center">

#  Mr. Fridge

**AI-powered smart fridge inventory manager & recipe generator**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Kivy](https://img.shields.io/badge/Kivy-2.x-brightgreen?style=for-the-badge&logo=kivy&logoColor=white)](https://kivy.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

*Point your camera at any food item — Mr. Fridge identifies it, logs it, and cooks up a recipe for you.*

</div>

---

##  Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Tech Stack](#-tech-stack)
- [Contributing](#-contributing)

---

##  Overview

**Mr. Fridge** is a cross-platform mobile application that helps you manage your refrigerator's contents using AI. Simply scan food items with your phone's camera, and GPT-4o Vision automatically identifies them. When you're wondering what to cook, Mr. Fridge generates a creative, step-by-step recipe based on what you have — streamed in real time.

The project follows a **client-server architecture**: a **FastAPI** async backend handles all AI communication and database persistence, while a **Kivy** mobile frontend provides the user interface.

---

##  Features

| Feature | Description |
|---|---|
|  **AI Camera Scan** | Capture a photo of any food item; GPT-4o Vision identifies it automatically |
|  **Smart Inventory** | Add, browse, and delete items; everything is persisted in a local SQLite database |
|  **Recipe Generation** | Select ingredients from your fridge, get a full recipe streamed token-by-token |
|  **Auto-Categorization** | Items are automatically grouped (Dairy, Fruit, Vegetable, Meat & Fish, etc.) |
|  **Manual Entry** | Add items manually when camera scanning isn't needed |
|  **API Key Management** | Set, update, and remove your OpenAI API key directly from the app settings |
|  **Fridge Dashboard** | See total item count, fill percentage, and urgency notifications at a glance |
|  **Streaming Responses** | Recipe text appears word-by-word via Server-Sent Events for a natural feel |

---

##  Architecture

```
┌─────────────────────────────────────────────────┐
│                  Mobile Client                  │
│              (Kivy — Python)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │   Home   │ │Inventory │ │    Recipe    │   │
│  │  Screen  │ │  Screen  │ │    Screen    │   │
│  └──────────┘ └──────────┘ └──────────────┘   │
│              api_client.py (HTTP)               │
└─────────────────────┬───────────────────────────┘
                      │  REST + SSE
                      ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Backend                    │
│  /camera   /inventory   /recipe   /settings    │
│                                                 │
│  VisionService   LLMService   InventoryService  │
└──────────┬─────────────────────────┬────────────┘
           │                         │
     OpenAI GPT-4o            SQLite (aiosqlite)
```

---

##  Project Structure

```
Mr.-Fridge/
├── backend/                   # FastAPI server
│   ├── api/
│   │   ├── routes_camera.py   # POST /camera/scan
│   │   ├── routes_inventory.py# CRUD /inventory/*
│   │   ├── routes_recipe.py   # POST /recipe/generate (SSE)
│   │   └── routes_settings.py # GET/POST/DELETE /settings/api-key
│   ├── core/
│   │   ├── api_key_store.py   # Centralized OpenAI key manager
│   │   ├── database.py        # SQLAlchemy async engine
│   │   └── exceptions.py      # Custom exception handlers
│   ├── models/
│   │   ├── fridge.py          # Fridge ORM model
│   │   └── item.py            # Item ORM model
│   ├── schemas/
│   │   └── api_schemas.py     # Pydantic request/response models
│   ├── services/
│   │   ├── inventory_service.py# Business logic + in-memory cache
│   │   ├── llm_service.py     # Recipe generation via GPT-4o
│   │   └── vision_service.py  # Image identification via GPT-4o Vision
│   ├── main.py                # FastAPI app entry point
│   └── requirements.txt
│
├── frontend/                  # Kivy mobile app
│   ├── ui/
│   │   ├── screens/
│   │   │   ├── home_screen.py
│   │   │   ├── inventory_screen.py
│   │   │   ├── recipe_screen.py
│   │   │   ├── profile_screen.py
│   │   │   └── scan_screen.py
│   │   ├── main_window.py     # ScreenManager + bottom nav + FAB
│   │   ├── theme.py           # Color palette & typography tokens
│   │   └── widgets.py         # Reusable styled components
│   ├── api_client.py          # All HTTP calls to the backend
│   ├── main.py                # Kivy app entry point
│   └── requirements.txt
│
├── buildozer.spec             # Android build configuration
└── README.md
```

---

##  Getting Started

### Prerequisites

- **Python 3.10+**
- **OpenAI API key** with access to `gpt-4o`
- *(Optional)* A webcam for live camera scanning on desktop

---

### Backend Setup

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your OpenAI API key
# Option A — create a .env file:
echo OPENAI_API_KEY=sk-your-key-here > .env

# Option B — set it via the app's Settings screen after launching

# 5. Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.  
Interactive docs: `http://127.0.0.1:8000/docs`

---

### Frontend Setup

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Install OpenCV for live camera scanning
pip install opencv-python

# 5. Run the Kivy app
python main.py
```

> **Android:** The `buildozer.spec` is pre-configured. Run `buildozer android debug` from the project root on a Linux/macOS machine with Buildozer installed.

---

##  Usage

1. **Start the backend** server (`uvicorn main:app --reload`).
2. **Launch the frontend** (`python main.py`).
3. **Add items** using the central **+** FAB button:
   - ** Take Photo** — point the camera at a food item and tap *Start Scan*.
   - ** Manual Entry** — type the item name and category.
4. **Browse inventory** in the **Inventory** tab.
5. **Generate a recipe** in the **Recipes** tab — check the ingredients you want to use and tap *Generate with OpenAI*.
6. **Manage your API key** in the **Profile** tab → *Account Settings*.

---

##  API Documentation

Full API reference is available in **[API.md](API.md)**.

A live Swagger UI is served at `http://127.0.0.1:8000/docs` when the backend is running.

Quick endpoint summary:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/camera/scan` | Identify a food item from a base64 image |
| `POST` | `/inventory/add` | Add an item to the fridge inventory |
| `GET` | `/inventory/{fridge_id}/items` | List all items for a fridge |
| `GET` | `/inventory/{fridge_id}/categorized` | Get categorized inventory |
| `DELETE` | `/inventory/delete/{item_id}` | Remove an item by ID |
| `POST` | `/recipe/generate` | Stream a recipe based on selected ingredients |
| `GET` | `/settings/api-key` | Get current API key status |
| `POST` | `/settings/api-key` | Set a new OpenAI API key |
| `DELETE` | `/settings/api-key` | Remove the stored API key |

---

##  Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com) | Async REST API framework |
| [SQLAlchemy 2.0](https://docs.sqlalchemy.org) | Async ORM |
| [aiosqlite](https://github.com/omnilib/aiosqlite) | Async SQLite driver |
| [Pydantic v2](https://docs.pydantic.dev) | Data validation & serialization |
| [OpenAI Python SDK](https://github.com/openai/openai-python) | GPT-4o Vision & text generation |
| [Pillow](https://python-pillow.org) | Image compression before API calls |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Environment variable management |

### Frontend
| Technology | Purpose |
|---|---|
| [Kivy](https://kivy.org) | Cross-platform mobile UI framework |
| [OpenCV](https://opencv.org) | Live camera capture (desktop) |
| [requests](https://requests.readthedocs.io) | HTTP client for backend calls |
| [Pillow](https://python-pillow.org) | Frame-to-JPEG conversion |

---

##  Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

<div align="center">

Made with ❄️ by the Mr. Fridge team

</div>
