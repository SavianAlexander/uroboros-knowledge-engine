# Planetary Industry (PI) Production Chain Solver & Factory Topology

Complete automated dependency resolution engine for High-Tech P4 manufacturing across planetary networks.

---

## 🌐 P4 Master Commodity Schematics
### 🏭 **Broadcast Node**
- **Unit Market Value**: `3,450,000 ISK` *(Volume: 100.0 m³)*
- **Primary Industrial Usage**: Sovereignty Infrastructure & Upwell Citadel Construction
- **Required P3 Inputs**: `Data Chips (x1), High-Tech Transmitter (x1), Neocoms (x1)`
- **P2 Intermediates**: `Microfiber Shielding, Synthetic Synapses, Polytextiles, Biocells, Silicate Glass`
- **Required Planet Topology**: `Barren, Gas, Oceanic, Temperate`

### 🏭 **Integrity Response Drones**
- **Unit Market Value**: `3,820,000 ISK` *(Volume: 100.0 m³)*
- **Primary Industrial Usage**: Upwell Structure Quantum Cores & Supercapital Assemblies
- **Required P3 Inputs**: `Guidance Systems (x1), Hazmat Detection Systems (x1), Planetary Vehicles (x1)`
- **P2 Intermediates**: `Water-Cooled CPU, Superconductors, Biocells, Microfiber Shielding, Mechanical Parts, Coolant`
- **Required Planet Topology**: `Barren, Lava, Oceanic, Storm, Temperate`

### 🏭 **Nano-Factory**
- **Unit Market Value**: `3,610,000 ISK` *(Volume: 100.0 m³)*
- **Primary Industrial Usage**: Capital Construction & Advanced Cynosural Upgrades
- **Required P3 Inputs**: `Industrial Explosives (x1), Supercomputers (x1), Ukomi Super Conductors (x1)`
- **P2 Intermediates**: `Fertilizer, Polytextiles, Consumer Electronics, Synthetic Synapses, Superconductors`
- **Required Planet Topology**: `Gas, Lava, Plasma, Storm, Temperate`

### 🏭 **Wetware Mainframe**
- **Unit Market Value**: `3,950,000 ISK` *(Volume: 100.0 m³)*
- **Primary Industrial Usage**: Capital Jump Drives, Supercarriers & Titans
- **Required P3 Inputs**: `Bioreactive Transponder (x1), Supercomputers (x1), Synthetic Synapses (x1)`
- **P2 Intermediates**: `Biocells, Consumer Electronics, Synthetic Synapses, Genetically Enhanced Livestock`
- **Required Planet Topology**: `Oceanic, Plasma, Storm, Temperate`


---

## ⚙️ Factory Throughput & Cycle Mechanics
1. **Basic Industry Facility (P0 $\rightarrow$ P1)**:
   - Input: **3,000 units P0** $\rightarrow$ Output: **20 units P1**
   - Cycle Duration: **30 minutes** (Power: 200 MW, CPU: 800 tf)
2. **Advanced Industry Facility (P1 $\rightarrow$ P2)**:
   - Input: **40 units P1 (20 + 20)** $\rightarrow$ Output: **5 units P2**
   - Cycle Duration: **60 minutes** (Power: 500 MW, CPU: 700 tf)
3. **Advanced Industry Facility (P2/P1 $\rightarrow$ P3)**:
   - Input: **20 units P2 / P1** $\rightarrow$ Output: **3 units P3**
   - Cycle Duration: **60 minutes** (Power: 500 MW, CPU: 700 tf)
4. **High-Tech Production Plant (P3/P1 $\rightarrow$ P4)**:
   - Input: **P3 Intermediates** $\rightarrow$ Output: **1 unit P4**
   - Cycle Duration: **60 minutes** (Power: 1100 MW, CPU: 400 tf)

---

## 💰 Customs Office (POCO) Tax Optimization Formula
- **Tax Formula**: `Total_Tax = Base_Tax_Value * (NPC_Tax_Rate + Player_Corp_Tax_Rate)`
- **Highsec Base NPC Tax**: **10.0%** (reduced to **5.0%** with *Customs Code Expertise V*)
- **Nullsec Player POCO Tax**: Typically **0.0% to 2.5%** in sovereign alliance space (KarmaFleet / Goonswarm)
