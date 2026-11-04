# Draws a breadboard wiring view of the A4 circuit (IR receiver -> Arduino -> servo + LED)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon
fig, ax = plt.subplots(figsize=(14, 7.5)); ax.set_aspect('equal'); ax.axis('off')
def wire(pts, c, lw=3.5):
    xs, ys = zip(*pts); ax.plot(xs, ys, color=c, lw=lw, solid_capstyle='round', zorder=4)
def t(x, y, s, **kw): ax.text(x, y, s, **{'fontsize': 10, 'zorder': 6, **kw})

# Arduino
ax.add_patch(FancyBboxPatch((0, 1), 5.2, 6.2, boxstyle='round,pad=0.1', fc='#1b6ca8', ec='#0d3b5e', lw=2))
t(2.6, 4.1, 'Arduino Uno', ha='center', color='white', fontsize=14, weight='bold')
pins_top = {'D11': 2.0, 'D9': 3.0, 'D7': 4.0}
for n, x in pins_top.items():
    ax.add_patch(Rectangle((x-0.15, 6.55), 0.3, 0.3, fc='black', zorder=5)); t(x, 6.15, n, ha='center', color='white', weight='bold')
pins_bot = {'5V': 1.8, 'GND': 2.6}
for n, x in pins_bot.items():
    ax.add_patch(Rectangle((x-0.15, 1.15), 0.3, 0.3, fc='black', zorder=5)); t(x, 1.65, n, ha='center', color='white', weight='bold')

# Breadboard
ax.add_patch(Rectangle((7, 0.3), 14, 8.2, fc='#f4f1ea', ec='#bbb', lw=1.5))
ax.plot([7.2, 20.8], [8.1, 8.1], color='#c0392b', lw=1.5); t(6.6, 7.95, '+', color='#c0392b', fontsize=14, weight='bold')
ax.plot([7.2, 20.8], [7.6, 7.6], color='#2457a6', lw=1.5); t(6.6, 7.45, '−', color='#2457a6', fontsize=14, weight='bold')
for i in range(55):
    x = 7.4 + i*0.25
    for y in (7.85, 7.35): ax.plot(x, y, 's', ms=2.2, color='#999')
    for j in range(5): ax.plot(x, 6.6 - j*0.25, 's', ms=2.2, color='#999')
    for j in range(5): ax.plot(x, 3.4 - j*0.25, 's', ms=2.2, color='#999')
ax.add_patch(Rectangle((7.2, 3.6), 13.6, 1.4, fc='#e8e4da', ec='none'))
t(14, 4.2, 'center gap', ha='center', color='#999', fontsize=9)

# Power from Arduino to the rails
wire([(1.8, 1.3), (1.8, 0.0), (6.3, 0.0), (6.3, 8.1), (7.4, 8.1)], '#c0392b')
wire([(2.6, 1.3), (2.6, 0.45), (6.0, 0.45), (6.0, 7.6), (7.4, 7.6)], '#222')
t(5.5, -0.35, '5V → + rail (red)   GND → − rail (black)', fontsize=9.5)

# IR receiver module: legs at x = 9.0 (OUT/Y), 9.5 (VCC/R), 10.0 (GND/G), row y = 6.1
ax.add_patch(Rectangle((8.7, 5.3), 1.6, 0.55, fc='#333', zorder=5))
ax.add_patch(Circle((9.5, 5.05), 0.4, fc='#111', zorder=5))
for x, lab in ((9.0, 'Y'), (9.5, 'R'), (10.0, 'G')):
    ax.plot([x, x], [5.85, 6.1], color='#888', lw=2, zorder=5); t(x, 5.95, lab, ha='center', color='white', fontsize=8, weight='bold')
t(9.5, 4.35, 'IR receiver', ha='center', fontsize=10, weight='bold')
wire([(9.5, 6.35), (9.5, 8.1)], '#c0392b')
wire([(10.0, 6.35), (10.2, 7.6)], '#222')
wire([(9.0, 6.35), (9.0, 6.9), (2.0, 6.9), (2.0, 6.7)], '#e67e22')
t(4.8, 7.0, 'D11 → IR OUT (Y)', color='#b35900', fontsize=9.5, weight='bold')

# LED + 220 ohm resistor: D7 -> column 13.0 -> resistor -> 15.0 -> LED -> 15.5 -> ground rail
wire([(4.0, 6.7), (4.0, 5.6), (6.6, 5.6), (6.6, 6.35), (13.0, 6.35)], '#27ae60')
t(10.6, 5.55, 'D7 → resistor', color='#1e8449', fontsize=9.5, weight='bold')
ax.plot([13.0, 15.0], [6.1, 6.1], color='#888', lw=1.5, zorder=5)
ax.add_patch(Rectangle((13.45, 5.98), 1.1, 0.25, fc='#d8b47a', ec='#8a6d3b', zorder=6))
for k, c in enumerate(('#c0392b', '#c0392b', '#6e3b1f')): ax.add_patch(Rectangle((13.6 + k*0.25, 5.98), 0.08, 0.25, fc=c, zorder=7))
t(14.0, 5.5, '220 Ω', ha='center', fontsize=9.5)
ax.plot([15.0, 15.0], [6.1, 6.6], color='#888', lw=1.5, zorder=5); ax.plot([15.5, 15.5], [6.1, 6.6], color='#888', lw=1.5, zorder=5)
ax.add_patch(Circle((15.25, 6.95), 0.38, fc='#ff6b6b', ec='#c0392b', zorder=6))
t(15.25, 5.5, 'LED', ha='center', fontsize=9.5); t(14.55, 6.75, 'long\nleg +', fontsize=7.5, ha='center')
wire([(15.5, 6.1), (15.9, 7.6)], '#222')

# Servo: its cable plugs into columns 18.0 (brown), 18.5 (red), 19.0 (orange)
ax.add_patch(FancyBboxPatch((17.4, 0.6), 2.4, 1.6, boxstyle='round,pad=0.05', fc='#3b82c4', ec='#1d4f80', lw=2, zorder=5))
t(18.6, 1.3, 'Servo SG90', ha='center', color='white', weight='bold', zorder=7)
ax.add_patch(Circle((18.6, 2.5), 0.35, fc='white', ec='#1d4f80', zorder=6))
for x, c in ((18.0, '#6e3b1f'), (18.5, '#c0392b'), (19.0, '#e67e22')): ax.plot([x, x], [2.2, 3.15], color=c, lw=3, zorder=5)
wire([(18.0, 3.15), (18.0, 3.4), (17.2, 3.4), (17.2, 7.6)], '#222')
wire([(18.5, 3.15), (18.5, 3.55), (20.5, 3.55), (20.5, 8.1)], '#c0392b')
wire([(3.0, 6.7), (3.0, 5.2), (6.85, 5.2), (6.85, 2.8), (19.0, 2.8), (19.0, 3.15)], '#e67e22')
t(10.6, 2.45, 'D9 → servo signal (orange)', color='#b35900', fontsize=9.5, weight='bold')

ax.set_xlim(-0.4, 21.4); ax.set_ylim(-0.8, 8.8)
plt.tight_layout(); plt.savefig('../docs/a4_breadboard.png', dpi=140, facecolor='white')
