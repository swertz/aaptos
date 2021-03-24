import re
import random


class DummyInstrument:
    def __init__(self, index=0, label="", connection=None):
        self.index_ = index
        self.label_ = label
        self.isCurrent_ = index == 0
        self.current_ = 0.0
        self.voltage_ = 0.0
        self.maxv_ = re.findall(r"\d+", label)[0]
        self.connection = connection

    def label(self):
        return self.label_

    def __copy__(self):
        raise copy.error("DummyInstrument cannot be copied")

    def __deepcopy__(self, memo):
        raise copy.error("DummyInstrument cannot be copied")

    def isCurrent(self):
        return self.isCurrent_

    def makeCurrent(self):
        self.isCurrent_ = True

    def getMeasuredCurrent(self):
        if self.connection.state():
            return random.normalvariate(self.current_ / 2.0, 0.1)
        else:
            return 0.0

    def getMeasuredVoltage(self):
        if self.connection.state():
            return random.normalvariate(self.voltage_, 0.1)
        else:
            return 0.0

    def setCurrentLimit(self, current, triggered=False):
        self.makeCurrent()
        self.current_ = current

    def getCurrentLimit(self, triggered=False):
        self.makeCurrent()
        return self.current_

    def getMinCurrentLimit(self, triggered=False):
        """This query returns the minimum programmable current limit level of the selected output"""
        self.makeCurrent()
        return 0

    def getMaxCurrentLimit(self, triggered=False):
        """This query returns the maximum programmable current limit level of the selected output"""
        self.makeCurrent()
        return 5

    def setVoltage(self, voltage, triggered=False):
        self.makeCurrent()
        self.voltage_ = voltage

    def getVoltage(self, triggered=False):
        """This query returns the presently programmed voltage limit level of the selected output"""
        self.makeCurrent()
        return self.voltage_

    def getMinVoltage(self, triggered=False):
        """This query returns the minimum programmable voltage limit level of the selected output"""
        self.makeCurrent()
        return 0.0

    def getMaxVoltage(self, triggered=False):
        """This query returns the minimum programmable voltage limit level of the selected output"""
        self.makeCurrent()
        return 10.0
