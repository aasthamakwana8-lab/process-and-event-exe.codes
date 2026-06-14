import psutil
import time

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


SUSPICIOUS_PROCESSES = [
    "powershell.exe",
    "cmd.exe",
    "wscript.exe",
    "cscript.exe",
    "mshta.exe",
    "rundll32.exe",
    "regsvr32.exe"
]

hash_cache = {}


def collect_process_events():

    events = []

    for process in psutil.process_iter():

        try:

            path = process.exe()

            if path in hash_cache:

                sha256_hash = hash_cache[path]

            else:

                sha256_hash = calculate_sha256(path)

                hash_cache[path] = sha256_hash

            process_name = process.name()

            runtime_minutes = round(
                (
                    time.time()
                    - process.create_time()
                ) / 60,
                2
            )

            privilege = get_privilege(
                process
            )

            is_ps = is_powershell(
                process
            )

            #connections = get_connections(
            #    process.pid
            #)
            connections = []

            risk_score = 0

            alerts = []

            correlation_rules = []

            # PowerShell Detection
            if is_ps:

                risk_score += 20

                alerts.append(
                    "POWERSHELL_ACTIVITY"
                )

            # Privileged Process Detection
            if privilege.upper() in [
                "ADMIN",
                "ADMINISTRATOR",
                "SYSTEM"
            ]:

                risk_score += 25

                alerts.append(
                    "PRIVILEGED_PROCESS"
                )

            # Network Activity Detection
            if len(connections) > 0:

                risk_score += 5

            # Suspicious Binary Detection
            if process_name.lower() in SUSPICIOUS_PROCESSES:

                risk_score += 30

                alerts.append(
                    "SUSPICIOUS_PROCESS"
                )

            # ==========================
            # Correlation Rules
            # ==========================

            # Elevated PowerShell
            if (
                is_ps
                and privilege.upper() in [
                    "ADMIN",
                    "ADMINISTRATOR",
                    "SYSTEM"
                ]
            ):

                correlation_rules.append(
                    "ELEVATED_POWERSHELL"
                )

                risk_score += 20

            # PowerShell Network Activity
            if (
                is_ps
                and len(connections) > 0
            ):

                correlation_rules.append(
                    "POWERSHELL_NETWORK_ACTIVITY"
                )

                risk_score += 15

            # Long Running LOLBin
            if (
                process_name.lower()
                in SUSPICIOUS_PROCESSES
                and runtime_minutes >= 60
            ):

                correlation_rules.append(
                    "LONG_RUNNING_LOLBIN"
                )

                risk_score += 15

            # Privileged LOLBin
            if (
                process_name.lower()
                in SUSPICIOUS_PROCESSES
                and privilege.upper() in [
                    "ADMIN",
                    "ADMINISTRATOR",
                    "SYSTEM"
                ]
            ):

                correlation_rules.append(
                    "PRIVILEGED_LOLBIN"
                )

                risk_score += 20

            # Cap Risk
            risk_score = min(
                risk_score,
                100
            )

            # Risk Classification
            if risk_score >= 80:

                risk_level = "HIGH"

            elif risk_score >= 40:

                risk_level = "MEDIUM"

            else:

                risk_level = "LOW"

            event = {

                "event_id":
                generate_event_id(),

                "timestamp":
                get_timestamp(),

                "pid":
                process.pid,

                "process_name":
                process_name,

                "process_path":
                path,

                "username":
                process.username(),

                "command_line":
                get_commandline(
                    process
                ),

                "sha256_hash":
                sha256_hash,

                "status":
                "RUNNING",

                "priority":
                get_priority(
                    process
                ),

                "privilege":
                privilege,

                "start_time":
                get_start_time(
                    process
                ),

                "runtime_minutes":
                runtime_minutes,

                "ancestors":
                get_ancestor_chain(
                    process
                ),


                "is_powershell":
                is_ps,

                "network_stats":
                #get_network_stats(),
                {},
                
                "network_connections":
                connections,

                "risk": {

                    "score":
                    risk_score,

                    "level":
                    risk_level
                },

                "alerts":
                alerts,

                "correlation_rules":
                correlation_rules
            }

            event.update(
                get_parent_info(
                    process
                )
            )

            events.append(
                event
            )

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