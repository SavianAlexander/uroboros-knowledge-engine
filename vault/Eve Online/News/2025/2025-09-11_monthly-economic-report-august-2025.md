# Monthly Economic Report - August 2025

- **Date**: 2025-09-11T15:53:00.000Z
- **Category**: dev-blogs
- **Author**: EVE Online Economic Council
- **Source**: https://www.eveonline.com/news/view/monthly-economic-report-august-2025
- **Tags**: #monthly-economic-reports, #dev-blogs

## Overview
The Monthly Economic Report for August 2025 is now available!

---

Greetings MER-enjoyers!

The Monthly Economic Report for August 2025 is now available!

The Future & Beta:


- We are doing major work on both the data-pipeline and output (plots and CSVs) of the MER. You can see some of the early output in the beta directory. Expect to see significantly more in the September MER.
- Some plots will removed, mostly due to data issues.. We’ll go though each in detail next MER release.
- Specific to the Import/Export Chart - The data-source for this being depreciated. Regardless, we’ll continue to run it for as long as we can, in its current state. We understand there is some interest in it at the moment.


Some of the issues it has:


- It ignores Titan Bridge movements.
- It ignored Jump Bridge movements (rare between regions) until recently.
- We wanted to only include Non-Singleton items (that is, un-assembled items), in cargo holds. We can’t, the current data-source doesn’t differentiate between singletons and non-singletons. Nor does it differentiate between different holds (for example - ship holds for Capitals). We want the chart to show the movement of goods (but not ships) between regions. Instead we get a weird mix of goods and some ships in some cases.


For those running scripts to extract data from the MER; Sorry. Thank you for your patience.

You can download all of the raw data used in this report [here](https://web.ccpgamescdn.com/aws/community/EVEOnline_MER_202508.zip). Each image can be enlarged by clicking on it.

To join the player discussion, please visit the official thread on [EVE Online forums](https://forums.eveonline.com/t/monthly-economic-report-august-2025/497419).
