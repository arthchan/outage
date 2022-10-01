#!/usr/bin/env python3
"""Create ttl file manually."""

# Import libraries
from rdflib import Graph, Namespace

# Graph initialisations
g = Graph()
LNK = Namespace("http://corp.mtrc.com/imd/pd/lnk%")
HVS = Namespace("http://corp.mtrc.com/imd/pd/hvs%")
OHL = Namespace("http://corp.mtrc.com/imd/pd/ohl%")
LOC = Namespace("http://corp.mtrc.com/imd/pd/loc%")
g.bind("lnk", LNK)
g.bind("hvs", HVS)
g.bind("ohl", OHL)
g.bind("loc", LOC)

"""--- Insert script below ---"""
# TIHDCB (Example)
g.set((HVS["TIHDCB"], LNK["hasStatus"], HVS["Energised"]))
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
