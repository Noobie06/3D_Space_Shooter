# 🚀 Space Shooter – 3D Bullet Frenzy

A fully featured 3D space combat game built with Python, OpenGL, and GLUT.  
Fight enemy UFOs, survive a giant boss, explore procedurally placed planets, and master advanced weapons with dynamic heat and homing missiles.

---

## ✨ Features

### Core Gameplay
- **3D Open‑World Space** – Seamless starfield that wraps around the player for an infinite feel.
- **Dual Camera System** – Switch between first‑person cockpit view and third‑person orbit camera.
- **8 Unique Planets** – Procedurally generated planets with rings, moons, surface details, and atmospheric glows.
- **Enemy AI** – 8 UFOs that predict your movement, chase you, and pulse in size.
- **Epic Boss Fight** – Massive multi‑phase boss with adaptive difficulty, dynamic health bar, and unique attack patterns.
- **Space Storm Mode** – Turbulent environmental hazard with fog, colour shift, and camera shake.

### Advanced Weapons
- **Weapon Heat System** – Firing builds heat; overheat jams the gun. Boss fights automatically adjust heat generation (70% less) and cooling rate (3× faster).
- **Homing Missiles** – Launch a volley of 3 missiles that lock onto the nearest enemies. Missiles intelligently retarget if their original target is destroyed.
- **Screen Shake & Hit Feedback** – Damage intensity determines shake duration and strength. Boss flashes white when hit.

### Movement & Boost
- **Strategic Boost** – Hold `SHIFT` + movement for 3× speed. Boost has a regeneration delay, shown in a colour‑coded HUD bar.

### AI & Automation
- **Cheat / Auto‑Pilot Mode** – The ship automatically aims, fires, dodges, and positions itself. Extra lives and faster fire rate against bosses.
- **Adaptive Boss AI** – Boss shoots slower when auto‑pilot is active, keeping the fight fair.

### Environment
- **Procedural Planets** – 8 planets with different sizes, colours, rings, moons, and surface features (craters, gas bands).
- **Planet Collision Physics** – Hitting a planet damages you and pushes the ship away with realistic vector recoil.

---

## 🎮 Controls

| Key / Mouse          | Action                            |
|----------------------|-----------------------------------|
| `W` `A` `S` `D`     | Move forward / left / back / right|
| `Q` `E`              | Move up / down                    |
| `SHIFT` + movement   | Boost (3× speed, consumes boost)  |
| `Left Click`         | Fire plasma bullets               |
| `Right Click`        | Toggle first‑person / orbit camera|
| `X`                  | Launch homing missiles            |
| `C`                  | Toggle cheat / auto‑pilot mode    |
| `V`                  | Toggle cheat vision (while in cheat)|
| `M`                  | Toggle space storm                |
| `P`                  | Pause / unpause                   |
| `R`                  | Restart game                      |

---

## 📦 Installation & Running

### Requirements
- Python 3.7+
- PyOpenGL
- PyOpenGL‑accelerate (optional, for better performance)
- freeglut (or another GLUT implementation)

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/space-shooter.git
   cd space-shooter
