import sys
import pyfiglet

ascii_banner = pyfiglet.figlet_format("FILE    SCANNER")
print(ascii_banner)

# Receive args and paths from file execution location & command line args
loc = sys.path[0]
args = sys.argv

# Create dict, and process file name
line_data = dict()

print('-' * 80, end="\n\n")
if len(args) < 2:
    print(" No file was given as an argument, searching for default file name ('test.txt') ", end="\n\n")
    print('-' * 80, end="\n\n")

file_name = 'test.txt' if len(args) < 2 else args[1]

# Open file and process the data
with open(f"{loc}/{file_name}", "r") as file:
    lines = file.readlines()
    for l in lines:
        to_add = l.strip()
        if len(to_add) != 0:
            if to_add not in line_data.keys():
                line_data[to_add] = 1
            else:
                line_data[to_add] += 1
        else:
            print("Tried to process line, but line was empty (len(line) == 0)")

for data in line_data.keys():
    print(f"Character: '{data}', Frequency: {line_data[data]}")