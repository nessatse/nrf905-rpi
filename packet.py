# Sensor types
SENSE_LM75=1
SENSE_BAT=2

class PacketError(Exception):
    pass

class Packet:
    def __init__(self,packet=None):
        """Constructor
        :param packet: raw packet to decode
        :type packet:  string
        """
        self.temperatures = []
        self.batteryok = None
        if packet is not None:
            self.DecodePacket(packet)
    
    def DecodePacket(self,packet):
        self.pktlen = packet[0]
        if self.pktlen > len(packet):
            raise PacketError('Packet to small')
        packet = packet[0:self.pktlen]
        self.unitid = packet[1]
        self.packetid = packet[2]                
        packet = packet[3:]
        while packet:
            rectype = packet[0]
            packet = packet[1:]
            if rectype == SENSE_LM75:
                temp = (packet[1]<<8|packet[0])/8.0
                self.temperatures.append(temp)
                packet = packet[2:]
            elif rectype == SENSE_BAT:
                self.batteryok = (packet[0] != 0)
                packet = packet[1:]
            else:
                raise PacketError('Unknown record type: {0}'.format(rectype))
