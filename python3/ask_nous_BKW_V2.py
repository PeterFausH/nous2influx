#!/usr/bin/python
# -*- coding: utf-8 -*-
# Powerwerte vom NOUS A1 Steckern http://192.168.20.202/cm?cmnd=Status%208 abfragen
# Json an Nous A1T Steckdose abholen, in crontab eintragen und alle 2 min aufrufen

# 17.08.2020 V2 (c) PFu www.nc-lux.com
import requests
import json
import os
from influxdb import InfluxDBClient

#Konstanten
host = "192.168.22.100" # Raspberry mit Influx und Grafana
port = 8086             # Standard Port Influx
user = "nous"           # Zugangsdaten Influx
password = "passwort"
dbname = "klimawandel"

#Variablen vorbelegen
power = 0.0
today = 0.0

#Basis-Pfad für Http-Request an der Nous Steckdose,
#url_xxxx ist xxxx Teil der mac-Adresse
url_5458 = 'http://192.168.20.209/cm?cmnd=Status%208' # Waschmaschine
url_3029 = 'http://192.168.20.210/cm?cmnd=Status%208' # Starlink
url_4041 = 'http://192.168.20.207/cm?cmnd=Status%208' # SunMan 375Wp
url_7034 = 'http://192.168.20.208/cm?cmnd=Status%208' # TrinaSolar 385Wp
url_7682 = 'http://192.168.20.131/cm?cmnd=Status%208' # CEPS 250Wp


# Influx Datenbank verbinden
client = InfluxDBClient(host, port, user, password, dbname)
#print('InfluxDB erreicht')

# json zusammenbauen für Influx-Datenbank
def add(name,wert):
    info=[{"measurement": "Balkonkraftwerk",
           "fields": {name : wert}}]
    print(info)
    client.write_points(info, time_precision='m')
    return

# Verbrauchswert einlesen
def lese_phase(device, name):
    dose = device[7:21:1] #Teilstring, nur IP-Adresse
    HOST_UP  = True if os.system("ping -c 1 " + dose.strip(";")) is 0 else False
    #print("Dose: ",dose,HOST_UP)
    if HOST_UP == True:
        r = requests.get(device)
        r.raise_for_status()
        parsed_json = json.loads(r.text)
        power = int(parsed_json['StatusSNS']['ENERGY']['Power'])
        today = float(parsed_json['StatusSNS']['ENERGY']['Today'])
        if r.status_code == 200:
            print('Verbindung zur NOUS OK')
        else:
            print('FEHLER, NOUS nicht erreicht!')
        add("p"+name,int(power))
        add("t"+name,float(today))


#Power und Tagesleistung der Mess-Dosen einlesen
power=lese_phase(url_5458,"Waschmaschine")
power=lese_phase(url_3029,"Starlink")
power=lese_phase(url_4041,"sunman_375")
power=lese_phase(url_7034,"trinasolar_385")
power=lese_phase(url_7682,"CEPS_250")

