import SOAPpy
import time
import AaptosDb
import AaptosSOAP
from threading import Thread

#example to use thread events to pause a thread: http://stackoverflow.com/questions/8103847/pausing-two-python-threads-while-a-third-one-does-stuff-with-locks

def main():

  class serverThread(Thread):
    def run(self):
      server = SOAPpy.SOAPServer(("localhost", 8080))
      server.registerObject(aaptos())
      print "AAPTOS SOAP server started."
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
          readings = AaptosDb.supplyReadings()
          readings.instrument = device
          readings.voltage = values[0]
          readings.current = values[1]
          dbstore.add(readings)
        dbstore.commit()
        time.sleep(AaptosDb.pooldelay)

  class cliThread(Thread):
    def run(self):
      aaptos =  SOAPpy.SOAPProxy("http://localhost:8080/")
      #wait to let other threads start. 
      #TODO: use signaling instead
      print "Welcome"
      while True:
        sleep(5)
        status = aaptos.getStatus()
        print "Status: " 
        for device,values in status.iteritems():
          message = "%s: V=%3.2f, I=%3.2f" % (device,values[0],values[1])
          print (message, end="\r")

  
  serverThread().start()
  loggerThread().start()
  cliThread().start()

#TODO investigate urwid as a third thread... or pyqt??? or curses, simply.
#https://docs.python.org/2/howto/curses.html
#purpose: display status; control on/off; enable/disable logging

if __name__ == '__main__':
    main()

