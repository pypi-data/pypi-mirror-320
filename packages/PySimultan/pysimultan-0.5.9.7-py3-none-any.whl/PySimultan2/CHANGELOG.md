Version 0.5.9.7 (09.01.2024)
- Added default component support to Mapper: if a default component is not present in the datamodel, it is automatically added
- Fixed content naming bug: Content.name is now used for the name of the TaxonomyEntry in SIMULTAN
- Added typing for better code completion

Version 0.5.9.4 (31.12.2024)
- Fixed bug in DirectoryInfo where __dir__helper_file__ was not found if already existing

Version 0.5.7 (11.12.2024)
- Added get_orientation_to_volume method to SimultanFace which returns the orientation of the face to the volume

Version 0.5.3 (01.12.2024)
- Added support for directories (Assets and FileInfo)

Version 0.5.1 (25.11.2024)

- setting re-register default in Mapper to True
- added uncache method to utils for monkey patching
