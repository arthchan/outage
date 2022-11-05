#!/usr/bin/env python3
"""Fill in the form for system outage."""

# Import libraries
from datetime import datetime
import os
import json
import sys

# Get current timestamp
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# Load configurations
try:
    # Open configuration file
    with open("config.json") as json_file:

        # Load data in configuration file
        config = json.load(json_file)

        # Read variables
        form_folder_path = "C:/Users/" + os.getlogin(
            ) + config["form_folder_path"]

except BaseException as e:
    # Print error message on console
    print('[' + dt_string + "] Unable to load the configuration file: ",
          str(e))
    sys.exit()

# Input target asset
form = input("Form Name = ") + ".txt"

print(form_folder_path + '/' + form)

# Check if form exists
if form not in os.listdir(form_folder_path):
    print('[' + dt_string + "] Unable to find the target form!")
    sys.exit()

# Read form
with open(form_folder_path + '/' + form) as f:
    lines = f.readlines()
    print(lines)
