# Draws the full A4 circuit as one connected schematic, in the hand-drawn style of the HCDE 439 slides
import sys, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
from matplotlib.patches import Circle, Polygon, FancyBboxPatch, Arc

fm.fontManager.addfont(sys.argv[1])
plt.xkcd(scale=0.7, length=120, randomness=2)
plt.rcParams['font.family'] = ['Patrick Hand', 'DejaVu Sans']
plt.rcParams['path.effects'] = []

INK, BLUE, RED, BROWN, ORANGE = '#111', '#1f5fd6', '#d62f2f', '#7a4a24', '#d9771b'
fig, ax = plt.subplots(figsize=(15, 8.5)); ax.set_aspect('equal'); ax.axis('off')
def L(*p, c=INK, lw=2.4): ax.plot(*zip(*p), color=c, lw=lw, solid_capstyle='round')
def T(x, y, s, c=INK, fs=19, **k): ax.text(x, y, s, color=c, fontsize=fs, **k)
def dot(x, y): ax.plot(x, y, 'o', color=INK, ms=9)
def hop(x, y, r=0.22):   # small bump where a wire crosses another without connecting
    a = np.linspace(np.pi, 0, 20); ax.plot(x + r*np.cos(a), y + r*np.sin(a), color=INK, lw=2.4)

TOP, BOT = 7.6, 0.9      # 5V rail and ground rail heights
RIGHT = 15.2

# ---------- Arduino ----------
ax.add_patch(FancyBboxPatch((-0.4, 1.4), 3.9, 5.8, boxstyle='round,pad=0.05', fill=False, lw=2.6, ec=INK))
T(0.75, 4.15, 'Arduino\nUno', fs=23, ha='center', va='center')
pins = {'5V': 6.7, 'Pin 11': 5.5, 'Pin 9': 4.2, 'Pin 7': 2.9, 'GND': 1.7}
for n, y in pins.items():
    T(3.35, y + 0.12, n, c=BLUE, fs=18, ha='right')

# ---------- rails ----------
L((3.5, 6.7), (4.2, 6.7), (4.2, TOP), (RIGHT, TOP), c=RED)
T(5.0, TOP + 0.2, '5V', c=RED, fs=24)
L((3.5, 1.7), (4.2, 1.7), (4.2, BOT), (RIGHT, BOT))
gx = 9.4; L((gx, BOT), (gx, BOT - 0.4))
for i, w in enumerate((0.45, 0.3, 0.15)): L((gx - w, BOT - 0.4 - i*0.18), (gx + w, BOT - 0.4 - i*0.18))
T(gx + 0.6, BOT - 0.7, 'GND', fs=20)

# ---------- LED branch (Pin 7) ----------
x = 5.8
L((3.5, 2.9), (x, 2.9), (x, 2.75))
n = 6; y0, y1 = 2.75, 1.95; h = (y0 - y1) / n; pts = [(x, y0)]
for i in range(n): pts.append((x + (0.25 if i % 2 == 0 else -0.25), y0 - h*(i + 0.5)))
pts.append((x, y1)); L(*pts); T(x + 0.4, 2.2, 'R₁ 220 Ω', fs=17)
ax.add_patch(Polygon([(x - 0.3, 1.95), (x + 0.3, 1.95), (x, 1.45)], closed=True, fill=False, lw=2.4, ec=INK))
L((x - 0.3, 1.45), (x + 0.3, 1.45))
for dy in (0, 0.28): ax.annotate('', xy=(x - 0.95, 1.4 + dy), xytext=(x - 0.45, 1.7 + dy), arrowprops=dict(arrowstyle='->', lw=2, color=INK))
L((x, 1.45), (x, BOT)); dot(x, BOT)
T(x + 0.4, 1.45, 'LED', fs=17)

# ---------- Servo branch (Pin 9) ----------
x = 9.4
L((3.5, 4.2), (x - 0.75, 4.2), c=ORANGE); T(4.9, 3.72, 'signal (orange)', c=ORANGE, fs=16)
ax.add_patch(Circle((x, 4.2), 0.75, fill=False, lw=2.4, ec=INK)); T(x, 3.95, 'M', fs=28, ha='center')
T(x + 0.95, 4.05, 'Servo', fs=21)
L((x, 4.95), (x, TOP), c=RED); dot(x, TOP); T(x + 0.15, 6.4, 'red', c=RED, fs=16)
L((x, 3.45), (x, BOT), c=BROWN); dot(x, BOT); T(x + 0.15, 2.3, 'brown', c=BROWN, fs=16)

# ---------- IR receiver branch (Pin 11) ----------
x = 13.0
L((3.5, 5.5), (x - 0.22 - 3.6, 5.5)); hop(x - 3.6, 5.5); L((x - 3.6 + 0.22, 5.5), (x - 1.0, 5.5))
T(6.6, 5.65, 'OUT (signal)', fs=16)
ax.add_patch(FancyBboxPatch((x - 1.0, 4.5), 2.0, 2.0, boxstyle='round,pad=0.05', fill=False, lw=2.4, ec=INK))
ax.add_patch(Circle((x, 5.5), 0.45, fill=False, lw=2.4, ec=INK)); T(x, 5.32, 'IR', fs=18, ha='center')
T(x - 0.2, 6.75, 'IR receiver', fs=19, ha='right')
L((x, 6.55), (x, TOP)); dot(x, TOP); T(x + 0.15, 6.85, 'VCC', fs=15)
L((x, 4.45), (x, BOT)); dot(x, BOT); T(x + 0.15, 3.9, 'GND', fs=15)

# ---------- notes in the margin, like the slides ----------
nx = 16.0
T(nx, 6.9, 'Input: IR receiver → Pin 11', fs=17)
T(nx, 6.35, 'Output: servo ← Pin 9', fs=17)
T(nx, 5.8, 'Feedback: LED ← Pin 7', fs=17)
T(nx, 4.8, 'R₁ = 220 Ω', fs=22)
T(nx, 4.2, 'R min = (5V − 2V) / 20mA', fs=16)
T(nx, 3.75, '        = 150 Ω → use 220 Ω', fs=16)
T(nx, 3.2, 'I = 3V / 220 Ω ≈ 13.6 mA', fs=16)
T(nx, 2.75, '(under the 20 mA limit)', fs=16)

ax.set_xlim(-0.7, 21.4); ax.set_ylim(-0.3, 8.4)
plt.savefig(sys.argv[2], dpi=150, facecolor='white', bbox_inches='tight')
