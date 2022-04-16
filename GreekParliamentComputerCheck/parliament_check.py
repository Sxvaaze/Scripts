import ipaddress
import pyfiglet
import sys

ip = "195.251.32.0"
mask = 22
mask_bin = ""

s = mask % 8
first = True
for i in range(1,5):
    if mask - i * 8 < 0:
        const = ""
        if first:
            for j in range(s):
                const += "1"
            for j in range(8 - s):
                const += "0"
        else:
            for j in range(8):
                const += "0"

        first = False
        mask_bin += str(int(const, base=2))
        
    else:
        mask_bin += "255"

    if i != 4:
        mask_bin += "."

host = ipaddress.IPv4Address(ip)
net = ipaddress.IPv4Network(ip + '/' + mask_bin, False)
network_address = ipaddress.IPv4Address(int(host) & int(net.netmask))
broadcast_address = net.broadcast_address

ascii_banner = pyfiglet.figlet_format("GREEK PARLIAMENT IP CHECKER")
print(ascii_banner)
args = sys.argv
if len(args) == 2:
    ip_to_search = str(args[1])    
    if ip_to_search > str(network_address) and ip_to_search < str(broadcast_address):
        print(f"  " * 20 + f"The IP {ip_to_search} belongs to a greek parliament computer.")
    else:
        print(f"  " * 20 + f"The IP {ip_to_search} does not belong to a greek parliament comptuer.")
else:
    print(" " * 25 + "There was an error whilst trying to run the script. No IP Address was given as a parameter.")





