#!/usr/bin/env python3
"""Perform logic tests and queries for outage generation system."""

# Import libraries
from rdflib import Graph
from datetime import datetime
import os
import json
import sys


# Function for loading configurations and graphs
def load_configs_and_graphs():
    """Load configurations and graphs."""
    try:
        # Open configuration file
        with open("config.json") as json_file:

            # Load data in configuration file
            config = json.load(json_file)

            # Read variables
            data_folder_path = "C:/Users/" + os.getlogin() + config[
                "data_folder_path"]

    except BaseException as e:
        # Get current timestamp
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        # Print error message on console
        print(
            '[' + dt_string + "] Unable to load the configuration file: ",
            str(e))
        sys.exit()

    # Graph initialisation
    g = Graph()

    # Parse all .ttl files into the graph
    for f in os.listdir(data_folder_path):

        # Quit if there is no .ttl file inside the data directory
        if f == []:
            print("No .ttl file inside the data directory!")
            sys.exit()

        g.parse(data_folder_path + '/' + f, format='turtle')

    return g


# Function for getting neighbouring asset and its information (type, status)
def ask_asset_type_status(t, g):
    """Get neighbouring asset and its information (type, status)."""
    q = f"SELECT ?asset ?type ?status WHERE " \
        f"{'{'}hvs:{t} lnk:isConnectedTo ?asset ." \
        f"?asset lnk:hasType ?type ." \
        f"?asset lnk:hasStatus ?status .{'}'}"

    a = g.query(q)

    return a


# Function for filtering query results
def filter_query_results(ans, typ, ast, rch, asd, again=False):
    """Filter query results."""
    fql = []

    for a in ans:
        # If asset is reached before
        if str(a.asset).split('%')[1] in rch:
            continue

        # If asset does not match required type
        elif str(a.type).split('%')[1] not in typ:
            rch.append(str(a.asset).split('%')[1])
            asd.append((
                str(a.asset).split('%')[1],
                str(a.type).split('%')[1],
                str(a.status).split('%')[1]))
            if again:
                fql.append(str(a.asset).split('%')[1])

        # If asset is unreached before and matches required type
        else:
            ast.append(str(a.asset).split('%')[1])
            rch.append(str(a.asset).split('%')[1])
            asd.append((
                str(a.asset).split('%')[1],
                str(a.type).split('%')[1],
                str(a.status).split('%')[1]))

    return ast, rch, fql, asd


# Function for running logic
def run_logic(g, lv, t, type=None, again=True):
    """Run logic."""
    # Initialise lists
    asset = []
    reach = []
    target_list = []
    answer_list = []
    reach_list = []
    asset_details = []
    POINT_OF_ISOLATION = [
        "33CB", "33PS", "11CB", "3P3CB", "RMUI", "RMUCB", "DCCB", "DCI"]

    # Set items in POI as search type
    if type is not None:
        pass
    else:
        type = POINT_OF_ISOLATION

    # Append target to target list
    target_list.append(t)

    # Append target to reached asset list
    reach.append(t)

    # Iterate through all levels
    for i in range(lv):

        # Iterate through all targets
        for j in target_list:

            # Get neighbouring asset(s)
            answer = ask_asset_type_status(j, g)

            # Filter query results
            asset, reach, ask_again, asset_details = filter_query_results(
                answer, type, asset, reach, asset_details, again)

            # If there is asset to be further queried
            while len(ask_again) != 0:

                # Store items to be further queried in a temporary list
                ask_again_temp = ask_again
                ask_again = []

                # Iterate through all items to be further queried
                for x in ask_again_temp:

                    # Get neighbouring asset(s)
                    answer = ask_asset_type_status(x, g)

                    # Filter query results
                    asset, reach, ask_again_later, asset_details\
                        = filter_query_results(
                            answer, type, asset, reach, asset_details, again)

                    # Append items to be further queried to the main list
                    ask_again += ask_again_later

        # Add items in asset list to target list
        target_list = asset.copy()

        # Append answers to list
        answer_list.append((i + 1, asset.copy()))

        # Append reached assets to list
        reach_list.append((i + 1, reach.copy()))

        # Clear asset list
        asset.clear()

    return answer_list, reach_list, asset_details


# Run script directly for testing
if __name__ == "__main__":
    # Input target asset
    target = input("Target = ")

    # Input number of level
    try:
        level = int(input("Level(s) = "))

        # Quit if level is not greater than 0
        if level <= 0:
            print("Please input an integer greater than 1!")
            sys.exit()

    # Quit if there any error
    except BaseException:
        print("Please input an integer greater than 0!")
        sys.exit()

    # Print a blank line
    print("")

    # Load configurations and graphs
    graph = load_configs_and_graphs()

    # Run logic
    ans_list, rch_list, asd_list = run_logic(graph, level, target)

    # Print answers
    print("Point(s) of Isolation:")
    for ans in ans_list:
        print("Level " + str(ans[0]) + ": " + str(ans[1]))

    # Print reached assets
    print("\nReached asset(s):")
    for rch in rch_list:
        print("Level " + str(rch[0]) + ": " + str(rch[1]))

    # Print details of assets
    print("\nDetails of asset(s):")
    print(asd_list)
