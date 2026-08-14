# EVE Online: Smartbomb Spherical AoE Physics & Ship Collision Bump Mechanics

Instantaneous area-of-effect damage propagation and momentum transfer mechanics.

---

## 💥 Smartbomb Spherical AoE Matrix
| Module Size | Blast Radius | Raw Damage per Cycle | Cycle Duration | Tracking Check |
| :--- | :--- | :--- | :--- | :--- |
| **Small Smartbomb** | **2,500 m** | 75 HP | 5.0 Seconds | **Zero / Instant (100% Hit)** |
| **Medium Smartbomb**| **5,000 m** | 150 HP | 7.5 Seconds | **Zero / Instant (100% Hit)** |
| **Large Smartbomb** | **7,500 m** | 300 - 375 HP | 10.0 Seconds | **Zero / Instant (100% Hit)** |
| **Officer Smartbomb**| **10,000 m** | 450 HP | 10.0 Seconds | **Zero / Instant (100% Hit)** |

- **Pipebombing Protocol**: Rokh / Megathron battleships light smartbombs simultaneously on warp-in vectors, vaporizing whole Cruiser/Battlecruiser fleets in a single server tick.

---

## 🚀 Ship Collision & Momentum Bump Physics
Momentum is conserved during ship collisions:

$$m_1 \vec{v}_1 + m_2 \vec{v}_2 = m_1 \vec{v}_1' + m_2 \vec{v}_2'$$

- **The Machariel Bump Tactic**: A 3,000 m/s 500MN MWD Machariel colliding with an aligned Freighter transfers massive momentum, knocking the target **20-30 km off its warp vector** and resetting the 75% alignment threshold.
