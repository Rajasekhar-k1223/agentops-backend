from scapy.all import ARP, Ether, srp
import socket
import nmap


def scan_network(ip_range):
    # Create ARP packet to discover devices
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range)
    result = srp(packet, timeout=3, verbose=False)[0]

    nm = nmap.PortScanner()
    devices = []

    for sent, received in result:
        ip = received.psrc
        mac = received.hwsrc

        # Get hostname
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except socket.herror:
            hostname = "unknown"

        # Use nmap to scan for vendor and OS
        try:
            nm.scan(hosts=ip, arguments="-O")
            vendor = "unknown"
            os_guess = "unknown"

            # Extract vendor (if available)
            if 'macaddress' in nm[ip] and 'vendor' in nm[ip]['macaddress']:
                vendor = list(nm[ip]['macaddress']['vendor'].values())[0]

            # Extract OS guess
            if 'osmatch' in nm[ip] and nm[ip]['osmatch']:
                os_guess = nm[ip]['osmatch'][0]['name']
        except Exception as e:
            vendor = "unknown"
            os_guess = "unknown"

        devices.append({
            "ip": ip,
            "mac": mac,
            "hostname": hostname,
            "vendor": vendor,
            "os": os_guess
        })

    return devices
