import mmap
import struct
import os
import sys

class ValheimReader:
    def __init__(self, file_path, vendor_only = False):
        data_index = -1

        with open(file_path, mode='rb') as self.file_buffer:
            mmap_file = mmap.mmap(self.file_buffer.fileno(), length=0, access=mmap.ACCESS_READ)

            # used to use the start temple as the initial offset but I expanded my reverse enginerring to include progression
            # data_index = mmap_file.find(b"\x0bStartTemple")
            
            # values used to find initial offset
            search_bytes = b"\x63\x00\x00\x00\x16\x00\x00\x00"

            # maybe someone else can come up with a better way to find the starting offsets
            data_index = mmap_file.find(search_bytes)

            # if you don't find it, bail
            if data_index == -1:
                sys.exit("Unknown file format.")

            # skip those initial bytes that aren't part of the progression record set
            data_index = data_index + len(search_bytes)

            self.file_buffer.seek(data_index)

            # print progression
            progression = self.read_progression_records()

            self.print_progression(progression)

            # not sure what this byte is ??
            self.file_buffer.seek(1, os.SEEK_CUR)

            # read location data
            locations = self.read_location_records()

            # print all stored locations
            self.print_location(locations, vendor_only)
    
    def print_progression(self, progression):
        print("Progression:")

        # loop over progression events and print them
        for i in range(len(progression)):
            print("    {}. {}".format(i + 1, progression[i]))

    def print_location(self, locations, vendor_only = False):
        print("Locations:")
         # loop over all stored locations
        for location in locations:
            # print all of them or only the vendor if we are running that way
            if not vendor_only or vendor_only and location["name"] == "Vendor_BlackForest":
                print("    {} ({}, {}, {})".format(location["name"], location["x"], location["y"], location["z"]))

    def read_progression_records(self):
        progression = []

        # read progression record count
        total_records = int.from_bytes(self.file_buffer.read(1), "little")

        # skip three nulls
        self.file_buffer.seek(3, os.SEEK_CUR)

        # loop through records
        for _ in range(total_records):
            # read the location record from the current offset
            progression_record = self.read_progression_record()
            
            # save it to our list
            progression.append(progression_record)

        return progression

    def read_progression_record(self):
        # first byte is the length of the name
        name_length = int.from_bytes(self.file_buffer.read(1), "little")

        return self.file_buffer.read(name_length).decode("UTF-8")


    def read_location_records(self):
        locations = []

        # read location record count
        total_records = int.from_bytes(self.file_buffer.read(2), "little")
        
        # I had a null here, not sure what it is ??
        self.file_buffer.seek(1, os.SEEK_CUR)

        # loop through records
        for _ in range(total_records):
            # read the location record from the current offset
            location = self.read_location_record()
            
            # save it to our list
            locations.append(location)

        return locations

    # reads a location record at the current file offset
    def read_location_record(self):
        # not sure what this byte is for.  skipping it
        self.file_buffer.seek(1, os.SEEK_CUR)

        # first byte is the length of the name
        name_length = int.from_bytes(self.file_buffer.read(1), "little")

        # seek backwards so we can get the whole record in one struct
        self.file_buffer.seek(-2, os.SEEK_CUR)

        # convert struct to a dictionary for easier use later
        return self.bytes_to_location(name_length, self.file_buffer.read(name_length + 14))

    # takes bytes and converts them to a location struct
    def bytes_to_location(self, name_length, bytes):
        # byte packed format of data
        pack_format = "< ? c {}s f f f".format(name_length)

        # unpack the bytes
        unpacked = struct.unpack(pack_format, bytes)

        # convert struct to a dictionary for easier use later
        return {
            "name": unpacked[2].decode("UTF-8"),
            "x": unpacked[3],
            "y": unpacked[5],
            "z": unpacked[4]
        }
