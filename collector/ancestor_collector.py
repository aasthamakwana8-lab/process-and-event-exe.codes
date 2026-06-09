def get_ancestor_chain(process):

    ancestors = []

    try:

        parent = process.parent()

        while parent:

            ancestors.append({

                "pid": parent.pid,

                "name": parent.name()

            })

            parent = parent.parent()

    except:
        pass

    return ancestors