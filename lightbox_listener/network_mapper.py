import socket
import subprocess


def get_local_ips():
    """
    Get all local ips returned by arp -a

    :return: List[str] ips on local network
    """
    hostname = socket.getfqdn()
    ip_address = socket.gethostbyname_ex(hostname)[2][1]
    cmd = subprocess.run(["arp", "-a"], capture_output=True)
    line = str(cmd).split(",")
    format_line = line[3].replace("stdout=b'", "").replace("\\n", "\n")
    raw_ips = format_line.split("on wlan0")

    ips = []
    for raw_ip_line in raw_ips:
        for y in raw_ip_line.strip().splitlines():
            if y.strip().startswith(ip_address[0:6]):
                ips.append(y.strip().split()[0])
    print(ips)
    return ips


async def get_all_ips(ignored=None):
    if ignored is None:
        ignored = {}
    hostname = socket.getfqdn()
    ip_address = socket.gethostbyname_ex(hostname)[2][1]
    cmd = subprocess.run(["arp", "-a"], capture_output=True)
    a = str(cmd).split(",")
    b = a[3].replace("stdout=b'", "").replace("\\n", "\n")
    c = b.split("on wlan0")
    spl = ip_address.split(".")[0:-1]

    ips_out = []
    for x in range(61):
        ip = spl + [str(x)]
        out = ".".join(ip)
        ips_out.append(out)

    for x in ips_out:
        if x in ignored:
            ips_out.remove(x)
    return ips_out


if __name__ == '__main__':
    print(get_all_ips())
