# EVE Online: Jump Drive Navigation, Cyno Corridors & Jump Fatigue Physics

Mathematical formulas and logistics planning for Capital Ships, Jump Freighters, and Black Ops.

---

## 📐 Jump Distance & Range Physics
$$\text{Distance (LY)} = \sqrt{(X_2 - X_1)^2 + (Y_2 - Y_1)^2 + (Z_2 - Z_1)^2} \times \text{Scale}$$

### Maximum Jump Range by Class (with Jump Drive Calibration V):
- **Jump Freighters (Nomad, Ark, Rhea, Anshar)**: **10.0 Light Years**
- **Black Ops Battleships (Redeemer, Panther, Widow, Sin)**: **10.0 Light Years**
- **Capitals (Dreadnoughts, FAX, Carriers, Titans)**: **7.0 Light Years**

---

## ⏳ Jump Fatigue Mathematics
$$\text{New Fatigue} = \max(10 \text{ minutes}, \text{Current Fatigue} \times (1 + \text{Distance Travelled in LY}))$$

$$\text{Jump Activation Cooldown} = \frac{\text{Jump Fatigue}}{10}$$

- **Fatigue Cap**: Maximum fatigue is capped at **5.0 Hours** (300 minutes), ensuring maximum jump cooldown never exceeds **30 minutes**.
- **Jump Freighter / Industrial Bonus**: Jump Freighters receive a **90% reduction to Jump Fatigue accumulation**.

---

## 🛰️ Cynosural Field Generator Types
- **Standard Cyno**: Fits on Force Recon Ships and Heavy Industrials; lights beacon for all capital ships.
- **Covert Cyno**: Fits on Covert Ops, Blockade Runners, T3C; undetectable on overview; allows Black Ops and covert bridges.
- **Industrial Cyno**: Fits on standard T1 Haulers and Ventures; lights beacon exclusively for Jump Freighters.
