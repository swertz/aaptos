# SOAP Server
SOAPServer = "localhost"
SOAPPort = 8080

# Available Devices
Devices = []
#Devices = [ ("E3631A","AgilentE3631A","/dev/ttyUSB1"),
#            ("E3633A","AgilentE3633A","/dev/ttyUSB0") ]

AutoDevices = [ "/dev/ttyUSB0" ]#, "/dev/ttyUSB0" ]

def autoNaming(port, device):
  # defines the device name.
  # It will be called by the SOAP server for any AutoDevice above.
  # Example call: autoNaming("ttyUSB0","AgilentE3631A",0)
  return device[7:]

# Database for logging
DbLogin = "aaptos"
DbPassword = "aaptos"
Database = "localhost/aaptos"
PoolDelay = 10 #seconds

