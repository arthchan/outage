#!/usr/bin/env python3
"""Perform logic tests for outage generation system."""

# Import libraries
from rdflib import Graph
import os

# Initialise lists
asset = []
reach = []
target_list = []
point_of_isolation = ["33CB", "33PS", "11CB", "3P3CB", "RMUI", "RMUCB",
                      "DCCB", "DCI"]

# Graph initialisation
g = Graph()

# Parse all .ttl files into the graph
for f in os.listdir("data"):

    # Quit if there is no .ttl file inside the data directory
    if f == []:
        print("No .ttl file inside the data directory!")
        quit()

    g.parse("data/" + f, format='turtle')


# Function for getting neighbouring asset and its information (type, status)
def ask_asset_type_status(t):
    """Get neighbouring asset and its information (type, status)."""
    q = f"SELECT ?asset ?type ?status WHERE " \
        f"{'{'}hvs:{t} gen:isConnectedTo ?asset ." \
        f"?asset gen:hasType ?type ." \
        f"?asset gen:hasStatus ?status .{'}'}"

    a = g.query(q)

    return a


# Function for filtering query results
def filter_query_results(ans, poi, ast, rch, again=False):
    """Filter query results."""
    fql = []

    for a in ans:
        # If asset is reached before
        if str(a.asset).split('%')[1] in rch:
            continue

        # If asset is not a point of isolation
        elif str(a.type).split('%')[1] not in poi:
            rch.append(str(a.asset).split('%')[1])
            if again:
                fql.append(str(a.asset).split('%')[1])

        # If asset is unreached before and is a point of isolation
        else:
            ast.append(str(a.asset).split('%')[1])
            rch.append(str(a.asset).split('%')[1])

    return ast, rch, fql


# Input target asset
target = input("Target = ")

# Append target to target list
target_list.append(target)

# Append target to reached asset list
reach.append(target)

# Input number of level
try:
    level = int(input("Level(s) = "))

    # Quit if level is not greater than 0
    if level <= 0:
        print("Please input an integer greater than 1!")
        quit()

# Quit if there any error
except BaseException:
    print("Please input an integer greater than 0!")
    quit()

# Print a blank line
print("")

# Iterate through all levels
for i in range(level):

    # Iterate through all targets
    for j in target_list:

        # Get neighbouring asset(s)
        answer = ask_asset_type_status(j)

        # Filter query results
        asset, reach, ask_again = filter_query_results(
            answer, point_of_isolation, asset, reach, again=True)

        # If there is asset to be further queried
        while len(ask_again) != 0:

            # Store items to be further queried in a temporary list
            ask_again_temp = ask_again
            ask_again = []

            # Iterate through all items to be further queried
            for x in ask_again_temp:

                # Get neighbouring asset(s)
                answer = ask_asset_type_status(x)

                # Filter query results
                asset, reach, ask_again_later = filter_query_results(
                    answer, point_of_isolation, asset, reach, again=True)

                # Append items to be further queried to the main list
                ask_again += ask_again_later

    # Add items in asset list to target list
    target_list = asset.copy()

    # Print all answers
    print("Level " + str(i + 1) + ": ", asset)

    # Clear asset list
    asset.clear()
