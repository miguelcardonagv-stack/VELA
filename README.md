VELA 🤖
Autonomous AI Museum Guide & Robotic Companion

An intelligent, vision-enabled robotic assistant powered by edge computing, spatial awareness, and local LLM intelligence.








✨ Overview

Traditional museum guides are static, scripted, and incapable of adapting to visitors.

VELA reimagines the museum experience by combining robotics, computer vision, and local conversational AI into a fully autonomous companion capable of:

Greeting visitors proactively.
Understanding its physical location.
Answering exhibit-specific questions.
Navigating between museum rooms.
Detecting visitor presence and distance.
Operating entirely on a local network without cloud APIs.

Built around a Raspberry Pi and an edge-based AI architecture, VELA demonstrates how modern robotics can deliver contextual and privacy-preserving interactions in public spaces.

🚀 Why VELA?

VELA isn't just another chatbot attached to wheels.

It combines several disciplines into a single system:

Autonomous robotics
Computer vision
Distributed edge computing
Context-aware AI
Concurrent programming
Embedded systems
Human–robot interaction

The result is a robotic guide capable of adapting its behavior according to:

Context	Behavior
Visitor nearby	Greets and starts interaction
Visitor absent	Returns to idle mode
In the entrance hall	Provides orientation
In the art gallery	Explains exhibits
Emergency stop	Overrides all tasks immediately
🌟 Key Features
Local LLM Architecture
FastAPI bridge server running on a workstation.
Ollama-powered inference (Llama 3, Phi-3).
Zero dependency on external AI services.
Low-latency responses over a local network.
Computer Vision & Presence Detection
MediaPipe facial landmark detection.
Visitor state classification:
CERCA
LEJOS
AUSENTE
Automatic transition between interaction states.
Concurrent Event System

Priority-based scheduling ensures mission-critical events are handled instantly:

stop > ayuda > voz > persona_detectada
State-Aware Navigation

A dynamic ContextManager maintains:

Current room.
Destination room.
Route planning.
Language model context.

Example:

entrada -> arte_contemporaneo
Hardware Integration
Dual differential drive motors.
I2C 16x2 LCD display.
USB camera.
USB microphone.
Speaker output.
gTTS + Pygame speech synthesis.
🏗 System Architecture
┌──────────────────────────────────────────────────────────────┐
│                    Raspberry Pi (Edge Node)                  │
│                                                              │
│ [ Camera ] -> Vision Node (MediaPipe) ----┐                  │
│ [ Mic ]    -> Voice Pipeline (STT) -------┼-> Priority Queue │
│ [ Sensors] -> Distance Detector ----------┘        │         │
│                                                    ▼         │
│ [ Motors ] <- Navigator <- ContextManager <- main.py         │
│ [ LCD ]    <- LCD Node                                        │
│ [ Speaker] <- gTTS / Pygame                                   │
└───────────────────────────────────────────────┬──────────────┘
                                                │ HTTP / REST
                                                ▼
                         ┌────────────────────────────────┐
                         │      AI Workstation Node       │
                         │                                │
                         │ FastAPI Server (Port 8000)     │
                         │                │               │
                         │                ▼               │
                         │   Ollama (Llama 3 / Phi-3)     │
                         └────────────────────────────────┘
🛠 Hardware
Component	Specification
SBC	Raspberry Pi 4 (4GB/8GB)
Motor Driver	L298N
Motors	Dual DC Differential Drive
Display	16x2 LCD (I2C)
Vision	USB Camera
Audio Input	USB Microphone
Audio Output	USB/3.5mm Speaker
💻 Software Stack
Category	Technologies
Runtime	Python 3.11
AI	Ollama, FastAPI, Pydantic
Vision	OpenCV, MediaPipe
Speech	gTTS, SpeechRecognition, Pygame
Hardware	smbus2
Networking	REST APIs
⚡ Quick Start
AI Server
git clone https://github.com/your-username/VELA.git

cd VELA/server

pip install fastapi uvicorn requests pydantic

python servidor_ollama.py

Ensure ollama serve is running on the host machine.

Raspberry Pi
sudo apt update
sudo apt install -y i2c-tools python3-pip

sudo raspi-config nonint do_i2c 0

python main.py
🗺 Supported Locations
Room ID	Display Name	Capabilities
entrada	Main Entrance	Orientation & Welcome
arte_contemporaneo	Modern Art Gallery	Exhibit Explanations
📈 Roadmap

Core hardware drivers

Computer vision integration

Context-aware navigation

Local LLM integration

SLAM-based navigation

Multi-floor support

Battery monitoring

Touchscreen interface

Multi-language support

Autonomous charging dock

🎥 Demo

Coming soon: Full demonstration video showing autonomous navigation, visitor interaction, and exhibit explanations.s, motor controller, and I2C LCD integration.[x] Phase 2: Multi-threaded Priority Queue and MediaPipe vision node integration.[x] Phase 3: Distributed FastAPI + Ollama server architecture.[ ] Phase 4: Autonomous SLAM navigation with LiDAR integration.[ ] Phase 5: Multi-language voice recognition and dynamic personality profiles.
