import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich import box
from collector.process_collector import collect_process_events
from utils.json_writer import write_json

running_processes = 0
powershell_processes = 0
admin_processes = 0

console = Console()
known_processes = {}

total_start_events = 0
total_end_events = 0

latest_events = []
def generate_dashboard():

    dashboard = Table.grid(
        expand=True
    )

    stats = Table(
        box=box.SIMPLE,
        expand=True
    )

    stats.add_column(
        "Metric"
    )

    stats.add_column(
        "Value",
        justify="right"
    )

    stats.add_row(
        "Running Processes",
        str(running_processes)
    )

    stats.add_row(
        "PowerShell Processes",
        str(powershell_processes)
    )

    stats.add_row(
        "Privileged Processes",
        str(admin_processes)
    )

    stats.add_row(
        "Total Start Events",
        str(total_start_events)
    )

    stats.add_row(
        "Total End Events",
        str(total_end_events)
    )

    recent = Table(
        box=box.SIMPLE,
        expand=True
    )

    recent.add_column(
        "Process"
    )

    recent.add_column(
        "Event"
    )

    recent.add_column(
        "Risk"
    )

    for event in latest_events:

        recent.add_row(

            event.get(
                "process_name",
                "unknown"
            ),

            event.get(
                "event_type",
                "-"
            ),

            event.get(
                "risk",
                {}
            ).get(
                "level",
                "-"
            )
        )

    dashboard.add_row(

        Panel(
            stats,
            title="Process Metrics"
        )
    )

    dashboard.add_row(

        Panel(
            recent,
            title="Recent Activity"
        )
    )

    return Panel(
        dashboard,
        title="PROCESS TELEMETRY AGENT"
    )
with Live(
    generate_dashboard(),
    refresh_per_second=2,
    screen=False
) as live:

    try:

        while True:

            data = collect_process_events()

            current_processes = {
                event["pid"]: event
                for event in data
            }

            # First run = create baseline only
            if not known_processes:

                known_processes = current_processes
                time.sleep(3)

                continue

            # Metrics
            running_processes = len(
                current_processes
            )

            powershell_processes = 0
            admin_processes = 0

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

            # Process lifecycle tracking
            new_pids = (
                current_processes.keys()
                - known_processes.keys()
            )

            ended_pids = (
                known_processes.keys()
                - current_processes.keys()
            )

            events_to_write = []

            # Process Start Events
            for pid in new_pids:

                process_event = current_processes[pid]

                process_event["event_type"] = (
                    "PROCESS_START"
                )

                events_to_write.append(
                    process_event
                )

                total_start_events += 1

                latest_events.insert(
                    0,
                    process_event
                )

                if len(latest_events) > 10:
                    latest_events.pop()

            # Process End Events
            for pid in ended_pids:

                process_event = known_processes[pid]

                process_event["event_type"] = (
                    "PROCESS_END"
                )

                events_to_write.append(
                    process_event
                )

                total_end_events += 1

                latest_events.insert(
                    0,
                    process_event
                )

                if len(latest_events) > 10:
                    latest_events.pop()

            if events_to_write:

                write_json(
                    events_to_write,
                    "output/events.json"
                )

            known_processes = current_processes

            live.update(
                generate_dashboard()
            )
            time.sleep(3)

    except KeyboardInterrupt:

        print(
            "\nMonitoring Stopped"
        )