import sys
import os
import ctypes
import re
import argparse
from pathlib import Path

OPERANDS = ("add", "remove", "erase", "help", "show")

start_marker = "# BEGIN"
end_marker = "# END"

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
    """Util Function to validate operations"""
    if operand not in OPERANDS:
        exit("Invalid operation provided")

def show_domains(host_path):
    """Display all domains from all blocks managed by HostBlock"""
    blocks = []
    domains = []
    skip = True
    t = []
    with open(host_path, 'r') as file:
        for line in file:
            if end_marker in line:
                skip = True
                domains.append(t)
                t = []
            if not skip:
                t.append(line.split(" ")[1])
            if start_marker in line:
                blocks.append(line.strip("\n").split(" ")[2:])
                skip = False
    
    output_str = ""
    for index, b in enumerate(blocks):
        output_str += f"""Block {"".join(bb for bb in b)}:\n"""
        for db in domains[index]:
            output_str += f"Domain: {db}\n"
        output_str += "\n"
    return output_str[:-2]

def add_domain(domains, host_path, block_name=None):
    domains = set(domains)
    """Add domain to blacklist"""
    if block_name is None:
        block_name = "HOSTBLOCK"
    try: # Spot the script block or create it before appending anything
        add = False
        hosts_etc_data = load_hosts(host_path)
        
        # Remove \n from line to find the start and end marker idx easier
        temporary = []
        for s in hosts_etc_data:
            if "BEGIN" in s or "END" in s:
                temporary.append(s.replace('\n', ''))
            else:
                temporary.append(s)
        hosts_etc_data = temporary[::]

        start_marker_idx = hosts_etc_data.index(start_marker + " " + block_name)
        end_marker_idx = hosts_etc_data.index(end_marker + " " + block_name)

        # Add \n to line to make sure that when file is overwritten the format is still valid
        temporary = []
        for s in hosts_etc_data:
            if "BEGIN" in s or "END" in s:
                temporary.append(s + "\n")
            else:
                temporary.append(s)
        hosts_etc_data = temporary[::]
        
        block = hosts_etc_data[start_marker_idx : end_marker_idx + 1]
        blocks = [b.split()[1] for b in block if b.strip()]
    except ValueError as e: # Βαράει αν δεν υπάρχει ήδη block, άρα δημιούργησε το
        add = True
        blocks = []
    
    # Finally, execute operations
    mode = "a" if add else "w"
    with open(host_path, mode) as f:
        new_entries = []
        for domain in domains:
            if "www" in domain:
                domain = domain.replace("www.", "")
            if domain not in blocks:
                new_entries.append(f"127.0.0.1 {domain} www.{domain}\n")
        if add:
            f.write("\n")
            f.write(f"\n{start_marker} {block_name}\n") # ΔΕΝ ΞΕΡΩ ΓΙΑΤΙ ΤΟ f.write("\n\n{start_marker}") ΔΕΝ ΕΙΝΑΙ ΤΟ ΙΔΙΟ ΚΑΙ ΑΝΑΓΚΑΣΤΗΚΑ ΝΑ ΤΟ ΚΑΝΩ ΕΤΣΙ
            for domain in new_entries:
                    f.write(domain)
            f.write(f"{end_marker} {block_name}")
        else:
            hosts_etc_data[end_marker_idx:end_marker_idx] = new_entries
            f.writelines(hosts_etc_data)

def remove_domain(domains, host_path, block_name=None):
    """Remove domain from the blacklist"""
    try:
        hosts_etc_data = load_hosts(host_path)
        # Remove \n from line to find the start and end marker idx easier
        temporary = []
        for s in hosts_etc_data:
            if "BEGIN" in s or "END" in s:
                temporary.append(s.replace('\n', ''))
            else:
                temporary.append(s)
        hosts_etc_data = temporary[::]

        start_marker_idx = hosts_etc_data.index(f"{start_marker} {block_name}")
        end_marker_idx = hosts_etc_data.index(f"{end_marker} {block_name}")

        # Add \n to line to make sure that when file is overwritten the format is still valid
        temporary = []
        for s in hosts_etc_data:
            if "BEGIN" in s or "END" in s:
                temporary.append(s + "\n")
            else:
                temporary.append(s)
        hosts_etc_data = temporary[::]

        datablock = hosts_etc_data[start_marker_idx+1:end_marker_idx]
        to_keep = []
        for domain in domains:
            for data_block in datablock:
                if domain in data_block:
                    continue
                
                to_keep.append(data_block)

        hosts_etc_data[start_marker_idx+1:end_marker_idx] = to_keep
        with open(host_path, "w") as f:
            f.writelines(hosts_etc_data)
    except Exception as e: 
        exit(f"Critical Error Occured {e}")

# TO-DO: FIX WITH BLOCKS
def erase(host_path):
    """Erase all HostBlock records from etc/hosts"""
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

    # add MYBLOCK DOMAINS
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("domains")
    add_parser.add_argument("block")

    # remove <domain>
    remove_parser = subparsers.add_parser("remove")
    remove_parser.add_argument("domains")
    remove_parser.add_argument("block")

    # erase  (no additional arguments)
    erase_parser = subparsers.add_parser("erase")
    
    # help  (no additional arguments)
    help_parser = subparsers.add_parser("help")
    
    # show  (no additional arguments)
    show_parser = subparsers.add_parser("show")

    # test  (no additional arguments)
    test_parser = subparsers.add_parser("test")

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

    # Operation Actions
    if operation == "add":
        domain_q = args.domains.split(",")
        block_name = args.block
        domain_q = validate_domain(domain_q)
        if len(domain_q) == 0:
            exit("No valid domains were given")
        add_domain(domain_q, host_path, block_name=block_name)
    elif operation == "remove":
        domain_q = args.domains.split(",")
        block_name = args.block
        domain_q = validate_domain(domain_q)
        if len(domain_q) == 0:
            exit("No valid domains were given")
        remove_domain(domain_q, host_path, block_name=block_name)
    elif operation == "erase":
        erase(host_path)
    elif operation == "show":
        print(show_domains(host_path))
    elif operation == "help":
        print("""Usage: sudo python host_block.py <command> [subargs]

Commands:
  add     <domain>  Add the given domain(s) to the list. Case insensitive, comma separated.
  remove  <domain>  Remove the given domain(s) from the list. Case insensitive, comma separated.
  erase             Erase all entries
  show              Shows all blacklisted domains  
  help              Displays the help menu

Examples:
  sudo python host_block.py add test.org,example.org,twitter.com
  sudo python host_block.py remove example.org,test.org
  sudo python host_block.py erase
""")