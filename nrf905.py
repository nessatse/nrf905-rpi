#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 
import RPi.GPIO as GPIO
#import spidev
import spi
import time
import sys
import packet

NRF_CE=3
NRF_TxEN=5
NRF_PWR=7
NRF_CD=11
NRF_DR=13
NRF_CSN=24

# Instructions
W_CONFIG=0b00000000
R_CONFIG=0b00010000
W_TX_PAYLOAD=0b00100000
R_TX_PAYLOAD=0b00100001
W_TX_ADDRESS=0b00100010
R_TX_ADDRESS=0b00100011
R_RX_PAYLOAD=0b00100100
CHANNEL_CONFIG=0b10000000
# Registers
NRF905_REG_CHANNEL=0x00
NRF905_REG_AUTO_RETRAN=0x01
NRF905_REG_LOW_RX=0x01
NRF905_REG_PWR=0x01
NRF905_REG_BAND=0x01
NRF905_REG_CRC_MODE=0x09
NRF905_REG_CRC=0x09
NRF905_REG_CLK=0x09
NRF905_REG_OUTCLK=0x09
NRF905_REG_OUTCLK_FREQ=0x09
NRF905_REG_RX_ADDRESS=0x05
NRF905_REG_RX_PAYLOAD_SIZE=0x03
NRF905_REG_TX_PAYLOAD_SIZE=0x04
NRF905_REG_ADDR_WIDTH=0x02
# Register masks
NRF905_MASK_CHANNEL=0xFC
NRF905_MASK_AUTO_RETRAN=0x20
NRF905_MASK_LOW_RX=0x10
NRF905_MASK_PWR=0x0c
NRF905_MASK_BAND=0x02
NRF905_MASK_CRC_MODE=0x80
NRF905_MASK_CRC=0x40
NRF905_MASK_CLK=0x38
NRF905_MASK_OUTCLK=0x04
NRF905_MASK_OUTCLK_FREQ=0x03

NRF905_BAND_433=0x00
NRF905_BAND_868=0x02
NRF905_BAND_915=0x02
NRF905_PWR_n10=0x00
NRF905_PWR_n2=0x04
NRF905_PWR_6=0x08
NRF905_PWR_10=0x0C
NRF905_LOW_RX_ENABLE=0x10
NRF905_LOW_RX_DISABLE=0x00
NRF905_AUTO_RETRAN_ENABLE=0x20
NRF905_AUTO_RETRAN_DISABLE=0x00
NRF905_OUTCLK_ENABLE=0x04
NRF905_OUTCLK_DISABLE=0x00
NRF905_OUTCLK_4MHZ=0x00
NRF905_OUTCLK_2MHZ=0x01
NRF905_OUTCLK_1MHZ=0x02
NRF905_OUTCLK_500KHZ=0x03
NRF905_CRC_ENABLE=0x40
NRF905_CRC_DISABLE=0x00
NRF905_CRC_MODE_8=0x00
NRF905_CRC_MODE_16=0x80
NRF905_XOF_16=0x18

# SA Bands
# 433.05-434.79 (Ch 107-124) (Actually 123.9)
# 868-868.6 
# 868.7-869.2 (Ch 12)
# 869.4-869.65 
# 869.7-870
class nrf905:
    def __init__(self):
        #self._spi = spidev.SpiDev()
        #self._spi.open(0,1)
        self.setupio()
        spi.openSPI(speed=106000)

    def setupio(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(NRF_CE, GPIO.OUT)
        GPIO.setup(NRF_TxEN, GPIO.OUT)
        GPIO.setup(NRF_PWR, GPIO.OUT)
        GPIO.setup(NRF_CSN, GPIO.OUT)
        GPIO.setup(NRF_CD, GPIO.IN)
        GPIO.setup(NRF_DR, GPIO.IN)
        GPIO.output(NRF_CSN,1)
        GPIO.output(NRF_PWR,0)
        GPIO.output(NRF_CE,0)
        GPIO.output(NRF_TxEN,0)

    def wr_config(self,reg,val):
        GPIO.output(NRF_CSN,0)
        spi.transfer((reg,val))
        GPIO.output(NRF_CSN,1)

    def configure(self):
        self.wr_config(W_CONFIG|NRF905_REG_CHANNEL,117)
        self.wr_config(W_CONFIG|1,(NRF905_PWR_10))
        self.wr_config(W_CONFIG|NRF905_REG_ADDR_WIDTH,0x44)
        self.wr_config(W_CONFIG|NRF905_REG_RX_PAYLOAD_SIZE,32)
        self.wr_config(W_CONFIG|NRF905_REG_TX_PAYLOAD_SIZE,32)
        self.wr_config(W_CONFIG|9,(NRF905_CRC_MODE_16|NRF905_CRC_ENABLE|NRF905_XOF_16))
        self.powerup()
        
    def powerup(self):
        GPIO.output(NRF_CE,0)
        GPIO.output(NRF_TxEN,0)
        GPIO.output(NRF_PWR,1)

    def powerdown(self):
        GPIO.output(NRF_PWR,0)

    def shutdown(self):
        self.powerdown()
        GPIO.cleanup()

    def dumpconfig(self):
        GPIO.output(NRF_CSN,0)
        cfg = spi.transfer((R_CONFIG,0,0,0,0,0,0,0,0,0,0))
        GPIO.output(NRF_CSN,1)
        print("STATUS  = 0x%0.2x" % cfg[0])
        print("CHANNEL = 0x%0.2x %d" % (cfg[1],cfg[1]))
        print("AUTO_RETRAN = 0x%0.2x RX_RED_PWR = 0x%0.2x PWR = 0x%0.2x BAND = 0x%0.2x" % (cfg[2]&
            NRF905_MASK_AUTO_RETRAN,cfg[2]& NRF905_MASK_LOW_RX, cfg[2]&
            NRF905_MASK_PWR, cfg[2]& NRF905_MASK_BAND))
        print("RX_AFW = 0x%0.2x TX_AFW = 0x%0.2x" %((cfg[3] & 0x70)>>4,cfg[3] &
            0x7))
        print("RX_PW = 0x%0.2x TX_PW = 0x%0.2x" % (cfg[4]& 0x3f,cfg[5]& 0x3f))
        print("RX_ADDRESS = 0x%0.2x%0.2x%0.2x%0.2x" %
                (cfg[6],cfg[7],cfg[8],cfg[9]))
        print("CRC_MODE = 0x%0.2x CRC_EN = 0x%0.2x XOF = 0x%0.2x OUTCLK = 0x%0.2x OUTCLK_FREQ = 0x%0.2x" 
                % ((cfg[10] & NRF905_MASK_CRC_MODE)>>7,
            (cfg[10] & NRF905_MASK_CRC)>>6,(cfg[10] & NRF905_MASK_CLK)>>3,(cfg[10] &
                NRF905_MASK_OUTCLK)>>2,cfg[10] & NRF905_MASK_OUTCLK_FREQ))
        return cfg

    def rxaddress(self,addr):
        GPIO.output(NRF_CSN,0)
        spi.transfer((W_CONFIG|NRF905_REG_RX_ADDRESS,))
        spi.transfer(addr)
        GPIO.output(NRF_CSN,1)

    def status(self):
        GPIO.output(NRF_CSN,0)
        st = spi.transfer((0xff,))
        GPIO.output(NRF_CSN,1)
        return st[0]

    def receive(self):
        GPIO.output(NRF_TxEN,GPIO.LOW)
        GPIO.output(NRF_CE,GPIO.HIGH)   

        timeout = time.time()+20
        cdcount = 0
        GPIO.wait_for_edge(NRF_DR, GPIO.RISING);
        GPIO.output(NRF_CE,GPIO.LOW)   
        data = self.rxpayload()
        GPIO.output(NRF_TxEN,GPIO.HIGH)
        return data
        
    def rxpayload(self):
        GPIO.output(NRF_CSN,0)
        spi.transfer((R_RX_PAYLOAD,))
        data = list(spi.transfer((0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0)))
        GPIO.output(NRF_CSN,1)
        return data

    def dumptxaddr(self):
      return spi.transfer((R_TX_ADDRESS,0,0,0,0))

if __name__ == '__main__':
    print("Hello")
    n=nrf905()
    print(n.dumpconfig())
    n.configure()
    n.rxaddress((0xf0,0xf0,0xf0,0xf0))
    print(n.dumpconfig())
    n.shutdown()
    print("Bye")
