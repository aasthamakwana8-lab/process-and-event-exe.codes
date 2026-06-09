# collector/privilege_collector.py

def get_privilege(process):

    try:

        username = process.username()

        if "SYSTEM" in username.upper():
            return "SYSTEM"

        elif "ADMIN" in username.upper():
            return "ADMIN"

        else:
            return "USER"

    except:
        return None