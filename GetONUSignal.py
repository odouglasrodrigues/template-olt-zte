#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import telnetlib
import sys
import statistics


pons = []


def OrgnnizePonName(dataPonsTotal):
    for linha in dataPonsTotal:
        if "gpon_" in linha:
            pon = linha.split(":")[1].replace('"', '').replace(" ", "")
            pons.append(pon)


def GetPonNameInfo():
    cmd = "snmpwalk -v2c -c public 190.123.65.230:65161 iso.3.6.1.2.1.31.1.1.1.1 | grep gpon_"
    shellcmd = os.popen(cmd)
    return shellcmd.read().splitlines()


def GetOntSignalMinMaxAndMidle(PonInfo):
    sinais = []
    for linha in PonInfo:
        if "dbm" in linha:
            sinal = float(linha.replace(
                'gpon-onu', '').replace('(dbm)', '').split('-')[1].replace(' ', ''))*(-1)
            sinais.append(sinal)
    if len(sinais) > 0:
        media = statistics.median_grouped(sinais)
        melhor = max(sinais)
        pior = min(sinais)
        print(
            f"Melhor sinal: {melhor} || Pior sinal: {pior} || Sinal médio: {media}")


def ConnectOnOLTWithTelnet(ip, user, password, port):
    OrgnnizePonName(GetPonNameInfo())

    try:
        tn = telnetlib.Telnet(ip, port, 10)
    except Exception as e:
        print(e)
        return

    # tn.set_debuglevel(100)

    tn.read_until(b"Username:")
    tn.write(user.encode('utf-8') + b"\n")
    time.sleep(.3)
    tn.read_until(b"Password:")
    tn.write(password.encode('utf-8') + b"\n")
    time.sleep(.3)
    tn.write(b'terminal length 0\n')
    time.sleep(.3)

    for pon in pons:
        pon_olt = pon.replace("_", "-olt_")
        tn.write(f'show pon power olt-rx {pon_olt}\n'.encode('utf-8'))
        time.sleep(1)
        return_interfaceList = tn.read_until(
            'Control flag'.encode('utf-8'), 3).decode('utf-8').splitlines()

        print(f'PON: {pon}')
        GetOntSignalMinMaxAndMidle(return_interfaceList)

    tn.write(b"exit\n")
    time.sleep(.3)
    tn.close()
    return


def main(ip, user, password, port):
    ConnectOnOLTWithTelnet(ip, user, password, port)


ip = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]
port = sys.argv[4]

if __name__ == "__main__":
    main(ip, user, password, port)
