import psutil

from collector.hash_collector import calculate_sha256
from collector.parent_chain import get_parent_info
from collector.commandline_collector import get_commandline
from collector.network_collector import get_connections

from collector.priority_collector import get_priority
from collector.privilege_collector import get_privilege
from collector.process_lifecycle import get_start_time
from collector.ancestor_collector import get_ancestor_chain
from collector.powershell_collector import is_powershell
from collector.network_stats_collector import get_network_stats

from utils.eventid_util import generate_event_id
from utils.timestamp_util import get_timestamp


def collect_process_events():

    events = []

    for process in psutil.process_iter():

        try:

            path = process.exe()

            event = {

                "event_id": generate_event_id(),

                "timestamp": get_timestamp(),

                "pid": process.pid,

                "process_name": process.name(),

                "process_path": path,

                "username": process.username(),

                "command_line": get_commandline(process),

                "sha256_hash": calculate_sha256(path),

                "status": "RUNNING",

                "priority":
                get_priority(process),

                "privilege":
                get_privilege(process),

                "start_time":
                get_start_time(process),

                "ancestors":
                get_ancestor_chain(process),

                "is_powershell":
                is_powershell(process),

                "network_stats":
                get_network_stats(),

                "network_connections":
                get_connections(process.pid)

            }

            event.update(
                get_parent_info(process)
            )

            events.append(event)

        except Exception as e:

            try:

                events.append({

                    "event_id":
                    generate_event_id(),

                    "timestamp":
                    get_timestamp(),

                    "pid":
                    process.pid,

                    "process_name":
                    process.name(),

                    "status":
                    "ACCESS_DENIED",

                    "error":
                    str(e)

                })

            except:

                pass

    return events