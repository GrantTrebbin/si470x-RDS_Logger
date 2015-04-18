#Python Version 2 code

# Many Thanks to Nathan Seidle at Sparkfun for his Arduino Code Example
# It saved me a lot of work

import RPi.GPIO as GPIO
import smbus
import time

GPIO.setwarnings(False)

i2c = smbus.SMBus(1)      #use 0 for older RasPi
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(0, GPIO.OUT)

#create #create 16 registers for SI4703
reg = [0] * 16
 
#Register Descriptions
DEVICEID = 0x00
CHIPID = 0x01
POWERCFG = 0x02
CHANNEL = 0x03
SYSCONFIG1 = 0x04
SYSCONFIG2 = 0x05
SYSCONFIG3 = 0x06
OSCILLATOR = 0x07
STATUSRSSI = 0x0A
READCHAN = 0x0B
RDSA = 0x0C
RDSB = 0x0D
RDSC = 0x0E
RDSD = 0x0F

z = "000000000000000"
 
si4703_addr = 0x10 #found using i2cdetect utility
 
#create list to write registers
#only need to write registers 2-7 and since first byte is in the write
# command then only need 11 bytes to write
writereg = [0] * 11
 
#read 32 bytes
readreg = [0] * 32
 
def write_registers():
    #starts writing at register 2
    #but first byte is in the i2c write command
    global writereg
    global reg
    global readreg
    cmd, writereg[0] = divmod(reg[2], 1<<8)
    writereg[1], writereg[2] = divmod(reg[3], 1<<8)
    writereg[3], writereg[4] = divmod(reg[4], 1<<8)
    writereg[5], writereg[6] = divmod(reg[5], 1<<8)
    writereg[7], writereg[8] = divmod(reg[6], 1<<8)
    writereg[9], writereg[10] = divmod(reg[7], 1<<8)
    w6 = i2c.write_i2c_block_data(si4703_addr, cmd, writereg)
    readreg[16] = cmd #readreg
    read_registers()
    return
 
def read_registers():
    global readreg
    global reg
    readreg = i2c.read_i2c_block_data(si4703_addr, readreg[16], 32)
    reg[10] = readreg[0] * 256 + readreg[1]
    reg[11] = readreg[2] * 256 + readreg[3]
    reg[12] = readreg[4] * 256 + readreg[5]
    reg[13] = readreg[6] * 256 + readreg[7]
    reg[14] = readreg[8] * 256 + readreg[9]
    reg[15] = readreg[10] * 256 + readreg[11]
    reg[0] = readreg[12] * 256 + readreg[13]
    reg[1] = readreg[14] * 256 + readreg[15]
    reg[2] = readreg[16] * 256 + readreg[17]
    reg[3] = readreg[18] * 256 + readreg[19]
    reg[4] = readreg[20] * 256 + readreg[21]
    reg[5] = readreg[22] * 256 + readreg[23]
    reg[6] = readreg[24] * 256 + readreg[25]
    reg[7] = readreg[26] * 256 + readreg[27]
    reg[8] = readreg[28] * 256 + readreg[29]
    reg[9] = readreg[30] * 256 + readreg[31]
    return

def getchannel():
    read_registers()
    channel = reg[READCHAN] & 0x03FF
    channel *= 2
    channel += 875
    return channel
 
def changechannel(newchannel):
    if newchannel < 878 or newchannel > 1080:
       return
    global reg
    newchannel *= 10
    newchannel -= 8750
    newchannel /= 20
    read_registers()
    reg[CHANNEL] &= 0xFE00; #Clear out the channel bits
    reg[CHANNEL] |= newchannel; #Mask in the new channel
    reg[CHANNEL] |= (1<<15); #Set the TUNE bit to start
    write_registers()
    while 1:
        read_registers()
        if ((reg[STATUSRSSI] & (1<<14)) != 0):
            break
    reg[CHANNEL] &= ~(1<<15)
    write_registers()
    return

def setvolume(newvolume):
    global reg
    if newvolume > 15:
        newvolume = 15
    if newvolume < 0:
        newvolume = 0
    read_registers()
    reg[SYSCONFIG2] &= 0xFFF0 #Clear volume bits
    reg[SYSCONFIG2] = newvolume #Set volume to lowest
    write_registers()
    return

def init():
    # init code needs to activate 2-wire (i2c) mode
    # the si4703 will not show up in i2cdetect until
    # you do these steps to put it into 2-wire (i2c) mode
   
    GPIO.output(0,GPIO.LOW)
    time.sleep(.1)
    GPIO.output(23, GPIO.LOW)
    time.sleep(.1)
    GPIO.output(23, GPIO.HIGH)
    time.sleep(.1)

    read_registers()
    # do init step, turn on oscillator
    reg[OSCILLATOR] = 0x8100
    write_registers()
    time.sleep(1)

    read_registers()
    reg[POWERCFG] = 0x4001 #Enable the Radio IC and turn off muted
    write_registers()
    time.sleep(.1)

    read_registers()
    reg[SYSCONFIG1] |= (1<<12) #Enable RDS
    reg[SYSCONFIG2] &= 0xFFF0; #Clear volume bits
    reg[SYSCONFIG2] = 0x0000; #Set volume to lowest
    reg[SYSCONFIG3] = 0x0100; #Set extended volume range (too loud for me without this)
    write_registers()
    return

def seek(direction):
    read_registers()
    reg[POWERCFG] |= (1<<10 )
    if direction == 0:
        reg[POWERCFG] &= ~(1<<1)
    else:
        reg[POWERCFG] |= (1<<9)
    reg[POWERCFG] |= (1<<8)
    write_registers()
    while 1:
        read_registers()
        if ((reg[STATUSRSSI] & (1<<14)) != 0):
            break
    print "Trying Station ", float(float(getchannel())/float(10))
    read_registers()
    valuesfbl = reg[STATUSRSSI] & (1<<13)
    reg[POWERCFG] &= ~(1<<8)
    write_registers()
    return

currvol = 7
init() #init stuff

changechannel(1011) #101.1 The Fox in Kansas City, Classic Rock!!
setvolume(currvol)

#print float(float(getchannel())/float(10))

ans = True
while ans:
    print ("f) Go to 101.1 The Fox")
    print ("+) Increase Volume")
    print ("-) Decrease Volume")
    print ("=) Channel Number (=101.1)")
    print ("w) Tune Up")
    print ("s) Tune Down")
    print ("c) Print Current Channel")
    print ("d) Display Status")
    print ("r} Write RDS")
    print ("r2} Display RDS Groups 2A")
    print ("4) Seek Down")
    print ("5) Seek Up")
    print ("")
   
    ans = raw_input(">")
    if ans == "5":
        seek (1) #1=up\
    if ans == "4":
        seek (0)
    if ans == "f":
        changechannel(1011)
    if ans == "+":
        currvol += 1
        setvolume (currvol)
    if ans == "c":
        print
        print "Curr Chan=", float(float(getchannel())/float(10))
        print
    if ans == "-":
        currvol -= 1
        setvolume (currvol)
    if ans == "w":
        currchan = getchannel()
        wc = currchan + 2
        if wc >= 878 and wc <= 1080:
            currchan = wc
            changechannel(currchan)
    if ans == "s":
        currchan = getchannel()
        wc = currchan - 2
        if wc >= 878 and wc <= 1080:
            currchan = wc
            changechannel(currchan)
    if ans != "" and ans[0] == "=":
        wc = float(ans[1:])
        wc *= 10
        if wc < 878 or wc > 1080:
            print ("Invalid Channel")
            print ("")
        else:   
            changechannel(int(wc))
           
    if ans == "d":
        read_registers()
        print
        print ("Radio Status:")
        if reg[STATUSRSSI] & (1<<15):
            print "RDS Available -",
            blockerr = reg[STATUSRSSI] & 0x0600 >> 9
            if blockerr == 0:
                print ("No RDS Errors")
            if blockerr == 1:
                print ("1-2 RDS Errors")
            if blockerr == 2:
                print ("3-5 RDS Errors")
            if blockerr == 3:
                print ("6+ RDS Errors")
            print
            #r1 = z[:16 - len(bin(reg[RDSA])[2:])] + bin(reg[RDSA])[2:]
            r2 = z[:16 - len(bin(reg[RDSB])[2:])] + bin(reg[RDSB])[2:]
            r3 = z[:16 - len(bin(reg[RDSC])[2:])] + bin(reg[RDSC])[2:]
            r4 = z[:16 - len(bin(reg[RDSD])[2:])] + bin(reg[RDSD])[2:]
            #print r1
            print r2
            print r3
            print r4
            print
        else:
            print ("RDS Not Available")
           
        if reg[STATUSRSSI] & (1<<8):
            print ("Stereo")
        else:
            print ("Mono")
        print

    if ans == "r":
        #h1=""
        h2=""       
        h3=""
        h4=""
        wc = 0
        f= open('/home/pi/rds.csv',"w")
        while 1:
            read_registers()
            if reg[STATUSRSSI] & (1<<15):
                #r1 = z[:16 - len(bin(reg[RDSA])[2:])] + bin(reg[RDSA])[2:]
                r2 = z[:16 - len(bin(reg[RDSB])[2:])] + bin(reg[RDSB])[2:]
                r3 = z[:16 - len(bin(reg[RDSC])[2:])] + bin(reg[RDSC])[2:]
                r4 = z[:16 - len(bin(reg[RDSD])[2:])] + bin(reg[RDSD])[2:]
                if h2 != r2 or h3 != r3 or h4 != r4:
                    f.write(r2 + "," + r3 + "," + r4 + "\n")
                    print wc
                    wc += 1
                    #h1 = r1
                    h2 = r2
                    h3 = r3
                    h4 = r4
                    if wc == 5000:
                        f.close
                        break
    if ans == "r2":
        msg = ""
        mi = 0
        h2=""       
        h3=""
        h4=""
        wc = 0
        f= open('/home/pi/rds.csv',"w")
        while 1:
            read_registers()
            if reg[STATUSRSSI] & (1<<15):
                r2 = z[:16 - len(bin(reg[RDSB])[2:])] + bin(reg[RDSB])[2:]
                r3 = z[:16 - len(bin(reg[RDSC])[2:])] + bin(reg[RDSC])[2:]
                r4 = z[:16 - len(bin(reg[RDSD])[2:])] + bin(reg[RDSD])[2:]
                if h2 != r2 or h3 != r3 or h4 != r4:
                    f.write(r2 + "," + r3 + "," + r4 + "\n")
                    #print wc
                    wc += 1
                    #h1 = r1
                    h2 = r2
                    h3 = r3
                    h4 = r4
                    value = int(r2[:4],2)
                    value2 = int(r2[5:-5],2)
                    if value2 == 0:
                        type = "A"
                    else:
                        type = "B"
                    code =  str(value) + type
                    #time.sleep(.)
                    #print code
                    if code == "2B":
                        chars = chr(int(r3[:8],2)) + chr(int(r3[9:],2)) + chr(int(r4[:8],2)) + chr(int(r4[9:],2))
                        index = int(r2[12:],2)
                        #print hex(int(r3[:8],2)) + '-' + hex(int(r3[9:],2)) + '-' + hex(int(r4[:8],2)) + '-' + hex(int(r4[9:],2))
                        print str(index) + '-' +  chars
                        if index == 0 and mi != 0:
                            print
                            print "RDS MSG = " + msg
                            print
                            break
                        if index == mi:
                            msg += chars
                            mi += 1

                    if wc == 500:
                        f.close
                        break