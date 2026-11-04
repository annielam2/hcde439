# Plots the voltage at servo pin 9 for the A4 Question 1 sweep loop
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
P=20.0  # servo period ms (50 Hz)
def pw(deg): return 0.544+(2.4-0.544)*deg/180  # Servo lib default pulse range
def trace(t_ms, pos_of_t):
    v=np.zeros_like(t_ms)
    for i,t in enumerate(t_ms):
        start=np.floor(t/P)*P
        v[i]=5.0 if (t-start)<pw(pos_of_t(start)) else 0.0
    return v
fig,ax=plt.subplots(3,1,figsize=(11,9))
t=np.linspace(0,300,30000); pos=lambda s: min(int(s//100),180)
ax[0].plot(t,trace(t,pos),lw=1.2,color="#1f5fa8"); ax[0].set_xlim(0,300)
for x in (100,200): ax[0].axvline(x,ls="--",c="gray",lw=.8)
ax[0].set_title("Zoom: first 300 ms: pos = 0°, 1°, 2° (each held 100 ms = 5 pulses)")
ax[0].text(3,5.25,"pulse ≈ 0.54 ms wide, repeats every 20 ms (50 Hz)",fontsize=9)
t2=np.linspace(18000,18200,20000); pos2=lambda s: 180 if s<18100 else 0
ax[1].plot(t2,trace(t2,pos2),lw=1.2,color="#1f5fa8"); ax[1].axvline(18100,ls="--",c="gray",lw=.8)
ax[1].set_title("Zoom: end of sweep: pos = 180° (pulse ≈ 2.4 ms), then loop() restarts at 0°")
T=np.arange(0,40000,10); ph=T%18100; deg=np.minimum(ph//100,180)
ax[2].plot(T/1000,pw(deg),color="#c0392b"); ax[2].set_ylabel("pulse width (ms)\n(time pin 9 is at 5 V)")
ax[2].set_title("Whole picture: pulse width ramps 0.54 to 2.4 ms over 18.1 s, then jumps back (sawtooth)")
ax[2].set_xlabel("time (s)")
for a in ax[:2]: a.set_ylabel("V(pin 9) to GND"); a.set_ylim(-.3,5.8); a.set_yticks([0,5]); a.set_xlabel("time (ms)")
plt.tight_layout(); plt.savefig("docs/a4_servo_graph.png",dpi=130)
