def get_commandline(process):

    try:
        return " ".join(process.cmdline())

    except:
        return None