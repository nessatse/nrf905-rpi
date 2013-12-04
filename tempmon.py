#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 
import time
import sys
import emoncms
import nrf905
import packet
import rrdtool

API_KEY='251480aabf94ea4187bdbde465a1a524'
RRDPATH='/home/pi/tempmon'

emon = emoncms.emoncms(API_KEY)
radio = nrf905.nrf905()
radio.configure()
radius.rxaddress((0xf0,0xf0,0xf0,0xf0))
print(radio.dumpconfig())
try:
    pubctr = {}
    while True:
        pubctr[pkt.unitid] = pubctr.get(pkt.unitid,0) + 1
        pkt = packet.Packet(radio.receive());
        print("%s PktID: %d UnitID: %d " % (time.ctime(),pkt.packetid,pkt.unitid)),
        for t in range(len(pkt.temperatures)):
            print("Temp[%d]:%f" %(t,pkt.temperatures[t])),
        if pkt.batteryok is not None:
            print(" Battery: %d" % (pkt.batteryok))
        else:
            print("")
        for t in range(len(pkt.temperatures)):
            rrdfile = RRDPATH+'/temp-'+str(pkt.unitid)+'-'+str(t)+'.rrd'
            rrdtool.update(rrdfile,'N:'+str(pkt.temperatures[t]))
        if pubctr[pkt.unitid] == 20:
            for t in range(len(pkt.temperatures)):
                emon.publish(('U'+str(pkt.unitid)+'S'+str(t),pkt.temperatures[t]))
            pubctr[pkt.unitid]=0
except KeyboardInterrupt:
    print "Interrupt"
radio.shutdown();
print("Done")
