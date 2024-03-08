import requests
import time
import csv
import geopy.distance


# convert gtfs file to dictionary
def convert_file(file, key):
    result = {}
    with open(file, mode="r") as f:
        lines = list(csv.reader(f))
        for line in lines[1:]:
            obj = {}
            for idx, field in enumerate(lines[0]):
                obj[field] = line[idx]
            if obj[key] not in result:
                result[obj[key]] = obj
    return result


# convert timestamp to string for logging
def convert_time(timestamp):
    return time.strftime("%X", time.localtime(timestamp))


# convert bus stops gtfs file
stops = convert_file("google_transit/stops.txt", "stop_id")

# initialize results csv file
header = [
    "tripId",
    "stopId",
    "arrivalTime",
    "predictionTime",
    "predictionDelta",
    "predictedTime",
    "predictionError",
    "predictionDelay",
]
f = open("data/predictions.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(header)

# initialize variables
predictions = {}
passed = set()
starttime = time.time()

while True:
    # get timestamp and stop after 24 hours
    timestamp = time.time()
    if timestamp - starttime > 86400:
        break

    try:
        # fetch vehicle positions
        vehicles_json = requests.get(
            f"https://s3.amazonaws.com/kcm-alerts-realtime-prod/vehiclepositions_enhanced.json"
        ).json()["entity"]

        # convert vehicle positions to dictionary
        vehicles = {}
        for vehicle in vehicles_json:
            vehicles[vehicle["vehicle"]["vehicle"]["id"]] = vehicle["vehicle"]

        # fetch trip updates
        trips = requests.get(
            f"https://s3.amazonaws.com/kcm-alerts-realtime-prod/tripupdates_enhanced.json"
        ).json()["entity"]

        print("data fetched")

        # iterate through trip updates
        for trip in trips:
            # check that necessary fields exits
            if (
                "vehicle" not in trip["trip_update"]
                or "trip" not in trip["trip_update"]
                or "stop_time_update" not in trip["trip_update"]
            ):
                continue

            # check that trip is scheduled
            if trip["trip_update"]["trip"]["schedule_relationship"] != "SCHEDULED":
                continue

            trip_id = trip["trip_update"]["trip"]["trip_id"]

            # check that vehicle exists
            vehicle_id = trip["trip_update"]["vehicle"]["id"]
            if vehicle_id not in vehicles:
                continue

            # initialize prediction dictionary
            if trip_id not in predictions:
                predictions[trip_id] = {}

            # get vehicle position
            trip_pos = (
                vehicles[vehicle_id]["position"]["latitude"],
                vehicles[vehicle_id]["position"]["longitude"],
            )

            # iterate through predicted stop times
            for stop_time in trip["trip_update"]["stop_time_update"]:
                stop_id = stop_time["stop_id"]

                # check that stop exists and has prediction
                if (
                    stop_id not in stops
                    or "arrival" not in stop_time
                    or "time" not in stop_time["arrival"]
                    or "delay" not in stop_time["arrival"]
                ):
                    continue

                # get stop position
                stop_pos = (
                    float(stops[stop_id]["stop_lat"]),
                    float(stops[stop_id]["stop_lon"]),
                )

                # check if vehicle is at stop
                if (
                    stop_id in predictions[trip_id]
                    and geopy.distance.distance(trip_pos, stop_pos).meters < 30
                ):
                    arrival_time = vehicles[vehicle_id]["timestamp"]
                    print(
                        "arrived: ",
                        stops[stop_id]["stop_name"],
                        convert_time(arrival_time),
                    )

                    # write predictions to csv
                    for predicted_time in predictions[trip_id][stop_id]:
                        writer.writerow(
                            [
                                trip_id,
                                stop_id,
                                arrival_time,
                                predicted_time[0],
                                predicted_time[0] - arrival_time,
                                predicted_time[1],
                                predicted_time[1] - arrival_time,
                                predicted_time[2],
                            ]
                        )

                    del predictions[trip_id][stop_id]
                    passed.add(trip_id + "-" + stop_id)
                    continue

                # check if stop has prediction
                if trip_id + "-" + stop_id in passed:
                    continue

                # add prediction to dictionary
                predicted_time = stop_time["arrival"]["time"]
                prediction_delay = stop_time["arrival"]["delay"]
                if stop_id in predictions[trip_id]:
                    predictions[trip_id][stop_id].append(
                        (
                            timestamp,
                            predicted_time,
                            prediction_delay,
                        )
                    )
                else:
                    if timestamp - predicted_time > 0:
                        continue

                    predictions[trip_id][stop_id] = [
                        (
                            trip["trip_update"]["timestamp"],
                            predicted_time,
                            prediction_delay,
                        )
                    ]

    except Exception as e:
        print(e)
        continue

    time.sleep(30 - ((time.time() - starttime) % 30))
