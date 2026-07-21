<div align="center">

# VELA

### *Autonomous AI Museum Guide & Robotic Companion*

<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Raspberry%20Pi-4-A22846?style=for-the-badge&logo=raspberrypi&logoColor=white"/>
<img src="https://img.shields.io/badge/Ollama-Local%20LLM-000000?style=for-the-badge"/>
<img src="https://img.shields.io/badge/FastAPI-Edge%20AI-009688?style=for-the-badge&logo=fastapi"/>
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>

<br>

> **An intelligent robotic companion that sees, listens, navigates, and speaks—powered entirely by local AI.**

---

*"Building the future of human-robot interaction, one exhibit at a time."*

</div>

<br>

## Overview

VELA is an experimental edge-AI robotics platform designed for museums and interactive public spaces.

Unlike traditional museum guides, VELA understands **where it is**, **who is nearby**, and **what it should say**.

By combining:

* Computer Vision
* Context-Aware Navigation
* Embedded Systems
* Distributed Edge Computing
* Local Large Language Models
* Human-Robot Interaction

VELA transforms static exhibits into immersive conversations.

<br>

---

## Why VELA?

Imagine entering a museum and being greeted by a robot that says:

> *"Welcome to the Modern Art Gallery. Would you like to learn about the evolution of abstract expressionism?"*

VELA makes this possible by continuously answering three questions:

| Question               | Answered By              |
| ---------------------- | ------------------------ |
| **Where am I?**        | Context Manager          |
| **Is someone nearby?** | Computer Vision Pipeline |
| **What should I say?** | Local LLM (Ollama)       |

No cloud.

No subscriptions.

No external APIs.

Just robotics, running locally.

---

## Features

### Local Intelligence

* Ollama-powered LLM inference.
* FastAPI bridge architecture.
* Supports:

  * `Llama 3`
  * `Phi-3`
* Fully offline operation.

---

### Spatial Awareness

VELA maintains a live understanding of its environment:

```text
Current Room:
└── entrada

Destination:
└── arte_contemporaneo

Computed Route:
└── entrada → arte_contemporaneo
```

Every room changes the robot's behavior and system prompt automatically.

---

### Visitor Presence Detection

Using OpenCV + MediaPipe, VELA classifies visitors in real time:

| State     | Behavior             |
| --------- | -------------------- |
| `CERCA`   | Starts conversation  |
| `LEJOS`   | Waits attentively    |
| `AUSENTE` | Returns to idle mode |

---

### Concurrent Event Engine

Critical actions always win.

```python
Priority Order

1. stop
2. ayuda
3. voz
4. persona_detectada
```

This thread-safe queue guarantees that safety commands immediately override background processes.

---

### Embedded Hardware Stack

```text
• Raspberry Pi 4
• USB Camera
• USB Microphone
• Dual DC Motors
• L298N Driver
• 16x2 I2C LCD
• Speaker System
```

<br>

---

## Architecture

```text
                     ┌───────────────────────┐
                     │   AI WORKSTATION      │
                     │                       │
                     │   FastAPI + Ollama    │
                     │                       │
                     │  Llama 3 / Phi-3      │
                     └──────────┬────────────┘
                                │
                           HTTP/REST
                                │
                                ▼
┌──────────────────────────────────────────────────────────┐
│                   RASPBERRY PI NODE                      │
│                                                          │
│  Camera ─────► Vision Pipeline                           │
│  Microphone ─► Speech Recognition                        │
│  Sensors ────► Presence Detection                        │
│                            │                             │
│                            ▼                             │
│                  Thread Priority Queue                   │
│                            │                             │
│                            ▼                             │
│                     Context Manager                      │
│                            │                             │
│                            ▼                             │
│                        Navigator                         │
│                            │                             │
│                            ▼                             │
│               Motors • LCD • Speaker Output              │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

<br>

---

## Technology Stack

| Layer      | Technologies                    |
| ---------- | ------------------------------- |
| Runtime    | Python 3.11                     |
| AI         | Ollama, FastAPI, Pydantic       |
| Vision     | OpenCV, MediaPipe               |
| Speech     | gTTS, SpeechRecognition, Pygame |
| Hardware   | smbus2, I2C                     |
| Networking | REST APIs                       |
| Platform   | Raspberry Pi 4                  |

---

## Quick Start

### 1. Start the AI Node

```bash
git clone https://github.com/your-username/VELA.git

cd VELA/server

pip install fastapi uvicorn requests pydantic

python servidor_ollama.py
```

Make sure:

```bash
ollama serve
```

is running on the host machine.

---

### 2. Start the Robot

```bash
sudo apt update

sudo apt install -y \
i2c-tools \
python3-pip

sudo raspi-config nonint do_i2c 0

python main.py
```

---

## Supported Environments

| Location             | Capabilities                                |
| -------------------- | ------------------------------------------- |
| `entrada`            | Greetings, orientation, museum information  |
| `arte_contemporaneo` | Exhibit explanations and guided interaction |

---

## Roadmap

```text
[✓] Hardware Drivers
[✓] Computer Vision
[✓] Local LLM Integration
[✓] Context-Aware Navigation
[✓] Speech Synthesis

[ ] SLAM Navigation
[ ] Multi-Floor Support
[ ] Battery Monitoring
[ ] Autonomous Docking
[ ] Multi-Language Support
[ ] Mobile Dashboard
```

---

## Gallery

```text
Coming Soon

• Autonomous Navigation Demo
• Visitor Interaction Footage
• Full Museum Walkthrough
• Hardware Assembly Photos
```

---

## Philosophy

> VELA was built around a simple idea:
>
> **Intelligent robots should understand context, not just commands.**
>
> By combining local AI, spatial awareness, and embedded systems, VELA explores what the next generation of human-robot interaction might look like.

---

<div align="center">

### Built with Python, Raspberry Pi, and a lot of curiosity.

**If you enjoyed this project, consider giving it a ⭐**

</div>
