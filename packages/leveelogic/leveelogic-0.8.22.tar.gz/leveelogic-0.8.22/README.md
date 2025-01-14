## IDEAS



## ADVANCED STUFF

Leveelogic combines the geolib code () with its own solutions. To avoid problems with new geolib versions
specific solutions are simply implemented as classes with the same name as the geolib ones but with added
functionality or fixed bugs. This way we avoid the need for an updated geolib and we can proceed with 
the leveelogic code until geolib fixed the bugs internally.

These classes are defined in the external directory and files;

* dgeolib.py (added a lot of extra fields for convinience)
* internal.py (added a bugfix for allowing reference lines that allow interpolation)

For the developers this means that during updates of geolib these classes have to be checked
to see if functionality has been added or bugs have been fixed that make leveelogic code
old or obsolete. 

Sounds like a headache but it is still easier then waiting for geolib to fix the bugs!

## Settings

You will need a leveelogic.env with the following paths:

* DSTABILITY_CONSOLE_EXE, location of the dstability console
* DSTABILITY_MIGRATION_CONSOLE_PATH, location of the dstability migration console
* CALCULATIONS_FOLDER, location of the folder to add and remove temporary calculations