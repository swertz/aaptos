import re
import SOAPpy
import AaptosSettings
from AgilentSCPI import AgilentSCPI
from AgilentE3631A import AgilentE3631A
from AgilentE3633A import AgilentE3633A

SOAPpy.Config.simplify_objects = 1


def AgilentFactory(port):
    device = AgilentSCPI(port)
    identity = device.identity()
    device.close()
    if "E3631A" in identity:
        return AgilentE3631A
    elif "E3633A" in identity:
        return AgilentE3633A
    else:
        raise RuntimeError("Unknown device: %s" % identity)


def increment(label):
    p = re.compile("(.+)_(\d+)$")
    if p.match(label) is None:
        return label + "_1"
    else:
        m = p.findall(label)
        return "%s_%d" % (m[0][0], int(m[0][1]) + 1)


class aaptos:
    def __init__(self):
        # devices
        self.devices = {}
        for dev in AaptosSettings.Devices:
            module = __import__(dev[1])
            class_ = getattr(module, dev[1])
            setattr(self, dev[0], class_(port=dev[2]))
            self.devices[dev[0]] = getattr(self, dev[0])
        for port in AaptosSettings.AutoDevices:
            class_ = AgilentFactory(port)
            label = AaptosSettings.autoNaming(port, class_.__name__)
            if hasattr(self, label):
                increment(label)
            setattr(self, label, class_(port))
            self.devices[label] = getattr(self, label)
        # instruments
        self.instruments = {}
        for devname, dev in self.devices.items():
            for label, inst in dev.instruments_.items():
                setattr(self, "%s_%s" % (devname, label), inst)
                self.instruments["%s_%s" % (devname, label)] = getattr(
                    self, "%s_%s" % (devname, label)
                )

    def getStatus(self):
        return {
            label: (i.getMeasuredVoltage(), i.getMeasuredCurrent())
            for label, i in self.instruments.items()
        }

    def getErrors(self):
        return {label: device.getErrors() for label, device in self.devices.items()}

    def getDevices(self):
        return list(self.devices.keys())

    def configureInstrument(self, instrument, V, I, triggered=False):
        getattr(self, instrument).setVoltage(V, triggered)
        getattr(self, instrument).setCurrentLimit(I, triggered)

    def getInstrumentConfiguration(self, instrument, triggered=False):
        instr = getattr(self, instrument)
        return (instr.getVoltage(triggered), instr.getCurrentLimit(triggered))

    def recall(self, memory):
        for device in list(self.devices.values()):
            device.recall(memory)

    def save(self, memory):
        for device in list(self.devices.values()):
            device.save(memory)

    def turnOn(self):
        for device in list(self.devices.values()):
            device.enable()
            device.displayMessage("AAPTOS ON")

    def turnOff(self):
        for device in list(self.devices.values()):
            device.disable()
            device.displayMessage("AAPTOS OFF")

    def isOn(self):
        output = True
        for device in list(self.devices.values()):
            output &= int(device.state())
        return output

    def lock(self, yesno):
        for device in list(self.devices.values()):
            device.setRemote(locked=yesno)


class SOAPServer(SOAPpy.SOAPServer):
    pass


class SOAPProxy(SOAPpy.SOAPProxy):
    pass


def main():
    # Start the server
    server = SOAPServer((AaptosSettings.SOAPServer, AaptosSettings.SOAPPort))
    server.registerObject(aaptos())
    # server.config.dumpSOAPIn = 1
    # server.config.dumpSOAPOut = 1

    # aaptos_instance = aaptos()
    # server.registerObject(aaptos_instance, namespace="aaptos")
    # server.registerObject(aaptos_instance.E3631A, namespace="E3631A")
    # server.registerObject(aaptos_instance.E3633A, namespace="E3633A")
    # server.registerObject(aaptos_instance.P6V, namespace="P6V")
    # server.registerObject(aaptos_instance.P25V, namespace="P25V")
    # server.registerObject(aaptos_instance.N25V, namespace="N25V")
    # server.registerObject(aaptos_instance.P20V, namespace="P20V")
    server.serve_forever()


if __name__ == "__main__":
    main()
