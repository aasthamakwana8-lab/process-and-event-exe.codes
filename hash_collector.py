import hashlib

def calculate_sha256(filepath):

    try:

        sha256 = hashlib.sha256()

        with open(filepath, "rb") as file:

            while True:

                chunk = file.read(4096)

                if not chunk:
                    break

                sha256.update(chunk)

        return sha256.hexdigest()

    except:
        return None