import psutil
import socket

def get_connections(pid):

    connections = []

    try:

        for conn in psutil.net_connections():

            if conn.pid == pid:

                domain = None

                if conn.raddr:

                    try:
                        domain = socket.gethostbyaddr(
                            conn.raddr.ip
                        )[0]

                    except:
                        pass

                connections.append({

                    "local_ip":
                    conn.laddr.ip if conn.laddr else None,

                    "local_port":
                    conn.laddr.port if conn.laddr else None,

                    "remote_ip":
                    conn.raddr.ip if conn.raddr else None,

                    "remote_port":
                    conn.raddr.port if conn.raddr else None,

                    "domain":
                    domain,

                    "status":
                    conn.status

                })

    except:
        pass

    return connections