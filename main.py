import csv
import sys

import brotli


def generate_csv_data():
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
        "SOV": "auto",  # Single-Occupant Vehicle
        "HOV2": "auto",  # High-Occupancy Vehicle (2 people)
        "HOV3": "auto",  # High-Occupancy Vehicle (3+ people)
        "SB": "auto",  # School Bus
        "WAT": "transit",  # Walk Access Transit
        "PNR": "transit",  # Park and Ride
        "RNUP": "transit",   # Ride and Park
        "KNR": "transit",  # Kiss and Ride
        "RNK": "transit",  # Ride and Kiss
        "Bike": "active",
        "Walk": "active",
        "O": "home",
        "W": "work",
        "S": "school",
        "H": "shop",
        "T": "eat",
        "C": "other",  # Escort
        "P": "other",  # Personal Business
        "Q": "other",  # Quick Stop
        "L": "other",  # Social
        "R": "other",  # Recreation
    }

    mode_fields = ["auto", "transit", "active"]
    purpose_fields = ["home", "work", "school", "shop", "eat", "other"]

    output_fields = []
    for mode in mode_fields:
        for purpose in purpose_fields:
            output_fields.append("{}_{}".format(mode, purpose))

    # Create a dictionary of all OD pairs and their data
    # E.g.
    # {
    #    101: {101: {"auto_home": 0, ...}, 102: {...}, ...},
    #    102: {101: {"auto_home": 0, ...}, 102: {...}, ...},
    #    103: {101: {"auto_home": 0, ...}, 102: {...}, ...},
    #    ...
    # }
    output = {
        i: {j: {d: 0 for d in output_fields} for j in zones} for i in zones
    }

    # Iterate through every row of the trips file and tabulate its data
    with open(sys.argv[1], "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mode = input_to_output[row["Mode"]]
            purpose = input_to_output[row["DPurp"]]
            field = "{}_{}".format(mode, purpose)

            output[int(row["I"])][int(row["J"])][field] += 1

    # Create a CSV output file and write all output rows to it
    with open("output/od.csv", "w") as w:
        fieldnames = [
            "originZone",
            "destZone",
            "originDistrict",
            "destDistrict",
            *output_fields
        ]

        # Create a DictWriter instance with LF (UNIX) terminators
        writer = csv.DictWriter(w, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()

        # Iterate through the data of all OD pairs
        for i, j_dict in output.items():
            for j, count_dict in j_dict.items():
                # Only include a row if at least one of its values is nonzero
                if any(count_dict.values()):
                    writer.writerow({
                        "originZone": i,
                        "destZone": j,
                        "originDistrict": zone_to_district[i],
                        "destDistrict": zone_to_district[j],
                        **{d: count_dict[d] for d in output_fields}
                    })

    with open("output/od.csv", "rb") as r, open("output/od.csv.br", "wb") as w:
        w.write(brotli.compress(r.read()))


if __name__ == "__main__":
    generate_csv_data()
