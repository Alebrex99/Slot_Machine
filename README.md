# 🎰 Slot Machine — PyQt5 Desktop Game

**A modern, animated slot machine game built with PyQt5, Pygame, and modular Python architecture.**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg">
  <img src="https://img.shields.io/badge/Framework-PyQt5-41cd52.svg">
  <img src="https://img.shields.io/badge/Audio-Pygame.mixer-ffcc00.svg">
  <img src="https://img.shields.io/badge/License-MIT-green.svg">
  <img src="https://img.shields.io/badge/Status-Active-success.svg">
</p>

---

## ⭐ Overview

This project is a **high-quality, responsive desktop slot machine** featuring:

* 🎞 Smooth reel animation
* 🔊 Background music + sound effects
* 🪙 Reward and coin logic
* 🔐 One-time redeem code system with persistence
* ⚙️ Clean and scalable architecture
* 🗂 Organized assets structure
* 🪟 Fully interactive GUI built using **PyQt5**

Designed for readability, future expansion, and maintainability — ideal for learning, portfolio use, or extending into a full game.

---

## ✨ Features

### 🎮 Gameplay

* Randomized slot reels
* Reward system based on matching symbols
* Configurable spin cost
* Win animations + sound effects

### 🔊 Audio System

* Looping background music
* Triggered dynamic sound effects
* Non-blocking playback (async-friendly)

### 🔐 Redeem System

* Static `redeem_codes.json`
* Persistent `used_codes.json`
* Each code can be redeemed **once only**
* Automatically saved between sessions

### 🏗 Project Structure

* Clean separation of core logic and GUI
* Extensible modules for future features
* Fully modular OOP architecture

---

## 🧩 Project Architecture

```
project/
│
├── main.py
│
├── core/
│   ├── slot_logic.py       # reward + spin logic
│   ├── sound_manager.py    # BGM + SFX manager
│   └── redeem_logic.py     # redeem system + persistence
│
├── gui/
│   ├── main_window.py       # UI layout + integration
│   └── redeem_dialog.py      # redeem popup window
│
├── utils/
│   └── file_manager.py      # safe JSON load/save
│
├── gui/assets/
│   ├── icons/               # slot symbols + UI icons
│   ├── sounds/              # SFX
│   └── bgm/                 # background music
│
└── data/
    ├── redeem_codes.json    # constant list of valid codes
    └── used_codes.json      # persistent list of used codes
```

---

## 🖥 Preview

![Screenshot1](screenshots/Screenshot1.png)
![Screenshot2](screenshots/Screenshot2.png)
![Screenshot3](screenshots/Screenshot3.png)
![Screenshot4](screenshots/Screenshot4.png)

```
🎞 Animated reels
🔊 Sound effects
⚙️ Clean GUI layout
```

---

## 📦 Installation & Setup

### **1. Clone the repository**

```bash
git clone https://github.com/fadil-nurmaulid/Slot_Machine.git
cd Slot_Machine
```

### **2. Create a virtual environment (recommended)**

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### **3. Install dependencies**

```bash
pip install -r requirements.txt
```

### **4. Run the game**

```bash
python main.py
```

---

## 🔧 Configuration

All editable values (symbol list, reward table, coin cost, etc.) are located in:

```
core/slot_logic.py
```

Sound files are stored in:

```
gui/assets/sounds/
gui/assets/bgm/
```

Redeem codes live in:

```
data/redeem_codes.json
```

Used code persistence:

```
data/used_codes.json
```

---

## 🧠 Technical Highlights

* **QTimer-based animation** for smooth reel spin
* **Randomized symbol generation** using Python’s `random.choices`
* **Optimized reward table lookup**
* **Asynchronous audio playback** via Pygame mixer
* **Clean file I/O handling** with error-safe JSON helpers
* **Strict modularity** between UI and game logic

---

## 📜 License

This project is licensed under the **MIT License** — freely usable and modifiable.

---

## 👤 Author

**Fadil Nurmaulid**

Physics Student • Average Human • Aspiring AI Engineer 

> *Built with modularity, clarity, and expandability in mind.*

