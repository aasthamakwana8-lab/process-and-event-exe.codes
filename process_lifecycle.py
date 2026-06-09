# collector/process_lifecycle.py

from datetime import datetime

def get_start_time(process):

    try:
        return datetime.fromtimestamp(
            process.create_time()
        ).isoformat()

    except:
        return None