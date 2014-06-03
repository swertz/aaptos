import npyscreen
from datetime import datetime
import threading
import time
        
#####################################################
## Widgets - to be used: PowerBox
#####################################################

class GaugeWidget(npyscreen.Slider):
    """A slider with custom label"""
    def __init__(self, screen, *args, **keywords):
      super(GaugeWidget, self).__init__(screen, *args, **keywords)
      self.levels = (0,50,100, 100.1)
      self.unit = "a.u."
      if 'levels' in keywords:
        self.levels = keywords['levels']
      if 'unit' in keywords:
        self.unit = keywords['unit']

    def translate_value(self):
      stri = "%4.1f %s" % (self.value, self.unit)
      return stri

    def set_levels(self,levels):
      self.lowest = levels[0]
      self.warning = levels[1]
      self.maximum = levels[2]
      self.out_of = levels[3]
      self.step   = self.out_of/10.

    def get_levels(self):
      return (self.lowest, self.warning, self.maximum, self.out_of)

    levels = property(get_levels, set_levels)

    def set_value(self, val):
        #"We can only represent ints or floats, and must be less than what we are out of..."
        if val is None: val = 0
        if not isinstance(val, int) and not isinstance(val, float):
            raise ValueError

        else:
            self.__value = val

        if self.__value > self.out_of: raise ValueError
        if hasattr(self, 'levels'):
          if val < self.levels[1] :
            self.color = "SAFE"
          elif val < self.levels[2]:
            self.color = "WARNING"
          else:
            self.color = "DANGER"

    def get_value(self):
        return float(self.__value)

    value = property(get_value, set_value)


class TitleGauge(npyscreen.TitleText):
    _entry_type = GaugeWidget

    def set_levels(self,levels):
      self.entry_widget.set_levels(levels)

    def get_levels(self):
      return self.entry_widget.get_levels()

    levels = property(get_levels, set_levels)


class PowerBox(npyscreen.BoxBasic):
    """A widget combining Voltage and Current gauges"""

    def __init__(self, screen, *args, **keywords):
        """Initialize the widget. Relevant parameters are name, values, and levels.
           Levels is a pair of triplet (min, warning, max)."""
        super(PowerBox, self).__init__(screen, *args, **keywords)
        if 'levels' in keywords:
            self.levels_ = keywords['levels']
        else:
            self.levels_ = [(0,5,5,5), (0,0.5,1,2)]
        self.make_contained_widgets()
        if 'values' in keywords:
            self.values = keywords['values']
    
    def make_contained_widgets(self):
        self._my_widgets = []
        labels = ["Voltage","Current"]
        units  = ["V","A"]
        contained_widgets = [ TitleGauge, TitleGauge ]
        for i,w in enumerate(contained_widgets):
          self._my_widgets.append(w(self.parent, rely=self.rely+1+i, relx = self.relx+2, 
                                    max_width=self.width-4, max_height=self.height-2, name = labels[i], unit=units[i], levels=self.levels_[i]))
          self._my_widgets[-1].editable=False
          self._my_widgets[-1].scroll_exit=False
          self._my_widgets[-1].slow_scroll=False
            
    def update(self, clear=True):
        if self.hidden and clear:
            self.clear()
            return False
        elif self.hidden:
            return False
        super(PowerBox, self).update(clear=clear)
        for w in self._my_widgets:
            w.update(clear=clear)
            
    def resize(self):
        super(PowerBox, self).resize()
        for w in self._my_widgets:
            w.resize()
    
    def edit(self):
        self.editing=True
        self.display()
        self.editing=False
        self.display()
        
    def get_values(self):
        if hasattr(self, '_my_widgets'): 
            return [self._my_widgets[0].value, self._my_widgets[1].value ]
        elif hasattr(self, '__tmp_values'):
            return self.__tmp_values
        else:
            return None

    def set_values(self, values):
        if hasattr(self, '_my_widgets'): 
            self._my_widgets[0].value = values[0]
            self._my_widgets[1].value = values[1]
        elif hasattr(self, '__tmp_values'):
            # probably trying to set the value before the textarea is initialised
            self.__tmp_values = values

    def del_values(self):
        del self._my_widgets[0].value
        del self._my_widgets[1].value

    values = property(get_values, set_values, del_values)
    
    def get_levels(self):
        if hasattr(self, '_my_widgets'): 
            return [self._my_widgets[0].get_levels(), self._my_widgets[1].get_levels() ]
        elif hasattr(self, '__tmp_levels'):
            return self.__tmp_levels
        else:
            return None

    def set_levels(self, levels):
        if hasattr(self, '_my_widgets'): 
            self._my_widgets[0].set_levels(levels[0])
            self._my_widgets[1].set_levels(levels[1])
        elif hasattr(self, '__tmp_levels'):
            # probably trying to set the value before the textarea is initialised
            self.__tmp_levels = levels

    levels = property(get_levels, set_levels)

    def get_editable(self):
        return False

    def set_editable(self, value):
        pass

    def del_editable(self):
        pass

    editable = property(get_editable, set_editable, del_editable)

#####################################################
## App and Forms
#####################################################

class MyTestApp(npyscreen.NPSAppManaged):
    """This application class serves as a wrapper for the initialization of curses
       and also manages the actual forms of the application"""

    keypress_timeout_default = 10

    def onStart(self):
        #self.registerForm("MAIN", MainForm(name = "Welcome to Aaptos"))
        self.addForm("MAIN", MainForm , name = "Welcome to Aaptos")


class MainForm(npyscreen.Form):
#class MainForm(npyscreen.FormBaseNewWithMenus):
    """This form class defines the display that will be presented to the user."""

    def update_clock(self,period=1):
        while True:
          time.sleep(period)
          self.date_widget.value = datetime.now().strftime("%b %d %Y %H:%M:%S")
          self.display()
          #TODO: add the SOAPy loop to update the values on screen

    def create(self):
        # time info on top
        self.date_widget = self.add(npyscreen.FixedText, value=datetime.now().strftime("%b %d %Y %H:%M:%S"), editable=False)
        t = threading.Thread(target=MainForm.update_clock, args = (self,1))
        t.daemon = True
        t.start()
        self.nextrely += 1

        # name, voltage, current
        rely = self.nextrely
        self.PS1 = self.add(PowerBox, name="P6V",  levels=[(0,5,5,6),(0,1,1.5,2)], values=[5,1.2], width=50, height=4, rely=rely)
        self.PS2 = self.add(PowerBox, name="P25V", levels=[(0,5,5,6),(0,1,1.5,2)], values=[5,1.2], width=50, height=4, rely=rely, relx=55)
        rely = self.nextrely
        self.PS3 = self.add(PowerBox, name="M25V", levels=[(0,6,6,6),(0,1,1.5,2)], values=[5,1.2], width=50, height=4, rely=rely)
        self.PS4 = self.add(PowerBox, name="P20V", levels=[(0,6,6,6),(0,1,1.5,2)], values=[5,1.2], width=50, height=4, rely=rely, relx=55)
        self.nextrely += 2

        # options
        self.enablePower = self.add(npyscreen.RoundCheckBox, value=False, name="Enabled")
        self.remoteLock  = self.add(npyscreen.RoundCheckBox, value=False, name="Lock front panel")
        self.dblog       = self.add(npyscreen.RoundCheckBox, value=False, name="Log values")

#TODO: add a zone to display the logs and other messages

    def afterEditing(self):
        self.parentApp.setNextForm(None)

#TODO: add menu: settings (I,V for each, limits, etc.), SOAP server, save, recall, quit

#TODO: add the method that reacts to changes in widgets and sends SOAP commands accordingly (enable/disable, lock
# also control the logger... this uses a threading.Event... how to communicate "outside"?

if __name__ == '__main__':
    TA = MyTestApp()
    TA.run()
