# MLTask Utils

### to build the package

run `./build.sh`

### to push to pypi

run `./push_to_pepe/sh`

### to include in taskexecutor

run `/dump_in_mltask_processor.sh`
keep in mind this simply copies and dumps the .whl file using the same name, without considering the version since that would require us to update the requirements.txt and dockerfile with every update
see [Notes](NOTES.md) for more info
