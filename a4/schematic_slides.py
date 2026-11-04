# Draws the A4 schematic in the hand-drawn style of the HCDE 439 lecture slides
import sys, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Circle, Polygon, FancyBboxPatch

fm.fontManager.addfont(sys.argv[1])
plt.xkcd(scale=0.7, length=120, randomness=2)
plt.rcParams['font.family'] = ['Patrick Hand', 'DejaVu Sans']
plt.rcParams['path.effects'] = []

INK, BLUE, RED = '#111', '#1f5fd6', '#d62f2f'
fig, ax = plt.subplots(figsize=(13, 8)); ax.set_aspect('equal'); ax.axis('off')
fig.patch.set_facecolor('white')
def L(*p, c=INK, lw=2.4): ax.plot(*zip(*p), color=c, lw=lw, solid_capstyle='round')
def T(x, y, s, c=INK, fs=20, **k): ax.text(x, y, s, color=c, fontsize=fs, **k)

def supply(x, y, label='5V'):          # up-arrow power symbol like the slides
    L((x, y), (x, y + 0.9)); L((x - 0.25, y + 0.6), (x, y + 0.95), (x + 0.25, y + 0.6))
    T(x + 0.3, y + 0.75, label, fs=24)
def ground(x, y):                      # three-line ground symbol
    L((x, y), (x, y - 0.5))
    for i, w in enumerate((0.45, 0.3, 0.15)): L((x - w, y - 0.5 - i*0.18), (x + w, y - 0.5 - i*0.18))
def resistor(x, y0, y1):               # vertical zigzag from y0 down to y1
    n = 6; h = (y0 - y1) / n; pts = [(x, y0)]
    for i in range(n): pts.append((x + (0.3 if i % 2 == 0 else -0.3), y0 - h*(i + 0.5)))
    pts.append((x, y1)); L(*pts)
def pin(x, y, name):                   # blue Arduino pin label, like the slides' annotations
    ax.plot(x, y, 'o', color=BLUE, ms=9); T(x, y + 0.35, name, c=BLUE, fs=21, ha='center')

# ---------- IR receiver (input) ----------
x = 2.0
supply(x, 6.6)
L((x, 6.6), (x, 5.9))
ax.add_patch(FancyBboxPatch((x - 1.0, 3.6), 2.0, 2.3, boxstyle='round,pad=0.05', fill=False, lw=2.4, ec=INK))
ax.add_patch(Circle((x, 4.75), 0.5, fill=False, lw=2.4, ec=INK))
T(x, 4.55, 'IR', fs=20, ha='center')
T(x - 0.95, 6.05, 'VCC', fs=16); T(x - 0.95, 3.25, 'GND', fs=16)
L((x, 3.6), (x, 2.4)); ground(x, 2.4)
L((x + 1.0, 4.75), (x + 2.2, 4.75)); T(x + 1.1, 4.85, 'OUT', fs=16)
pin(x + 2.2, 4.75, 'Pin 11')
T(x - 1.2, 0.35, 'IR receiver\n(input)', fs=20)

# ---------- Servo (output) ----------
x = 8.8
supply(x, 6.6)
L((x, 6.6), (x, 5.5)); T(x + 0.15, 5.9, 'red', c=RED, fs=17)
ax.add_patch(Circle((x, 4.75), 0.75, fill=False, lw=2.4, ec=INK)); T(x, 4.5, 'M', fs=28, ha='center')
L((x, 4.0), (x, 2.4)); T(x + 0.15, 3.2, 'brown', c='#7a4a24', fs=17); ground(x, 2.4)
L((x - 0.75, 4.75), (x - 2.0, 4.75)); T(x - 2.45, 4.2, 'orange (signal)', c='#d9771b', fs=15)
pin(x - 2.0, 4.75, 'Pin 9')
T(x - 0.6, 0.35, 'Servo\n(output)', fs=20)

# ---------- LED with resistor ----------
x = 12.8
pin(x, 6.9, 'Pin 7')
L((x, 6.9), (x, 6.3)); resistor(x, 6.3, 4.9); T(x + 0.45, 5.45, 'R₁', fs=22)
L((x, 4.9), (x, 4.4))
ax.add_patch(Polygon([(x - 0.4, 4.4), (x + 0.4, 4.4), (x, 3.75)], closed=True, fill=False, lw=2.4, ec=INK))
L((x - 0.4, 3.75), (x + 0.4, 3.75))
for dy in (0, 0.35): ax.annotate('', xy=(x + 1.0, 3.75 + dy), xytext=(x + 0.5, 4.15 + dy), arrowprops=dict(arrowstyle='->', lw=2, color=INK))
L((x, 3.75), (x, 2.4)); ground(x, 2.4)
T(x - 0.65, 0.35, 'LED\n(feedback)', fs=20)

# ---------- handwritten notes, like the slide margins ----------
T(14.4, 6.3, 'R₁ = 220 Ω', fs=22)
T(14.4, 5.55, 'R min = (5V − 2V) / 20mA', fs=17)
T(14.4, 5.05, '        = 150 Ω  →  use 220 Ω', fs=17)
T(14.4, 4.45, 'I = 3V / 220 Ω ≈ 13.6 mA', fs=17)
T(14.4, 3.85, '(under the 20 mA limit)', fs=17)
T(9.3, -0.2, '5V and ground all come from the Arduino', c=BLUE, fs=17, ha='center')

ax.set_xlim(0.3, 19.6); ax.set_ylim(-0.5, 8.0)
plt.savefig(sys.argv[2], dpi=150, facecolor='white', bbox_inches='tight')
