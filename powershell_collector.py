# collector/powershell_collector.py

def is_powershell(process):

    try:

        name = process.name().lower()

        return (
            "powershell" in name
            or
            "pwsh" in name
        )

    except:
        return False