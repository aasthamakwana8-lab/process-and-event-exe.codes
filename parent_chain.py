def get_parent_info(process):

    try:

        parent = process.parent()

        return {
            "parent_pid": parent.pid,
            "parent_process_name": parent.name()
        }

    except:

        return {
            "parent_pid": None,
            "parent_process_name": None
        }