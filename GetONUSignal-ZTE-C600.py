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


def GetPonNameInfo(ip):
    cmd = f'snmpwalk -v2c -c tripleplay {ip}:65161 iso.3.6.1.2.1.31.1.1.1.1 | grep gpon_'
    shellcmd = os.popen(cmd)
    return shellcmd.read().splitlines()


def GetOntSignalMinMaxAndMidle(PonInfo, pon):
    sinais = []
    for linha in PonInfo:
        if "dbm" in linha:
            sinal = float(linha.replace(
                'gpon_onu-', '').replace('(dbm)', '').split('-')[1].replace(' ', ''))*(-1)
            print(sinal)
            sinais.append(sinal)
    if len(sinais) > 0:
        media = statistics.median_grouped(sinais)
        melhor = max(sinais)
        pior = min(sinais)

        os.system(f'zabbix_sender -z zabbix -s "{hostname}" -k OntBestSinal.[{pon}] -o {melhor}')
        time.sleep(1)
        os.system(f'zabbix_sender -z zabbix -s "{hostname}" -k OntPoorSinal.[{pon}] -o {pior}')
        time.sleep(1)
        os.system(f'zabbix_sender -z zabbix -s "{hostname}" -k OntMediaSinal.[{pon}] -o {media}')
        time.sleep(1)
        


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

        tn.write(f'show pon power olt-rx {pon}\n'.encode('utf-8'))
        time.sleep(1)
        return_interfaceList = tn.read_until(
            'Control flag'.encode('utf-8'), 3).decode('utf-8').splitlines()

        GetOntSignalMinMaxAndMidle(return_interfaceList, pon)

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
hostname = sys.argv[5]


if __name__ == "__main__":
    main(ip, user, password, port)
