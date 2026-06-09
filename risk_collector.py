def get_risk_score(process):

    try:

        risky = [

            "powershell.exe",
            "cmd.exe",
            "wscript.exe",
            "cscript.exe",
            "rundll32.exe",
            "mshta.exe"

        ]

        if process.name().lower() in risky:
            return 80

        return 10

    except:
        return 0