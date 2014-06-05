from storm.locals import *
import AaptosSOAP
import time

def DbStore(login="aaptos", password="aaptos", database="localhost/aaptos"):
  """create a database object and returns the db store from STORM"""
  database = create_database("mysql://"+login+":"+password+"@"+database)
  return Store(database)

class supplyReadings(Storm):
  """Table to record readings from the power supplies"""
  __storm_table__ = "supplyReadings"
  reading = Int(primary=True)
  reading_time = DateTime()
  instrument = Unicode()
  voltage = Float()
  current = Float()

  def __str__(self):
    result = "%s: V=%3.2f I=%3.2f at %s" % (str(self.instrument), self.voltage, self.current, str(self.reading_time))
    return result

pooldelay=1

def main():
  """AAPTOS SOAP client for db logging of readings"""
  aaptos =  AaptosSOAP.SOAPProxy("http://localhost:8080/")
  dbstore = DbStore()
  print "AAPTOS SOAP client for db logging started"
  while True:
    status = aaptos.getStatus()
    for device,values in status.iteritems():
      readings = supplyReadings()
      readings.instrument = unicode(device)
      readings.voltage = values[0]
      readings.current = values[1]
      dbstore.add(readings)
    dbstore.commit()
    time.sleep(pooldelay)
      
  #aaptos.recall(1)
  #aaptos.turnOn()
  ##more advanced queries
  #print aaptos.P6V.getMaxVoltage()
  #aaptos.E3631A.disableDisplay()

if __name__ == '__main__':
    main()
