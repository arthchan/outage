#!/usr/bin/env python3
"""Fill in the form for system outage."""

# Import libraries
from datetime import datetime
import os
import json
import sys
import logic


# Function for loading configurations
def load_configs():
    """Load configurations."""
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
        # Get current timestamp
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        # Print error message on console
        print(
            '[' + dt_string + "] Unable to load the configuration file: ",
            str(e))
        sys.exit()

    return form_folder_path


# Function for completing outage form
def complete_outage_form(target, form, form_folder_path):
    """Complete outage form."""
    # Initialise dictionaries to store query results
    type_dict = dict()
    status_dict = dict()

    # Check if form exists
    if form not in os.listdir(form_folder_path):
        # Get current timestamp
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        # Print error message on console
        print('[' + dt_string + "] Unable to find the target form!")
        sys.exit()

    # Read form
    with open(form_folder_path + '/' + form) as f:
        lines = f.readlines()

    # Close form
    f.close()

    # Load configurations and graphs for running queries
    graph, POINT_OF_ISOLATION = logic.load_configs_and_graphs()

    # Open output text file for writing
    with open("output.txt", 'w') as f:

        # Iterate through all lines
        for ln, line in enumerate(lines):

            # Drop "\n" at the end of line
            line = line.replace("\n", "", -1)

            # Search for indice of brackets
            open_b = line.find('{')
            close_b = line.find('}')

            # Initialise item flag and answer memory
            item_flag = False
            ans_memory = []

            # Fill in the brackets
            while open_b != -1 and close_b != -1:

                # Extract parameters
                param = line[open_b+1:close_b].split(",")

                # Run query
                ans_list, rch_list, asd_list = logic.run_logic(
                    graph, int(param[0]), target, POINT_OF_ISOLATION)

                # Store asset details in dictionaries
                for asset, type, status in asd_list:
                    type_dict.setdefault(asset, type)
                    status_dict.setdefault(asset, status)

                # Initialise list to record all answers
                answer_list = []

                # Search for type in asset list if target is a POI
                if param[1] in POINT_OF_ISOLATION:
                    for x in ans_list[int(param[0])-1][1]:
                        if type_dict[x] == param[1]:
                            answer_list.append(x)

                # Search for type in reached list if target is not a POI
                else:
                    for x in rch_list[int(param[0])-1][1]:
                        if x == target:
                            continue

                        elif type_dict[x] == param[1]:
                            answer_list.append(x)

                        else:
                            pass

                # If answer mode is list (l)
                if param[2] == 'l':
                    line = line.replace(line[open_b:close_b+1], str(
                        answer_list)[1:-2].replace("'", ''))

                # If answer mode is quanity (q)
                elif param[2] == 'q':
                    line = line.replace(
                        line[open_b:close_b+1], str(len(answer_list)))

                # If answer mode is item (i)
                if param[2] == 'i':
                    pos_memory = line[open_b:close_b+1]
                    ans_memory = answer_list
                    item_flag = True

                else:
                    pass

                # Find next pair of brackets
                open_b = line.find('{', close_b+1)
                close_b = line.find('}', close_b+1)

            # If answer mode is item (i)
            if item_flag:
                for i in ans_memory:
                    line_i = line.replace(pos_memory, i)

                    # Write lines to output file
                    for ln in line_i.split(';'):
                        f.write(ln)
                        f.write("\n")

                    f.write('\n')

                # Reset item flag
                item_flag = False

            else:
                # Write lines to output file
                for ln in line.split(';'):
                    f.write(ln)
                    f.write("\n")

                f.write("\n")

    # Close output file
    f.close()

    # Get current timestamp
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    # Print success message on console
    print('[' + dt_string + "] Outage form is completed!")


# Run script manually
if __name__ == "__main__":
    # Load configurations
    form_folder_path = load_configs()

    # Input target asset and form
    target = input("Target = ")
    form = input("Form Name = ") + ".txt"

    # Complete outage form
    complete_outage_form(target, form, form_folder_path)
