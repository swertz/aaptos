import npyscreen
from datetime import datetime
import threading
import time
        
#TODO: can change the widget: drop the label and use instead the title.
class PowerBox(npyscreen.BoxBasic):
    def __init__(self, screen, *args, **keywords):
        super(PowerBox, self).__init__(screen, *args, **keywords)
        self.make_contained_widgets()
        if 'value' in keywords:
            self.value = keywords['value']
        if 'values' in keywords:
            self.values = keywords['values']
    
    def make_contained_widgets(self):
        self._my_widgets = []
        labels = ["","Voltage","Current"]
        contained_widgets = [ npyscreen.FixedText, npyscreen.TitleSlider, npyscreen.TitleSlider ]
        for i,w in enumerate(contained_widgets):
          self._my_widgets.append(w(self.parent, 
           rely=self.rely+1+i, relx = self.relx+2, 
           max_width=self.width-4, max_height=self.height-2,
           name = labels[i]))
          self._my_widgets[-1].editable=False
          self._my_widgets[-1].scroll_exit=False
          self._my_widgets[-1].slow_scroll=False
        self.entry_widget = self._my_widgets[0]
        self._my_widgets[1].name = "Voltage"
        self._my_widgets[2].name = "Current"
            
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
        
    def get_value(self):
        if hasattr(self, 'entry_widget'):
            return self.entry_widget.value
        elif hasattr(self, '__tmp_value'):
            return self.__tmp_value
        else:
            return None

    def set_value(self, value):
        if hasattr(self, 'entry_widget'):
            self.entry_widget.value = value
        else:
            # probably trying to set the value before the textarea is initialised
            self.__tmp_value = value

    def del_value(self):
        del self.entry_widget.value
    value = property(get_value, set_value, del_value)
    
#TODO: use values[3,4] to store max voltage and max current.
    def get_values(self):
        if hasattr(self, 'entry_widget'): 
            return [self._my_widgets[1].value, self._my_widgets[2].value ]
        elif hasattr(self, '__tmp_value'):
            return self.__tmp_values
        else:
            return None
    def set_values(self, value):
        if hasattr(self, 'entry_widget'): 
            self._my_widgets[1].value = value[0]
            self._my_widgets[2].value = value[1]
        elif hasattr(self, '__tmp_value'):
            # probably trying to set the value before the textarea is initialised
            self.__tmp_values = value
    def del_values(self):
        del self._my_widgets[1].value
        del self._my_widgets[2].value
    values = property(get_values, set_values, del_values)
    
    def get_editable(self):
        return False

    def set_editable(self, value):
        pass

    def del_editable(self):
        del self.entry_widget.editable
    editable = property(get_editable, set_editable, del_editable)


    # This application class serves as a wrapper for the initialization of curses
    # and also manages the actual forms of the application

class MyTestApp(npyscreen.NPSAppManaged):

    keypress_timeout_default = 10

    def onStart(self):
        #self.registerForm("MAIN", MainForm(name = "Welcome to Aaptos"))
        self.addForm("MAIN", MainForm , name = "Welcome to Aaptos")

# This form class defines the display that will be presented to the user.

class MainForm(npyscreen.Form):

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
        self.PS1 = self.add(PowerBox, value="P6V",  values=[5,1.2], width=50, height=5, rely=rely)
        self.PS2 = self.add(PowerBox, value="P25V", values=[5,1.2], width=50, height=5, rely=rely, relx=55)
        rely = self.nextrely
        self.PS3 = self.add(PowerBox, value="M25V", values=[5,1.2], width=50, height=5, rely=rely)
        self.PS4 = self.add(PowerBox, value="P20V", values=[5,1.2], width=50, height=5, rely=rely, relx=55)
        self.nextrely += 2

        # options
        self.enablePower = self.add(npyscreen.RoundCheckBox, value=False, name="Enabled")
        self.remoteLock  = self.add(npyscreen.RoundCheckBox, value=False, name="Lock front panel")
        self.dblog       = self.add(npyscreen.RoundCheckBox, value=False, name="Log values")

#TODO: add a zone to display the logs and other messages

    def afterEditing(self):
        self.parentApp.setNextForm(None)

#TODO: add menu: settings (I,V for each, limits, etc.) , save, recall, quit

#TODO: add the method that reacts to changes in widgets and sends SOAP commands accordingly (enable/disable, lock
# also control the logger... this uses a threading.Event... how to communicate "outside"?

if __name__ == '__main__':
    TA = MyTestApp()
    TA.run()
