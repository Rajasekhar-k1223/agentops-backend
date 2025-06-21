from scapy.all import ARP, Ether, srp
import socket
import nmap


def scan_network(ip_range):
    # Discover devices using ARP
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range)
    result = srp(packet, timeout=3, verbose=False)[0]

    nm = nmap.PortScanner()
    devices = []

    for sent, received in result:
        ip = received.psrc
        mac = received.hwsrc

        # Get hostname via reverse DNS
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except socket.herror:
            hostname = "unknown"

        # Default values
        vendor = "unknown"
        os_guess = "unknown"
        os_accuracy = "0%"

        try:
            nm.scan(hosts=ip, arguments="-O")

            if ip in nm.all_hosts():
                # Extract OS details
                os_matches = nm[ip].get("osmatch", [])
                if os_matches:
                    os_guess = os_matches[0].get("name", "unknown")
                    os_accuracy = os_matches[0].get("accuracy", "0") + "%"

                # Extract MAC vendor
                if 'addresses' in nm[ip] and 'mac' in nm[ip]['addresses']:
                    mac_addr = nm[ip]['addresses']['mac']
                    vendor = nm[ip].get("vendor", {}).get(mac_addr, "unknown")

        except Exception as e:
            print(f"Nmap scan failed for {ip}: {e}")

        devices.append({
            "ip": ip,
            "mac": mac,
            "hostname": hostname,
            "vendor": vendor,
            "os": os_guess,
            "os_accuracy": os_accuracy
        })

    return devices
