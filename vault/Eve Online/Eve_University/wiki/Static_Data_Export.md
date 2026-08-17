---
title: "Static Data Export"
url: "https://wiki.eveuniversity.org/Static_Data_Export"
pageid: 11898
source: "EVE University Wiki"
categories: ["Applications", "Needing updates"]
harvested_at: "2026-08-16 23:22:29 UTC"
---

# Static Data Export

CCP provides developers a series of static files, known as the Static Data Export(SDE), which contains static data from the Tranquility server. The SDE is currently exported as .yaml and .jsonl files, however, different and easier to use formats(mentioned below) are made by the community. The SDE can be found at the EVE developers [Static Data](https://developers.eveonline.com/static-data) page. All resources provided by CCP are subject to the [developer license agreement](https://developers.eveonline.com/license-agreement).

1. # Fuzzwork SDE Conversions
To aide fellow developers and players in consuming this data without having to extract or convert from YAML or JSON Lines format every time Steve Ronuken has hosted conversions in PostgreSQL, SQLite, MySQL, MSSQL, and CSV formats. They can be found at [Fuzzwork](https://www.fuzzwork.co.uk) under SDE or more directly at [www.fuzzwork.co.uk/dump](https://www.fuzzwork.co.uk/dump). Individual table data can be found in **CSV** and **SQL** (MySQL) formats here [www.fuzzwork.co.uk/dump/latest](https://www.fuzzwork.co.uk/dump/latest).

  1. # Opening a file from Fuzzwork SDE Conversions
To extract data from compressed files, use [tar](https://ss64.com/bash/tar.html) for <code>.tar.bz2</code> files or [bunzip2](https://ss64.com/osx/bzip.html) for <code>.bz2</code> files in Linux, and something like [7-zip](https://www.7-zip.org/) for either format in Windows. Once extracted the files can be opened in the appropriate application that supports the file format.

1. # How does the ESI fit into all this?
The **EVE Stable Infrastructure** (ESI) intends to have endpoints to account for all of the SDE; currently, it's not quite there yet, and the SDE is needed for many projects. The progress can be tracked on the [SDE parity checklist](https://github.com/esi/esi-issues/issues/1103) at the [ESI](https://github.com/esi) GitHub.

1. # How to implement the original SDE into your application
  1. # Step 0: Preface
This is not a guide to Python or programming, if you don't know how to program, there are tons of resources to learn to code, there are a few of my favorites in the **External links** section.

  1. # Step 1: Opening the file
Firstly, find the file containing the data you need, for this example, I'm going to use fsd/blueprints.yaml. This file contains all the information required to build an industry cost predictor. Next, open the file using your desired programming language, I'm going to use python, so to open this I'll run <code>with open("fsd/blueprints.yaml", "r") as f:</code>. The file is open! To the next step!

  1. # Step 2: Reading the file
  1. ## Step 2.1: Installing PyYAML
Assuming you're using pip, this should be as simple as <kbd>pip install pyyaml</kbd>. If you having issues have a look at [Reading and Writing YAML to a File in Python](https://stackabuse.com/reading-and-writing-yaml-to-a-file-in-python/) on stackabuse.

  1. ## Step 2.2: Interpreting the file
Now that PyYAML is installed, we need to use it to parse our file, we have already opened it, so it should just be a matter of parsing it with PyYAML, which can be done by <code>blueprints = yaml.load(f, Loader=yaml.FullLoader)</code>, remember to have *import yaml* at the top of your .py file. Hopefully now if you print out the blueprints variable, your console will be filled with sweet, sweet data and the taste of success. The data will be a dictionary, and the rest from here should be relatively simple, it should just be navigating through the data as if it was a dictionary. 

  1. # Step 3: Postface
I hope this short guide helped you somewhat get into the SDE.

1. # Content of each table (version 2025-07-07)

| -
! Table name !! Content |
| :--- |
| [agtAgents.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/agtAgents.csv.bz2) |
| [agtAgentsInSpace.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/agtAgentsInSpace.csv.bz2) |
| [agtAgentTypes.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/agtAgentTypes.csv.bz2) |
| [agtResearchAgents.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/agtResearchAgents.csv.bz2) |
| [certCerts.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/certCerts.csv.bz2) |
| [certMasteries.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/certMasteries.csv.bz2) |
| [certSkills.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/certSkills.csv.bz2) |
| [charFactions.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/charFactions.csv.bz2) |
| [chrAttributes.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/chrAttributes.csv.bz2) |
| [chrBloodlines.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/chrBloodlines.csv.bz2) |
| [chrFactions.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/chrFactions.csv.bz2) |
| [chrRaces.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/chrRaces.csv.bz2) |
| [crpActivities.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/crpActivities.csv.bz2) |
| [crpNPCCorporationDivisions.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/crpNPCCorporationDivisions.csv.bz2) |
| [crpNPCCorporationResearchFields.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/crpNPCCorporationResearchFields.csv.bz2) |
| [crpNPCCorporations.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/crpNPCCorporations.csv.bz2) |
| [crpNPCCorporationTrades.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/crpNPCCorporationTrades.csv.bz2) |
| [crpNPCDivisions.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/crpNPCDivisions.csv.bz2) |
| [dgmAttributeCategories.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/dgmAttributeCategories.csv.bz2) |
| [dgmAttributeTypes.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/dgmAttributeTypes.csv.bz2) |
| [dgmEffects.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/dgmEffects.csv.bz2) |
| [dgmExpressions.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/dgmExpressions.csv.bz2) |
| [dgmTypeAttributes.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/dgmTypeAttributes.csv.bz2) |
| [dgmTypeEffects.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/dgmTypeEffects.csv.bz2) |
| [eveGraphics.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/eveGraphics.csv.bz2) |
| [eveIcons.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/eveIcons.csv.bz2) |
| [eveUnits.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/eveUnits.csv.bz2) |
| [industryActivity.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/industryActivity.csv.bz2) |
| [industryActivityMaterials.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/industryActivityMaterials.csv.bz2) |
| [industryActivityProbabilities.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/industryActivityProbabilities.csv.bz2) |
| [industryActivityProducts.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/industryActivityProducts.csv.bz2) |
| [industryActivityRaces.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/industryActivityRaces.csv.bz2) |
| [industryActivitySkills.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/industryActivitySkills.csv.bz2) |
| [industryBlueprints.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/industryBlueprints.csv.bz2) |
| [invCategories.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invCategories.csv.bz2) |
| [invContrabandTypes.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invContrabandTypes.csv.bz2) |
| [invControlTowerResourcePurposes.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invControlTowerResourcePurposes.csv.bz2) |
| [invControlTowerResources.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invControlTowerResources.csv.bz2) |
| [invFlags.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invFlags.csv.bz2) |
| [invGroups.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invGroups.csv.bz2) |
| [invItems.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invItems.csv.bz2) |
| [invMarketGroups.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invMarketGroups.csv.bz2) |
| [invMetaGroups.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invMetaGroups.csv.bz2) |
| [invMetaTypes.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invMetaTypes.csv.bz2) |
| [invNames.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invNames.csv.bz2) |
| [invPositions.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invPositions.csv.bz2) |
| [invTraits.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invTraits.csv.bz2) |
| [invTypeMaterials.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invTypeMaterials.csv.bz2) |
| [invTypeReactions.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invTypeReactions.csv.bz2) |
| [invTypes.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invTypes.csv.bz2) |
| [invTypes-nodescription.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invTypes-nodescription.csv.bz2) |
| [invUniqueNames.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invUniqueNames.csv.bz2) |
| [invVolumes.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/invVolumes.csv.bz2) |
| [mapCelestialGraphics.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/mapCelestialStatistics.csv.bz2) |
| [mapCelestialStatistics.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/mapCelestialStatistics.csv.bz2) |
| [mapConstellationJumps.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/mapConstellationJumps.csv.bz2) |
| [mapConstellations.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/mapConstellations.csv.bz2) |
| [mapDenormalize.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/mapDenormalize.csv.bz2) |
| [mapJumps.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/mapJumps.csv.bz2) |
| [mapLandmarks.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/mapLandmarks.csv.bz2) |
| [mapLocationWormholeClasses.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/mapLocationWormholeClasses.csv.bz2) |
| [mapRegionJumps.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/mapRegionJumps.csv.bz2) |
| [mapRegions.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/mapRegions.csv.bz2) |
| [mapSolarSystemJumps.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/mapSolarSystemJumps.csv.bz2) |
| [mapSolarSystems.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/mapSolarSystems.csv.bz2) |
| [mapUniverse.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/mapUniverse.csv.bz2) |
| [planetSchematics.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/planetSchematics.csv.bz2) |
| [planetSchematicsPinMap.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/planetSchematicsPinMap.csv.bz2) |
| [planetSchematicsTypeMap.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/planetSchematicsTypeMap.csv.bz2) |
| [ramActivities.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/ramActivities.csv.bz2) |
| [ramAssemblyLineStations.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/ramAssemblyLineStations.csv.bz2) |
| [ramAssemblyLineTypeDetailPerCategory.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/ramAssemblyLineTypeDetailPerCategory.csv.bz2) |
| [ramAssemblyLineTypeDetailPerGroup.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/ramAssemblyLineTypeDetailPerGroup.csv.bz2) |
| [ramAssemblyLineTypes.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/ramAssemblyLineTypes.csv.bz2) |
| [ramInstallationTypeContents.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/ramInstallationTypeContents.csv.bz2) |
| [skinLicense.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/skinLicense.csv.bz2) |
| [skinMaterials.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/skinMaterials.csv.bz2) |
| [skins.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/skins.csv.bz2) |
| [skinShip.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/skinShip.csv.bz2) |
| [solarsystemprecise.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/solarsystemprecise.csv.bz2) |
| [staOperations.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/staOperations.csv.bz2) |
| [staOperationServices.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/staOperationServices.csv.bz2) |
| [staServices.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/staServices.csv.bz2) |
| [staStations.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/staStations.csv.bz2) |
| [staStationTypes.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/staStationTypes.csv.bz2) |
| [translationTables.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/translationTables.csv.bz2) |
| [trnTranslationColumns.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/trnTranslationColumns.csv.bz2) |
| [trnTranslationLanguages.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/trnTranslationLanguages.csv.bz2) |
| [trnTranslations.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/trnTranslations.csv.bz2) |
| [warCombatZones.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/warCombatZones.csv.bz2) |
| [warCombatZoneSystems.csv.bz2](https://www.fuzzwork.co.uk/dump/latest/warCombatZoneSystems.csv.bz2) |

1. # External links
- [CodeCademy](https://codecademy.com)
- [Corey Schafer](https://www.youtube.com/channel/UCCezIgC97PvUuR4_gbFUs5g)
- EVE Online Discord Dev Chat [3rd-party-dev-and-esi](https://discord.com/channels/940573867192221696/972841377798946896) - I read most messages sent here, if you need help that StackOverflow can't provide, here is your best bet.
