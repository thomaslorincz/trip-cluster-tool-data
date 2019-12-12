import csv
import json
import sys

import brotli


def generate_json_data():
    if len(sys.argv) != 2:
        print("Error: Incorrect number of arguments. Expected 1.")
        print("Usage: python main.py trips_file.csv")
        exit(1)

    zones = []  # List of all zones
    zone_to_district = {}  # Dictionary mapping zone ID to district ID
    with open("config/ZoneDefs.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            zones.append(int(row["TAZ"]))
            zone_to_district[int(row["TAZ"])] = int(row["District"])

    # Map input fields to output fields
    input_to_output = {
        "SOV": "auto",      # Single-Occupant Vehicle
        "HOV2": "auto",     # High-Occupancy Vehicle (2 people)
        "HOV3": "auto",     # High-Occupancy Vehicle (3+ people)
        "SB": "auto",       # School Bus
        "WAT": "transit",   # Walk Access Transit
        "PNR": "transit",   # Park and Ride
        "RNUP": "transit",  # Ride and Park
        "KNR": "transit",   # Kiss and Ride
        "RNK": "transit",   # Ride and Kiss
        "Bike": "active",
        "Walk": "active",
        "O": "home",
        "W": "work",
        "S": "school",
        "H": "shop",
        "T": "eat",
        "C": "other",       # Escort
        "P": "other",       # Personal Business
        "Q": "other",       # Quick Stop
        "L": "other",       # Social
        "R": "other",       # Recreation
        "1": "early",
        "21": "amRush",     # AM Shoulder 1
        "22": "amRush",     # AM Crown
        "23": "amRush",     # AM Shoulder 2
        "3": "midday",
        "41": "pmRush",     # PM Shoulder 1
        "42": "pmRush",     # PM Crown
        "43": "pmRush",     # PM Shoulder 2
        "5": "evening",
        "6": "overnight"
    }

    mode_fields = ["auto", "transit", "active"]
    purpose_fields = ["home", "work", "school", "shop", "eat", "other"]
    time_fields = [
        "early", "amRush", "midday", "pmRush", "evening", "overnight"
    ]

    output_fields = []
    for mode in mode_fields:
        for purpose in purpose_fields:
            for time in time_fields:
                output_fields.append("{}_{}_{}".format(mode, purpose, time))

    # Create a dictionary of all OD pairs and their data
    # E.g.
    # {
    #    101: {101: {"auto_home": 0, ...}, 102: {...}, ...},
    #    102: {101: {"auto_home": 0, ...}, 102: {...}, ...},
    #    103: {101: {"auto_home": 0, ...}, 102: {...}, ...},
    #    ...
    # }
    count = {
        i: {j: {d: 0 for d in output_fields} for j in zones} for i in zones
    }

    # Iterate through every row of the trips file and tabulate its data
    with open(sys.argv[1], "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mode = input_to_output[row["Mode"]]
            purpose = input_to_output[row["DPurp"]]
            time = input_to_output[row["Time"]]
            field = "{}_{}_{}".format(mode, purpose, time)

            count[int(row["I"])][int(row["J"])][field] += 1

    # Create a JSON array output file and write all trip data to it
    with open("output/od.json", "w") as w:
        # Iterate through the data of all OD pairs
        output = []
        for i, j_dict in count.items():
            for j, count_dict in j_dict.items():
                # Only include a row if at least one of its values is nonzero
                if any(count_dict.values()):
                    output.append({
                        "originZone": i,
                        "destZone": j,
                        "originDistrict": zone_to_district[i],
                        "destDistrict": zone_to_district[j],
                        "trips": [
                            [
                                [
                                    count_dict[
                                        "{}_{}_{}".format(mode, purpose, time)
                                    ] for time in time_fields
                                ] for purpose in purpose_fields
                            ] for mode in mode_fields
                        ]
                    })
        w.write(json.dumps(output))


def compress_json_data():
    with open("output/od.json", "rb") as r, \
            open("output/od.json.br", "wb") as w:
        w.write(brotli.compress(r.read()))


if __name__ == "__main__":
    generate_json_data()
    compress_json_data()
