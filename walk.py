#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
cmd = "snmpwalk -v2c -c public 190.123.65.230:65161 iso.3.6.1.2.1.31.1.1.1.1 | grep gpon_"
shellcmd = os.popen(cmd)
return_walk=shellcmd.read().splitlines()
pons = []

for linha in return_walk:
    if "gpon_" in linha:
        pon = linha.split(":")[1].replace('"','').replace(" ", "")
        print(pon)
        pons.append(pon)

print(pons)