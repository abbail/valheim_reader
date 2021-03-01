from valheim_reader import ValheimReader
from os import path
import glob
import ntpath

def yes_or_no(question):
    while True:
        reply = input(question + " (y/n): ").strip().lower()
        if reply == "y":
            return True
        if reply == "n":
            return False

def choose_world_file():
    fodler = path.expandvars(r"%appdata%\\..\\LocalLow\\IronGate\\Valheim\\worlds\\*.db")

    world_files = glob.glob(fodler)

    if len(world_files) == 1:
        return world_files[0]

    prompt = ""
    int_response = -1

    for i in range(len(world_files)):
        world_file_name = ntpath.basename(world_files[i])
        prompt = "{}{}: {}\n".format(prompt, i + 1, world_file_name.replace(".db", "")) #.replace("8uuuuD", "SomeWorld"))

    prompt = "{}Select a world to read (1-{}): ".format(prompt, len(world_files))

    while int_response < 0:
        response = input(prompt)
        try:
            int_response = int(response)
            if int_response > len(world_files) or int_response == 0:
                int_response = -1
        except ValueError:
            continue

    return world_files[int_response - 1]

file_path = choose_world_file()

vendor_only = False
vendor_only = yes_or_no("Do you only want the coordinates of the vendor?")

valheim_reader = ValheimReader(file_path, vendor_only)

input("Press enter to exit...")
