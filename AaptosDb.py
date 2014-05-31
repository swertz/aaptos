# db interface to log readings: (time, instrument, V, I) for each instrument
# use the same library as SAMADHI

import SOAPpy
aaptos =  SOAPpy.SOAPProxy("http://localhost:8080/")
print aaptos.getStatus() #voltage and current for all instruments
aaptos.recall(1)
aaptos.turnOn()
print aaptos.getStatus() #voltage and current for all instruments

#more advanced queries
print aaptos.P6V.getMaxVoltage()
aaptos.E3631A.disableDisplay()

