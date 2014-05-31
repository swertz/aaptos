import SOAPpy
import time
import AaptosDb
from threading import Thread
from AgilentE3631A import AgilentE3631A
from AgilentE3633A import AgilentE3633A

class aaptos:
  def __init__(self):
    # For now, this is static. 
    self.E3631A = AgilentE3631A(port='/dev/usb/ttyUSB0')
    self.E3633A = AgilentE3633A(port='/dev/usb/ttyUSB1')
    self.devices = [ self.E3631A, self.E3633A ] 
    self.P6V = self.E3631A.getInstrument("P6V")
    self.P25V = self.E3631A.getInstrument("P25V")
    self.M25V = self.E3631A.getInstrument("M25V")
    self.P20V = self.E3633A.getInstrument("P20V")
    self.instruments = [ self.P6V, self.P25V, self.M25V, self.P20V ]
    
  def getStatus(self):
    result = {}
    for i in self.instruments:
      result[i.label()] = (i.getMeasuredVoltage(), i.getMeasuredCurrent())
    return result

  def recall(self, memory):
    for device in self.devices:
      device.recall(memory)
  
  def reconfigure(self, memory=None):
    self.E3631A.applySettings("P6V",1.2,0.001)
    self.E3631A.applySettings("P25V",5,0.05)
    self.E3631A.applySettings("M25V",-5,0.05)
    self.E3633A.applySettings("P20V",3.3,0.25)
    if memory is not None:
      device.save(memory)

  def turnOn(self):
    for device in self.devices:
      device.enable()

  def turnOff(self):
    for device in self.devices:
      device.disable()

#TODO method to know if each device is active or not
    
# Start the server
#server = SOAPpy.SOAPServer(("localhost", 8080))
#server.registerObject(aaptos())
#aaptos_instance = aaptos()
#server.registerObject(aaptos_instance, namespace="aaptos")
#server.registerObject(aaptos_instance.E3631A, namespace="E3631A")
#server.registerObject(aaptos_instance.E3633A, namespace="E3633A")
#server.registerObject(aaptos_instance.P6V, namespace="P6V")
#server.registerObject(aaptos_instance.P25V, namespace="P25V")
#server.registerObject(aaptos_instance.M25V, namespace="M25V")
#server.registerObject(aaptos_instance.P20V, namespace="P20V")
#server.serve_forever()

#example to use thread events to pause a thread: http://stackoverflow.com/questions/8103847/pausing-two-python-threads-while-a-third-one-does-stuff-with-locks

#TODO: move the main to another file

def main():

  class serverThread(Thread):
    def run(self):
      server = SOAPpy.SOAPServer(("localhost", 8080))
      server.registerObject(aaptos())
#TODO register a function to enable/disable the logging thread (via events, see example above)
      server.serve_forever()

  class loggerThread(Thread):
    def run(self):
      aaptos =  SOAPpy.SOAPProxy("http://localhost:8080/")
      dbstore = AaptosDb.DbStore()
      print "AAPTOS SOAP client for db logging started"
      while True:
        status = aaptos.getStatus()
        for device,values in status.iteritems():
          readings = supplyReadings()
          readings.instrument = device
          readings.voltage = values[0]
          readings.current = values[1]
          dbstore.add(readings)
        dbstore.commit()
        time.sleep(AaptosDb.pooldelay)
  
  serverThread().start()
  loggerThread().start()

#TODO investigate urwid as a third thread... or pyqt???
#purpose: display status; control on/off; enable/disable logging

if __name__ == '__main__':
    main()

