# collector/file_activity_collector.py

import os
from datetime import datetime

def get_recently_modified_files():

    modified = []

    try:

        for root, dirs, files in os.walk("C:\\"):

            for file in files:

                path = os.path.join(root,file)

                try:

                    modified_time = os.path.getmtime(path)

                    modified.append({

                        "file": path,

                        "modified_time":
                        datetime.fromtimestamp(
                            modified_time
                        ).isoformat()

                    })

                except:
                    pass

    except:
        pass

    return modified[:100]