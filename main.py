
import time

from collector.process_collector import collect_process_events
from utils.json_writer import write_json

previous_pids = set()

try:

    while True:

        print("\nCollecting Process Data...")

        data = collect_process_events()

        current_pids = set()

        for event in data:

            current_pids.add(
                event["pid"]
            )

        new_processes = (
            current_pids -
            previous_pids
        )

        ended_processes = (
            previous_pids -
            current_pids
        )

        print(
            "Started:",
            len(new_processes)
        )

        print(
            "Ended:",
            len(ended_processes)
        )

        previous_pids = current_pids

        print(
            f"Writing {len(data)} events..."
        )

        write_json(
            data,
            "output/events.json"
        )

        print("Updated")

        time.sleep(3)

except KeyboardInterrupt:

    print(
        "\nMonitoring Stopped"
    )