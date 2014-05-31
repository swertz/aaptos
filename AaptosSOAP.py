import SOAPpy
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
    
# Start the server
server = SOAPpy.SOAPServer(("localhost", 8080))
server.registerObject(aaptos())
#aaptos_instance = aaptos()
#server.registerObject(aaptos_instance, namespace="aaptos")
#server.registerObject(aaptos_instance.E3631A, namespace="E3631A")
#server.registerObject(aaptos_instance.E3633A, namespace="E3633A")
#server.registerObject(aaptos_instance.P6V, namespace="P6V")
#server.registerObject(aaptos_instance.P25V, namespace="P25V")
#server.registerObject(aaptos_instance.M25V, namespace="M25V")
#server.registerObject(aaptos_instance.P20V, namespace="P20V")
server.serve_forever()

#TODO: the server can be started as a thread, which would allow to start it together with the db in another thread
#import Queue
#import threading
#import urllib2
#
## called by each thread
#def get_url(q, url):
#    q.put(urllib2.urlopen(url).read())
#
#theurls = '''http://google.com http://yahoo.com'''.split()
#
#q = Queue.Queue()
#
#for u in theurls:
#    t = threading.Thread(target=get_url, args = (q,u))
#    t.daemon = True
#    t.start()
#
#s = q.get()
#print s

# another example:

#from threading import Thread
#
#class worker(Thread):
#    def run(self):
#    	for x in xrange(0,11):
#    		print x
#    		time.sleep(1)
#
#class waiter(Thread):
#    def run(self):
#    	for x in xrange(100,103):
#    		print x
#    		time.sleep(5)
#
#def run():
#    worker().start()
#    waiter().start()
