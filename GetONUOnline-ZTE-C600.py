#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import telnetlib
import sys


pons = []
TotalOntOnline = []
TotalOntProvisioned = []

# @profile
def OrgnnizePonName(dataPonsTotal):
    for linha in dataPonsTotal:
        if "gpon_" in linha:
            pon = linha.split(":")[1].replace('"', '').replace(" ", "")
            pons.append(pon)

# @profile
def GetPonNameInfo(ip):
    cmd = f'snmpwalk -v2c -c tripleplay {ip}:65161 iso.3.6.1.2.1.31.1.1.1.1 | grep gpon_'
    shellcmd = os.popen(cmd)
    return shellcmd.read().splitlines()

# @profile
def GetOntProvisionedAndOntOnline(PonInfo, pon):
    for linha in PonInfo:
        if "ONU Number" in linha:
            onuOnline = int(linha.split(':')[1].split('/')[0].replace(" ", ""))
            onuProvisioned = int(linha.split(
                ':')[1].split('/')[1].replace(" ", ""))

            TotalOntOnline.append(onuOnline)
            TotalOntProvisioned.append(onuProvisioned)

            os.system(
                f'zabbix_sender -z zabbix -s "{hostname}" -k OntOnline.[{pon}] -o {onuOnline}')
            time.sleep(1)
            os.system(
                f'zabbix_sender -z zabbix -s "{hostname}" -k OntProvisioned.[{pon}] -o {onuProvisioned}')
            time.sleep(1)
            os.system(
                f'zabbix_sender -z zabbix -s "{hostname}" -k OntOffline.[{pon}] -o {onuProvisioned-onuOnline}')
            time.sleep(1)

# @profile
def ConnectOnOLTWithTelnet(ip, user, password, port):
    OrgnnizePonName(GetPonNameInfo(ip))

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
        tn.write(f'show gpon onu state {pon}\n'.encode('utf-8'))
        time.sleep(1)
        return_interfaceList = tn.read_until(
            'Control flag'.encode('utf-8'), 3).decode('utf-8').splitlines()
        
        GetOntProvisionedAndOntOnline(return_interfaceList, pon)

    tn.write(b"exit\n")
    time.sleep(.3)
    tn.close()
    return

# @profile
def main(ip, user, password, port):
    ConnectOnOLTWithTelnet(ip, user, password, port)
    os.system(
        f'zabbix_sender -z zabbix -s "{hostname}" -k TotalOntOnline -o {sum(TotalOntOnline)}')
    time.sleep(1)

    os.system(
        f'zabbix_sender -z zabbix -s "{hostname}" -k TotalOntProvisioned -o {sum(TotalOntProvisioned)}')
    time.sleep(1)

    os.system(
        f'zabbix_sender -z zabbix -s "{hostname}" -k TotalOntOffline -o {sum(TotalOntProvisioned)-sum(TotalOntOnline)}')
    time.sleep(1)


ip = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]
port = sys.argv[4]
hostname = sys.argv[5]

if __name__ == "__main__":
    main(ip, user, password, port)
