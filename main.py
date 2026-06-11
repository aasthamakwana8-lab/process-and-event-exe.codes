import time
import json

from collector.process_collector import collect_process_events
from utils.json_writer import (
    write_json,
    append_json
)

known_processes = {}

total_start_events = 0
total_end_events = 0

latest_events = []

try:

    while True:

        data = collect_process_events()

        current_processes = {
            event["pid"]: event
            for event in data
        }

        # First Run → Baseline
        if not known_processes:

            known_processes = current_processes

            print(
                f"Baseline created with "
                f"{len(current_processes)} processes"
            )

            time.sleep(1)

            continue

        # Process Metrics
        running_processes = len(
            current_processes
        )

        powershell_processes = 0
        admin_processes = 0

        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0

        alerted_processes = 0

        for process in current_processes.values():

            if process.get(
                "is_powershell",
                False
            ):
                powershell_processes += 1

            if process.get(
                "privilege",
                ""
            ).upper() in [
                "ADMIN",
                "ADMINISTRATOR",
                "SYSTEM"
            ]:
                admin_processes += 1

            risk_level = process.get(
                "risk",
                {}
            ).get(
                "level",
                "LOW"
            )

            if risk_level == "HIGH":

                high_risk_count += 1

            elif risk_level == "MEDIUM":

                medium_risk_count += 1

            else:

                low_risk_count += 1

            if process.get(
                "alerts",
                []
            ):
                alerted_processes += 1

        # Lifecycle Detection
        new_pids = (
            current_processes.keys()
            - known_processes.keys()
        )

        ended_pids = (
            known_processes.keys()
            - current_processes.keys()
        )

        events_to_write = []
        flagged_events = []
        correlation_events = []
        # PROCESS START
        for pid in new_pids:

            process_event = current_processes[pid]

            process_event["event_type"] = (
                "PROCESS_START"
            )

            events_to_write.append(
                process_event
            )
            if process_event.get("alerts"):
                flagged_events.append(process_event) 
            total_start_events += 1

            if process_event.get("correlation_rules"):
                correlation_events.append(process_event)
            latest_events.insert(
                0,
                {
                    "process_name":
                    process_event.get(
                        "process_name"
                    ),

                    "event_type":
                    "PROCESS_START",

                    "risk":
                    process_event.get(
                        "risk",
                        {}
                    )
                }
            )

        # PROCESS END
        for pid in ended_pids:

            process_event = known_processes[pid]

            process_event["event_type"] = (
                "PROCESS_END"
            )

            events_to_write.append(
                process_event
            )
            if process_event.get("alerts"):
                flagged_events.append(process_event)    
            total_end_events += 1

            if process_event.get("correlation_rules"):
                correlation_events.append(process_event)   

            latest_events.insert(
                0,
                {
                    "process_name":
                    process_event.get(
                        "process_name"
                    ),

                    "event_type":
                    "PROCESS_END",

                    "risk":
                    process_event.get(
                        "risk",
                        {}
                    )
                }
            )

        # Keep only latest 10 events
        latest_events = latest_events[:10]

        # Write lifecycle events only
        if events_to_write:

            write_json(
                events_to_write,
                "output/events.json"
            )
        if flagged_events:
            append_json(
                flagged_events,
                "output/flagged_events.json"
            )
        if correlation_events:
            append_json(
                correlation_events,
                "output/correlation_events.json"
            )
        # Metrics JSON
        metrics = {

            "timestamp": time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "running_processes":
            running_processes,

            "powershell_processes":
            powershell_processes,

            "privileged_processes":
            admin_processes,

            "total_start_events":
            total_start_events,

            "total_end_events":
            total_end_events,

            "high_risk_processes":
            high_risk_count,

            "medium_risk_processes":
            medium_risk_count,

            "low_risk_processes":
            low_risk_count,

            "alerted_processes":
            alerted_processes,

            "recent_events": [

                {
                    "process":
                    event["process_name"],

                    "event":
                    event["event_type"],

                    "risk":
                    event.get(
                        "risk",
                        {}
                    ).get(
                        "level",
                        "-"
                    )
                }

                for event in latest_events
            ]
        }

        with open(
            "output/metrics.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                metrics,
                file,
                indent=4
            )

        known_processes = current_processes

        print(
            f"[{metrics['timestamp']}] "
            f"Running={running_processes} | "
            f"Started={len(new_pids)} | "
            f"Ended={len(ended_pids)} | "
            f"alerted={alerted_processes}"
        )

        time.sleep(1)

except KeyboardInterrupt:

    print(
        "\nMonitoring Stopped"
    )