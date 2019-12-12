# Trip Cluster Tool Data
This project creates data for the [trip-cluster-tool](https://github.com/thomaslorincz/trip-cluster-tool) project
## Requirements
- Python >=3.4
## Setup
### Install Dependencies
```
pip install brotli
```
### Configuration
All configuration files are stored in the config directory.
At this time, only ```ZoneDefs.csv``` is needed to run the script.
If zone definitions change, modify (or replace) ```ZoneDefs.csv``` with the new information.
## Usage
Execute the following in a command shell:
```
python main.py <path to trips file>
```
Example:
```
python main.py total_trips_2020.csv
```
Note: The main script may run for a long time because it compresses the output.
The larger the raw output, the longer it takes to compress.
## Output
The script will output 2 files in the output directory: ```od.json``` (raw) and ```od.json.br``` (compressed).
Due to the large size of the raw file, it is recommended to only commit ```od.json.br``` to the [trip-cluster-tool](https://github.com/thomaslorincz/trip-cluster-tool) project.
