import psutil

def get_network_stats():

    try:

        io = psutil.net_io_counters()

        return {

            "bytes_sent": io.bytes_sent,

            "bytes_received": io.bytes_recv

        }

    except:

        return {

            "bytes_sent": 0,

            "bytes_received": 0

        }