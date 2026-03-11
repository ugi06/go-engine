Go-Engine
A high-performance strategy analysis engine for the game of Go, utilizing vectoral ray-casting to calculate and visualize stone influence.

🚀 Key Features
Vectoral Analysis: Real-time calculation of influence zones via ray-casting.

Group Capture Logic: Dynamic liberty and capture system consistent with official Go rules.

Multiple Modes: Supports BARRIER (Orthogonal), DIAGONAL, and SUPER_RAY (Hybrid) analysis.

Strategic Tools: Intersection detection (Red Points), Undo/Redo functionality, and PNG export.

🛠️ Installation
Ensure you have Python and Pygame installed on your system:

Bash
pip install pygame
python main.py
📖 How to Use
Click: Place a stone (Turn-based logic is automatic).

Undo / Redo: Navigate through the move history.

Toggle Mode: Switch the geometry of the ray propagation.

Save: Export the current analysis frame as a PNG image.

⚖️ License
MIT License.