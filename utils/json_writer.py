import json
import os

def write_json(data, filename):

    if not data:
        return

    os.makedirs(
        os.path.dirname(filename),
        exist_ok=True
    )

    with open(
        filename,
        "a",
        encoding="utf-8"
    ) as file:

        for event in data:

            file.write(
                json.dumps(event)
            )

            file.write("\n")