from storm.locals import *
import time
import AaptosSOAP
import AaptosSettings

def DbStore(login=AaptosSettings.DbLogin, password=AaptosSettings.DbPassword, database=AaptosSettings.Database):
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

def main():
  """AAPTOS SOAP client for db logging of readings"""
  aaptos = AaptosSOAP.SOAPProxy("http://%s:%d/"%(AaptosSettings.SOAPServer,AaptosSettings.SOAPPort))
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
    time.sleep(AaptosSettings.PoolDelay)
      
if __name__ == '__main__':
    main()
