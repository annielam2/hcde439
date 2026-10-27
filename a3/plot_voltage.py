"""Plot V-measure (the voltage at A0) over time for A3.

Usage:
  1. Run a3.ino, open the Serial Monitor, and record your demo video at the same time.
  2. Copy everything in the Serial Monitor and paste it into a3/serial_log.txt
  3. python3 a3/plot_voltage.py a3/serial_log.txt
     -> writes docs/a3_voltage_graph.png

  python3 a3/plot_voltage.py --expected
     -> draws the graph predicted from the resistor calculations instead.
"""
import re
import sys
import matplotlib.pyplot as plt

THRESHOLD_V = 400 * 5 / 1023  # night threshold (reading 400) from a3.ino, in volts (1.96 V)
LINE = re.compile(r"Room light level: (\d+)")


def from_log(path):
    # a3.ino prints one reading every 100 ms, so line i is at time i * 0.1 s
    readings = [int(m.group(1)) for line in open(path, encoding="utf-8", errors="ignore")
                if (m := LINE.search(line))]
    t = [i * 0.1 for i in range(len(readings))]
    v = [r * 5 / 1023 for r in readings]  # convert 0-1023 back to volts
    return t, v


def expected():
    """Demo script: room light -> hand covers sensor -> room -> flashlight -> room."""
    def vout(r_ldr):
        return 5 * 10_000 / (r_ldr + 10_000)
    room, dark, bright = vout(10_000), vout(50_000), vout(2_000)
    keys = [(0, room), (4, room), (5, dark), (9, dark), (10, room), (12, room),
            (13, bright), (17, bright), (18, room), (20, room)]
    t, v = [], []
    for (t1, v1), (t2, v2) in zip(keys, keys[1:]):
        for i in range(10 * (t2 - t1)):
            t.append(t1 + i / 10)
            v.append(v1 + (v2 - v1) * i / (10 * (t2 - t1)))
    return t, v


if __name__ == "__main__":
    is_expected = len(sys.argv) < 2 or sys.argv[1] == "--expected"
    t, v = expected() if is_expected else from_log(sys.argv[1])

    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=150)
    ax.axhspan(0, THRESHOLD_V, color="#d62728", alpha=0.07)
    ax.axhline(THRESHOLD_V, color="#d62728", ls="--", lw=1)
    ax.text(t[-1], THRESHOLD_V + 0.08, "night threshold 1.96 V (reading 400)",
            ha="right", color="#d62728", fontsize=9)
    ax.plot(t, v, color="#1f4e79", lw=2)
    ax.set_xlim(0, t[-1])
    ax.set_ylim(0, 5)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("V-measure at A0 (V)")
    sec = ax.secondary_yaxis("right", functions=(lambda x: x * 1023 / 5, lambda y: y * 5 / 1023))
    sec.set_ylabel("analogRead() value")
    if is_expected:
        for x, label in [(2, "room light"), (7, "hand covers\nsensor"), (11, "room"),
                         (15, "flashlight"), (19, "room")]:
            ax.text(x, 4.6, label, ha="center", va="top", fontsize=9, color="#444")
    ax.set_title("V-measure over time" + (" (expected)" if is_expected else ""))
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("docs/a3_voltage_graph.png")
    print("wrote docs/a3_voltage_graph.png")
