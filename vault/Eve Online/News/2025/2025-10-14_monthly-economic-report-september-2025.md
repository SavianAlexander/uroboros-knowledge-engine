# Monthly Economic Report - September 2025

- **Date**: 2025-10-14T13:00:00.000Z
- **Category**: dev-blogs
- **Author**: EVE Online Economic Council
- **Source**: https://www.eveonline.com/news/view/monthly-economic-report-september-2025
- **Tags**: #dev-blogs

## Overview
The Monthly Economic Report for September 2025 is now available!

---

Economic Capsuleers!

The Monthly Economic Report for September 2025 is now available!

**The following Plots & CSVs have been removed:**


- `0_produced_vs_mining_vs_destroyed` - Plot has been replaced, listed below.
- `0_produced_vs_mining_vs_destroyed__pct_mining` - Plot has been replaced, listed below.
- `0_produced_vs_mining_vs_destroyed__pct_production` - Plot has been replaced, listed below.
- `0_produced_vs_mining_vs_destroyed__pct_destruction` - Plot has been replaced, listed below.
- `1_regional_stats` - Import/Export data-source has been deprecated. Plot has been replaced, listed below.
- `2_destruction_value_by_region` - Plot provided very little usable value. All data exists in new data-export, listed below.
- `3_mining_value_by_region` - Plot provided very little usable value. All data exists in new data-export, listed below.
- `3_npc_bounties_by_region` - Plot provided very little usable value. All data exists in new data-export, listed below.
- `4_production_value_by_region` - Plot provided very little usable value. All data exists in new data-export, listed below.
- `5_trade_balance_by_region` - Plot provided very little usable value. All data exists in new data-export, listed below.
- `5_trade_balance_m3_by_region` - Import/Export data-source has been deprecated.
- `6_trade_value_by_region` - Plot provided very little usable value. All data exists in new data-export, listed below.
- `7_imports_exports_net_exports` - Import/Export data-source has been deprecated.
- `12a_wormhole_import_export` - Import/Export data-source has been deprecated.
- `12b_wormhole_import_export` - Import/Export data-source has been deprecated.
- `STATIC_ore_type_mapping.csv` - Data now exists in new data-export, listed below.
- `regional_stats.csv` - Data now exists (excluding import/export) in new data-export, listed below.
- `wormhole-trade.csv` - Import/Export data-source has been deprecated.


**The following Plots and CSVs have been added:**


- `0_mining_production_destruction_history` - New methodology used (described in `README.md`). In short, static type values are used so the plot shows the change in mining/production/destruction rather than the change in both.
- `0_mining_by_location`- New methodology used (described in `README.md`). Uses meta-locations which include more variance, i.e. Null Sec (Sov) vs Null Sec (NPC).
- `0_production_by_location` - New methodology used (described in `README.md`). Uses meta-locations which include more variance, i.e. Null Sec (Sov) vs Null Sec (NPC).
- `0_destruction_by_location` - New methodology used (described in `README.md`). Uses meta-locations which include more variance, i.e. Null Sec (Sov) vs Null Sec (NPC).
- `1_regional_stats` - New methodology used (described in `README.md`). No longer includes Imports/Exports. Production and Mining values use static pricing.
- `0_mining_production_destruction.csv` - All data needed to recreate `mining_production_destruction` plots, including by location sub-charts.
- `1_key_economic_figures_by_region.csv` - All data needed to recreate `regional_stats` plot.
- `static_ore_metagroups.csv` - Replacement of `STATIC_ore_type_mapping.csv`
- `static_solarsystems.csv` - Breakdown of all solarsystems including Location Metagroup (used in various plots and datasets).
- `static_type_values.csv` - Values used various plots where static prices used.


**Future**


- We plan to setup a github repository that will show the code behind each plot. Its primary purpose will be to enable tickets when you find issues with the MER.
- All existing plots will be moved over to the new process over time. Expect the MER to continue to change and evolve over the coming months. Thanks for your patience.
- We are considering exporting some of the larger data-exports in a binary format (such as parquet) for speed of reading and a smaller size.
- New plots and data-exports will be added, including a price history for each type, and what data-source we used (Market, ZKB or Base pricing).


**Economic Trends**


- Destruction remains relatively stable over the last ~9 months. While production continues its long term (~18 months) trend upward.
- Money supply has stopped falling. However ISK velocity continues its downward trend over the last ~6 months.
- MPI continues to fall.


You can download all of the raw data used in this report [here](https://web.ccpgamescdn.com/aws/community/EVEOnline_MER_202509.zip). Each image can be enlarged by clicking on it.

To join the player discussion, please visit the official thread on [EVE Online forums](https://forums.eveonline.com/t/monthly-economic-report-september-2025/499210).
