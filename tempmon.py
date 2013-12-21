#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 
import time
import sys
import emoncms
import nrf905
import packet
import rrdtool
import re

API_KEY='251480aabf94ea4187bdbde465a1a524'
RRDPATH='/home/pi/tempmon'

def createrrd(fn):
    rrdtool.create(fn,'DS:temp:GAUGE:300:-1.0000000000e+01:1.0000000000e+02',
            'RRA:AVERAGE:0.5:1:518400','RRA:AVERAGE:0.5:10:207360','RRA:AVERAGE:0.5:120:36000',
            'RRA:MAX:0.5:10:207360','RRA:MIN:0.5:10:207360',
            'RRA:MAX:0.5:120:36000','RRA:MIN:0.5:120:36000')

if __name__ == '__main__':
    emon = emoncms.emoncms(API_KEY)
    radio = nrf905.nrf905()
    radio.configure()
    radio.rxaddress((0xf0,0xf0,0xf0,0xf0))
    print(radio.dumpconfig())
    try:
        pubctr = {}
        while True:
            pkt = packet.Packet(radio.receive());
            pubctr[pkt.unitid] = pubctr.get(pkt.unitid,0) + 1
            print("%s PktID: %d UnitID: %d " % (time.ctime(),pkt.packetid,pkt.unitid)),
            for t in range(len(pkt.temperatures)):
                print("Temp[%d]:%f" %(t,pkt.temperatures[t])),
            if pkt.batteryok is not None:
                print(" Battery: %d" % (pkt.batteryok))
            else:
                print("")
            for t in range(len(pkt.temperatures)):
                rrdfile = RRDPATH+'/temp-'+str(pkt.unitid)+'-'+str(t)+'.rrd'
                try:
                    rrdtool.update(rrdfile,'N:'+str(pkt.temperatures[t]))
                except rrdtool.error as e:
                    print(("RRD Update Error: %s" % e.message))
                    if (re.search("No such file or directory",e.message)):
                        createrrd(rrdfile);
                        rrdtool.update(rrdfile,'N:'+str(pkt.temperatures[t]))
            if pubctr[pkt.unitid] == 5:
                for t in range(len(pkt.temperatures)):
                    emon.publish(('U'+str(pkt.unitid)+'S'+str(t),100*pkt.temperatures[t]))
                pubctr[pkt.unitid]=0
    except KeyboardInterrupt:
        print "Interrupt"
    radio.shutdown();
    print("Done")
