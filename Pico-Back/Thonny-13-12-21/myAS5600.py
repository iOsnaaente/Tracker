import machine 
import time 

class AS5600: 
  ##  FIGURE 21 - DATASHEET available in https://ams.com/documents/20143/36005/AS5600_DS000365_5-00.pdf
  ## Configuration registers 
  ZMCO      = 0x0 
  ZPOS      = 0x1
  MPOS      = 0x3
  MANG      = 0x5
  CONF      = 0x7
  ## Output Registers
  RAWANGLE  = 0x0C
  ANGLE     = 0x0E
  ## Status Registers
  STATUS    = 0x0B
  AGC       = 0x1A
  MAGNITUDE = 0x1B 
  ## Burn Commands 
  BURN      = 0xff

  # Magnetic sensor stuffs 
  Status     = 0       # Status register (MD, ML, MH)
  ADDRESS    = 0x36    # By default 

  startAngle = 0  # starting angle
  totalAngle = 0  # total absolute angular displacement

  ## Constructor 
  def __init__( self, I2C : machine.I2C , addr : int = 0x36, startAngle : float = 0.0  ): 
    self.ADDRESS = addr 
    self.AS5600 = I2C 

    self.degAngle = startAngle
    self.rawAngle = 0.0
    self.gain = 0.0 

    status = self.checkStatus()  # Check the magnet
    if status == 0:
      print('Magnet OK')
    elif status == -1: 
      print('Magnet with Low Level')
    elif status ==  1:
      print('Magnet with Strong Level')


  ## To write in the I2C we need a buffer struct like b'a21@\x02' 
  def _write( self, addr_mem : int, buffer : bytes ) -> None:
    self.AS5600.writeto_mem( self.ADDRESS, addr_mem, buffer )


  ## to read, we start at addr_mem and we read num_bytes from addr_mem 
  def _read( self, addr_mem : int, num_bytes : int = 2 ) -> list:
    return self.AS5600.readfrom_mem( self.ADDRESS, addr_mem, num_bytes )


  ## read the unscaled angle and unmodified angle 
  def readRawAngle( self ) -> bytes:
    raw_angle = self._read( self.ANGLE, 2 )
    HIGH_BYTE = raw_angle[0]    #  RAW ANGLE(11:8) on 0x0C address 
    LOW_BYTE  = raw_angle[1]    #  RAW ANGLE(7:0) on 0X0D address 

    RAW_ANGLE = ( (HIGH_BYTE << 8) | LOW_BYTE ) 
    
    self.rawAngle = RAW_ANGLE 
    return RAW_ANGLE 

  def getGain(self):
    self.gain = self._read( self.AGC , 1 )
    return self.gain

  ## Read the scaled angle 
  def readAngle( self ) -> bytes : 
    # To calculate the real angle : 
    # We have to divide the 360º by the 12bits (0x0fff) plus the value from the sensor
    # rawAngle * 360/4096 = rawAngle * 0.087890625
    RAW_ANGLE = self.readRawAngle() 
    DEG_ANGLE = RAW_ANGLE * ( 360.0 / 0x0fff )

    # If the angle is negative, we have to normalize it to be between [0, 360)º
    self.degAngle = DEG_ANGLE - self.startAngle
    if self.degAngle < 0: 
      self.degAngle += 360 

    return self.degAngle 
    

  ## Verify the status of the magnetic range 
  ### The status be in the 0x0B address in the 5:3 bits
  #  
  ## MH [3] AGC minimum gain overflow, magnet too strong  
  ## ML [4] AGC maximum gain overflow, magnet too weak
  ## MD [5] Magnet was detected
  #
  ## To operate properly, the MD have to be set and the MH and ML have to be 0 
  def checkStatus( self ): 
    status = self._read( self.STATUS, 1 )
    self.MH = status[0] >> 3 
    self.ML = status[0] >> 4
    self.MD = status[0] >> 5

    ## Return 0 if OK, else -1 to low magnetic level or 1 to high magnetic level 
    if self.MD:
      return 0 
    else: 
      if self.MH:
        return -1 
      if self.ML:
        return  1  

