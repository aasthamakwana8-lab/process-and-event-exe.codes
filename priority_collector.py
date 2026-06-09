# collector/priority_collector.py

import psutil

def get_priority(process):

    try:
        return process.nice()

    except:
        return None