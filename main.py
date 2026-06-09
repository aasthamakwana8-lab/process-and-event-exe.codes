import time

from collector.process_collector import collect_process_events
from utils.json_writer import write_json

known_processes = {}
try:

    while True:

        print("\nCollecting Process Data...")

        data = collect_process_events()
        current_processes = {
            event["pid"]: event
            for event in data
        }
        new_pids = (
            current_processes.keys()
            - known_processes.keys()
        )

        ended_pids = (
            known_processes.keys()
            - current_processes.keys()
        )
        events_to_write = []
        for pid in new_pids:
            process_event = current_processes[pid]
            process_event["event_type"] = (
            "PROCESS_START"
            )
            events_to_write.append(
                process_event
            )
        for pid in ended_pids:
            process_event = known_processes[pid]
            process_event["event_type"] = (
            "PROCESS_END"
            )
            events_to_write.append(
                process_event
            )

        print(
            "Started:",
            len(new_pids)
        )

        print(
            "Ended:",
            len(ended_pids)
        )

        print(
            f"Writing {len(events_to_write)} events..."
        )       

        write_json(
            events_to_write,
            "output/events.json"
        )
        known_processes = current_processes
        print("Updated")

        time.sleep(3)

except KeyboardInterrupt:

    print("\nMonitoring Stopped")
