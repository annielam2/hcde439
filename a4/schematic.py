# Draws the A4 schematic: IR receiver -> Arduino -> servo + feedback LED
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
fig, ax = plt.subplots(figsize=(12, 7)); ax.set_aspect('equal'); ax.axis('off')
K = dict(color='black', lw=2)
def line(*pts, **kw): xs, ys = zip(*pts); ax.plot(xs, ys, **{**K, **kw})
def dot(x, y): ax.plot(x, y, 'ko', ms=7)
def box(x0, y0, w, h, title):
    ax.add_patch(Rectangle((x0, y0), w, h, fill=False, lw=2)); ax.text(x0+w/2, y0+h/2, title, ha='center', va='center', fontsize=12, weight='bold')
def t(x, y, s, **kw): ax.text(x, y, s, **{'fontsize': 10.5, **kw})

# Rails
line((0.3, 9), (16.2, 9), color='#c0392b'); t(0.3, 9.25, '+5 V rail (from Arduino 5V)', color='#c0392b', weight='bold')
line((0.3, 0), (16.2, 0)); t(0.3, -0.5, 'GND rail (from Arduino GND)', weight='bold')

# Arduino
box(6, 2.5, 4, 5, 'Arduino Uno\n(Elegoo R3)')
line((8, 7.5), (8, 9)); dot(8, 9); t(8.15, 7.7, '5V')
line((8, 2.5), (8, 0)); dot(8, 0); t(8.15, 2.15, 'GND')
t(6.1, 4.85, 'D11'); t(9.25, 6.35, 'D9'); t(9.3, 3.85, 'D7')

# IR receiver (VS1838B module): VCC top, GND bottom, OUT right
box(1, 3.5, 2.6, 3, 'IR receiver\nVS1838B')
line((2.3, 6.5), (2.3, 9)); dot(2.3, 9); t(2.45, 6.7, 'VCC (R)')
line((2.3, 3.5), (2.3, 0)); dot(2.3, 0); t(2.45, 3.1, 'GND (G)')
line((3.6, 5), (6, 5)); t(3.7, 5.15, 'OUT (Y) → D11'); t(3.9, 4.55, 'IR signal', color='#555', style='italic')

# Servo SG90: signal left, +5V top, GND bottom
box(12.6, 5.4, 3, 2.4, 'Servo\nSG90')
line((10, 6.5), (12.6, 6.5), color='#e67e22'); t(10.15, 6.65, 'D9 → signal (orange)'); t(10.3, 6.0, '50 Hz pulses', color='#555', style='italic')
line((14.6, 7.8), (14.6, 9), color='#c0392b'); dot(14.6, 9); t(14.75, 8.2, '+5V (red)')
line((15.2, 5.4), (15.2, 0), color='#6e3b1f'); dot(15.2, 0); t(15.35, 2.6, 'GND\n(brown)')

# D7 -> R1 220 ohm -> LED -> GND
line((10, 4), (10.6, 4))
zx = [10.6 + i*0.2 for i in range(8)]; zy = [4] + [4 + (0.25 if i % 2 else -0.25) for i in range(1, 7)] + [4]
line(*zip(zx, zy)); line((12.0, 4), (12.8, 4)); t(10.65, 4.4, 'R1  220 Ω')
line((12.8, 4), (12.8, 3.1))
ax.add_patch(Polygon([(12.45, 3.1), (13.15, 3.1), (12.8, 2.5)], closed=True, fill=False, lw=2)); line((12.45, 2.5), (13.15, 2.5))
ax.annotate('', xy=(13.75, 2.35), xytext=(13.25, 2.85), arrowprops=dict(arrowstyle='->', lw=1.5))
ax.annotate('', xy=(13.95, 2.7), xytext=(13.45, 3.2), arrowprops=dict(arrowstyle='->', lw=1.5))
t(13.3, 1.85, 'LED1 (feedback)'); t(11.9, 3.25, '+', fontsize=12); t(11.95, 2.3, '−', fontsize=12)
line((12.8, 2.5), (12.8, 0)); dot(12.8, 0)

ax.set_xlim(0, 16.6); ax.set_ylim(-1, 9.8)
plt.tight_layout(); plt.savefig('docs/a4_schematic.png', dpi=150, facecolor='white')
