#!/bin/python3
#
# Examples:
#    python3 info.py -p /dev/ttyUSB0
#

import sys
import fcntl
import argparse
from time import sleep

sys.path.append("../")

import buttshock.et312

def main():

    modes = {0x76:"Waves", 0x77:"Stroke", 0x78:"Climb", 0x79:"Combo", 0x7a:"Intense", 0x7b:"Rhythm",
             0x7c:"Audio1",0x7d:"Audio2", 0x7e:"Audio3", 0x80:"Random1", 0x81:"Random2", 0x82:"Toggle",
             0x83:"Orgasm",0x84:"Torment",0x85:"Phase1",0x86:"Phase2",0x87:"Phase3",
             0x88:"User1",0x89:"User2",0x8a:"User3",0x8b:"User4",0x8c:"User5",0:"None", 0x7f:"Split"}
    powerlevels = {1:"Low (1)",2:"Normal (2)",3:"High (3)"}

    parser = argparse.ArgumentParser()

    parser.add_argument("-p","--port",dest="port",help="Port for ET312 (default /dev/ttyUSB0)")    
    args = parser.parse_args()
    port = "/dev/ttyUSB0"  # lazy default
    if (args.port):
        port = args.port

    # Lock the serial port while we use it, wait a few seconds
    connected = False
    for _ in range(10):
        try:
            et312 = buttshock.et312.ET312SerialSync(port)
            if et312.port.isOpen():
                fcntl.flock(et312.port.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                connected = True
            break
        except Exception as e:
            print(e)
            sleep(.2)

    if (not connected):
        print ("Failed")
        return

    try:
        print ("[+] connected")
# no need to do a handshake unless we want to poke
#        print ("[+] trying handshake")
#        et312.perform_handshake()
#        print ("[+] handshake ok")

        print("ADC0 (current sense)\t\t: {0:#x}".format(et312.read(0x4060)))
        print("ADC1 (MA knob)\t\t\t: {0:#x}".format(et312.read(0x4061)))
        print("\tMA scaled value\t\t: %d (mode range %d-%d)" %(et312.read(0x420d),et312.read(0x4086),et312.read(0x4087)))
        print("ADC2 (PSU voltage)\t\t: {0:#x}".format(et312.read(0x4062)))
        print("ADC3 (Battery voltage)\t\t: {0:#x}".format(et312.read(0x4063)))
        print("\tBattery at boot\t\t: {0:.1f}%".format((et312.read(0x4203))*100/256))
        print("ADC4 (Level A knob)\t\t: {0:#x}".format(et312.read(0x4064)))
        print("ADC5 (Level B knob)\t\t: {0:#x}".format(et312.read(0x4065)))
        currentmode =et312.read(0x407b)
        print("Power Level\t\t\t: "+powerlevels[et312.read(0x41f4)])
        usermodes = et312.read(0x41f3)-0x87
        print("User programs loaded\t\t: {0:#d}".format(usermodes))
        for i in range (0,usermodes):
            startmodule = et312.read(0x8018+i)
            if (startmodule < 0xa0):
                programlookup = et312.read(0x8000+startmodule-0x60)
                programblockstart = 0x8040+programlookup
            else:
                programlookup = et312.read(0x8000+startmodule-0xa0)
                programblockstart = 0x8100+programlookup
            print("\tUser %d is module 0x%02x\t: 0x%04x (eeprom)"%(i+1,startmodule,programblockstart))
        print("Current Mode\t\t\t: "+modes[currentmode])
        if (currentmode == 0x7f):
            print("\tSplit Mode A\t\t: "+modes[et312.read(0x41f5)])
            print("\tSplit Mode B\t\t: "+modes[et312.read(0x41f6)])
        if (currentmode == 0x80):
            print("\tCurrent Random Mode\t: "+modes[et312.read(0x4074)])
            timeleft = et312.read(0x4075) - et312.read(0x406a)
            if (timeleft<0):
                timeleft+=256
            print("\tTime until change mode\t: {0:#d} seconds ".format(int(timeleft/1.91)))
        print("\tMode has been running\t: {0:#d} seconds".format(int((et312.read(0x4089)+et312.read(0x408a)*256)*1.048)))

            
    except Exception as e:
        print(e)

    if (et312):
        print("[+] resetting key")
        et312.reset_key()  # reset cipher key so easy resync next time
        et312.close()

if __name__ == "__main__":
    main()
                                                                        
