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
def append_json(data, filename):

    old_data = []

    if os.path.exists(filename):

        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as file:

                old_data = json.load(file)

        except:

            old_data = []

    old_data.extend(data)

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            old_data,
            file,
            indent=4
        )   