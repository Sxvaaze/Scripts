import sys
import os
import ctypes
import re
import argparse
from pathlib import Path

def check_admin():
    """Util Function to check if user is administrator/root . Performing write operations on etc/hosts requires admin/root privileges"""
    if sys.platform in ("linux", "linux2", "darwin"):
        if os.geteuid() != 0:
            exit("You must run this script as root")
    elif sys.platform == "win32":
        if not ctypes.windll.shell32.IsUserAnAdmin():
            exit("You must run this script as administrator")

def load_hosts(file_path):
    """Util Function used to load data of etc/hosts file to make sure there are no duplicates """
    if not file_path.exists():
        return []
    with file_path.open("r") as f:
        lines = f.readlines()
    return lines

def validate_domain(domains):
    """Util Function to filter out non valid domains"""
    DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63}$"
    )

    valid_domains = [d for d in domains if DOMAIN_REGEX.match(d)]
    return valid_domains

def validate_operation(operand):
    if operand not in ("add", "remove", "erase", "help"):
        exit("Invalid operation provided")


def add_domain(domains, host_path):
    # Spot the script block or create it before appending anything
    start_marker = "# BEGIN HOSTSBLOCK\n"
    end_marker = "# END HOSTSBLOCK\n"

    try:
        add = False
        hosts_etc_data = load_hosts(host_path)
        start_marker_idx = hosts_etc_data.index(start_marker)
        end_marker_idx = hosts_etc_data.index(end_marker)
        block = hosts_etc_data[start_marker_idx : end_marker_idx + 1]
        blocks = [b.split()[1] for b in block if b.strip()]
    except ValueError: # Βαράει αν δεν υπάρχει ήδη block, άρα δημιούργησε το
        add = True
        blocks = []
    
    # Finally, execute operations
    mode = "a" if add else "w"
    with open(host_path, mode) as f:
        if add:
            f.write("\n")
            f.write(f"\n{start_marker}") # ΔΕΝ ΞΕΡΩ ΓΙΑΤΙ ΤΟ f.write("\n\n{start_marker}") ΔΕΝ ΕΙΝΑΙ ΤΟ ΙΔΙΟ ΚΑΙ ΑΝΑΓΚΑΣΤΗΚΑ ΝΑ ΤΟ ΚΑΝΩ ΕΤΣΙ
            for domain in domains:
                if domain not in blocks:
                    f.write(f"127.0.0.1 {domain} www.{domain} \n")
            f.write(end_marker)
        else:
            new_entries = [f"127.0.0.1 {d} www.{d}\n" for d in domains if d not in blocks]
            hosts_etc_data[end_marker_idx:end_marker_idx] = new_entries
            f.writelines(hosts_etc_data)

def remove_domain(domains, host_path):
    try:
        for d in domains:
            with open(host_path, 'r', encoding='utf-8') as f:
                for lineno, line in enumerate(f, start=1):
                    if d in line:
                        s_idx = lineno
                        break
            
            hosts_etc_data = load_hosts(host_path)
            hosts_etc_data[s_idx-1:s_idx] = ""

        with open(host_path, "w") as f:
            f.writelines(hosts_etc_data)
    except Exception as e: 
        exit(f"Critical Error Occured")

def erase(host_path):
    start_marker = "# BEGIN HOSTSBLOCK\n"
    end_marker = "# END HOSTSBLOCK\n"
    try:
        hosts_etc_data = load_hosts(host_path)
        start_marker_idx = hosts_etc_data.index(start_marker)
        end_marker_idx = hosts_etc_data.index(end_marker)

        hosts_etc_data[start_marker_idx:end_marker_idx + 1] = ""
        with open(host_path, "w") as f:
            f.writelines(hosts_etc_data)
    except ValueError: 
        exit("Critical Error Occured")

if __name__ == "__main__":
    check_admin()

    # CLI argument
    parser = argparse.ArgumentParser(description='HostBlock Script')

    subparsers = parser.add_subparsers(dest="operation", required=True)

    # add <domain>
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("domains")

    # remove <domain>
    remove_parser = subparsers.add_parser("remove")
    remove_parser.add_argument("domains")

    # erase  (no additional arguments)
    erase_parser = subparsers.add_parser("erase")
    
    # help  (no additional arguments)
    erase_parser = subparsers.add_parser("help")

    args = parser.parse_args()

    operation = args.operation.lower()
    validate_operation(operation)

    # Find where etc/hosts is
    if sys.platform == "linux" or sys.platform == "linux2":
        host_path = Path("/etc/hosts")
    elif sys.platform == "darwin":
        host_path = Path("/etc/hosts")
    elif sys.platform == "win32":
        host_path = Path("C:/Windows/System32/drivers/etc/hosts")
    else:
        exit("OS not supported")

    if operation == "add":
        domain_q = args.domains.split(",")
        domain_q = validate_domain(domain_q)
        if len(domain_q) == 0:
            exit("No valid domains were given")
        add_domain(domain_q, host_path)
    elif operation == "remove":
        domain_q = args.domains.split(",")
        domain_q = validate_domain(domain_q)
        if len(domain_q) == 0:
            exit("No valid domains were given")
        remove_domain(domain_q, host_path)
    elif operation == "erase":
        erase(host_path)
    elif operation == "help":
        print("""Usage: sudo python host_block.py <command> [subargs]

Commands:
  add     <domain>  Add the given domain(s) to the list. Case insensitive, comma separated.
  remove  <domain>  Remove the given domain(s) from the list. Case insensitive, comma separated.
  erase             Erase all entries
  help              Displays the help menu

Examples:
  sudo python host_block.py add test.org,example.org,twitter.com
  sudo python host_block.py remove example.org,test.org
  sudo python host_block.py erase
""")