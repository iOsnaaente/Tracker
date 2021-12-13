import sys, uselect
from utime import sleep, ticks_us
from machine import Pin, PWM, ADC, Timer

#   This will identify the Pico in a multidrop scenario
MyAddress = 1

#   Dictionaries used to translate a port number to a PIN object
DigiOut = {
        1: Pin(15, Pin.OUT),
        2: Pin(16, Pin.OUT),
        3: Pin(17, Pin.OUT),
        4: Pin(18, Pin.OUT),
        5: Pin(20, Pin.OUT),
        20: PWM(Pin(11)),
        21: PWM(Pin(12)),
        22: PWM(Pin(13)),
        }

DigiIn = {
        1: Pin(21, Pin.IN),
        2: Pin(22, Pin.IN),
        }

ADC =   {
        0: ADC(26),
        1: ADC(27),
        2: ADC(28),
        3: ADC(4)
        }

#   Next two lines set up
spoll = uselect.poll()
spoll.register(sys.stdin,uselect.POLLIN)

command = bytes()
validcommand = False

def PWMOut(c):
    #   About 2.5mS to implement
    #   The remote command originally had 4 bytes like #$63
    #   The first command byte has been stripped off at this point leaving $63
    #   The port value is offset by 32 to avoid non-printing characters
    #   and the dreaded CTRL-C which stops the REPL
    port = c[0] - 32
    
    #   convert the two digit hex number to 0-256 and scale it to 0-65535
    duty = c[1] * 256

    try:
        #   if an unknown port is received then don't fall over, just ignore
        #   The DigiOut dictionary contains the pin objects
        p = DigiOut[port]
        p.freq(1000)
        p.duty_u16(duty)
    # print ("56>",c,"1 data:",p,c[1],c[2],"duty:",duty,"*")
    except:
        print("No DigiOut Port",port)

def SetDigital(c):
    #   5mS for each pass of this at 115200
    #   The port value is offset by 32 to avoid non-printing characters
    #   and the dreaded CTRL-C which stops the REPL
    port = c[0] - 32
    # The next byte c[1] has the character "1" or "0"
    try:
        p = DigiOut[port]
        # A '1' in c[1] is ascii 49
        if c[1] == 49:
            p.high()
        else:
            p.low()
    except:
        print("No DigiOut Port",ord(c[0]) - 32)
        
def ReadDigital(c):
    #   5mS to execute
    print (DigiIn[ord(c[0]) - 32].value())

def ReadAnalogue(c):
    #   5mS to execute
    print (ADC[c[0] - 32].read_u16())
        
def ExecuteCmd(cmd):
    # dictionary of commands that can be looked up using an integer command code from the host
    commandpicker = {
        1: SetDigital,
        2: ReadDigital,
        3: ReadAnalogue,
        4: PWMOut,
        5: SetFlashTask,
    }
    # print ("  93>",cmd, cmd[0],cmd[1],cmd[2],"Command",cmd[0] & 31,"*")
    #   Only respond if the address in the command string = MyAddress
    if (cmd[0] >> 5) == MyAddress:
        # print(" 96> Command No:",cmd[0] & 31,cmd[1:],"*")
        func = commandpicker.get(cmd[0] & 31, lambda: "No such command*")

        # Execute the function
        try:
        # print ("  101>",cmd[0],cmd[1],cmd[2],"*")
            func(cmd[1:])
        except:
            print("Command No:",ord(cmd[0]) & 31,"not recognised",cmd[1:],"*")

def ReadSerial():
    global command, validcommand, commandlist
    #   This a non-blocking read of the stdin (REPL port)
    c = (sys.stdin.read(1) if spoll.poll(0) else "")
    if not c == "":
        command += c
    if c == '\x0a':
        # print ("_____",command,"*")
        validcommand = True

class FlashTask:
    #   This class is used for setting up individual Flash Tasks
    #   Each flash task is defined as having an OnTime and OffTime
    #   time expressed in milliseconds
    def __init__(self, PortNo, OnTime, OffTime):
        self.PortNo = PortNo
        self.OnTime = OnTime
        self.OffTime = OffTime
        self.State = 0
        self.CountmS = 0
        
    def stop(self):
        self.run = False
        self.PortNo.low()
        
    def start(self):
        self.CountmS = self.OnTime
        self.State = 1
        self.run = True

    #   This is called every millisecond and the CountmS variable
    #   is decremented from an initial value of either OnTime or OffTime
    #   When it reaches zero the pin is flipped.
    def update(self):
        self.CountmS -= 1
        # print (self.CountmS)
        if self.run:
            if self.CountmS == 0:
                if self.State == 1:
                    self.PortNo.low()
                    self.CountmS = self.OffTime
                    self.State = 0
                else:
                    self.PortNo.high()
                    self.CountmS = self.OnTime
                    self.State = 1
        # else:
           # self.PortNo.low()

def UpdateFlashTasks(t):
    #   This is called every millisecond by the timer interrupt
    for i in range(len(FlashTaskRunning)):
        if FlashTaskRunning[i]:
            FlashTaskList[i].update()  

def SetFlashTask(c):
    # port = int(c[0]) & 31
    # taskno = int(c[0]) >> 5
    port = c[0] & 31
    taskno = (c[0] >> 5) - 1
    # print ("  166>",len(c),"c=",c,"P=",DigiOut[port], "T=",taskno, int(c[1:5], 16),"-",int(c[5:9], 16),'*')
    if int(c[1:5], 16) > 0:
        FlashTaskList[taskno] = FlashTask(DigiOut[port], int(c[1:5], 16), int(c[5:9], 16))
        FlashTaskList[taskno].start()
        FlashTaskRunning[taskno] = True
    else:
        FlashTaskList[taskno].stop()
        FlashTaskRunning[taskno] = False   
    # print (FlashTaskList[taskno])

def MainExec():
    global command, validcommand
    print ("Listening for commands >>")
    while True:
        ReadSerial()
        if validcommand:
            # print("182>:",command,"*")
            ExecuteCmd(command)
            command = bytes()
            validcommand = False


#   We need a list to store the names of the flash tasks.
FlashTaskList = ["FlashTask1", "FlashTask2", "FlashTask3", "FlashTask4", "FlashTask5", "FlashTask6"]
FlashTaskRunning = [False] * 15

#   The next two lines sets up the Timer and initialises the interrupt
#   routine with the callback.
tim = Timer()
tim.init(freq=1000, mode=Timer.PERIODIC, callback=UpdateFlashTasks)
MainExec()