#!/usr/bin/env python3
"""Create ttl file manually."""

# Import libraries
from rdflib import Graph, Namespace
from datetime import datetime
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

except BaseException as e:
    # Print error message on console
    print('[' + dt_string + "] Unable to load the configuration file: ",
          str(e))
    sys.exit()

# Graph initialisations
g = Graph()
LNK = Namespace(config["LNK_URI"])
HVS = Namespace(config["HVS_URI"])
OHL = Namespace(config["OHL_URI"])
LOC = Namespace(config["LOC_URI"])
g.bind("lnk", LNK)
g.bind("hvs", HVS)
g.bind("ohl", OHL)
g.bind("loc", LOC)

"""--- Insert script below ---"""
# TIHDCB (Example)
g.set((HVS["TIHDCB"], LNK["hasStatus"], HVS["ENERGISED"]))
g.set((HVS["TIHDCB"], LNK["hasType"], HVS["DCB"]))
g.set((HVS["TIHDCB"], LNK["hasLocation"], LOC["TIH"]))
g.add((HVS["TIHDCB"], LNK["isConnectedTo"], HVS["TIH601"]))
g.add((HVS["TIHDCB"], LNK["isConnectedTo"], HVS["TIH602"]))
g.add((HVS["TIHDCB"], LNK["isConnectedTo"], HVS["TIH647"]))
g.add((HVS["TIHDCB"], LNK["isConnectedTo"], HVS["TIH659"]))
g.add((HVS["TIHDCB"], LNK["isConnectedTo"], HVS["TIH658"]))
g.add((HVS["TIHDCB"], LNK["isConnectedTo"], HVS["TIH648"]))
"""--- Insert script above ---"""

# Graph serialisation
g.serialize('TIH.ttl', format='turtle')
