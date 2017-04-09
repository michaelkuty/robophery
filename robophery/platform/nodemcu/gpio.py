from machine import Pin
from robophery.interface.gpio import GpioInterface
from robotparser.compat import const


class NodeMcuGpioInterface(GpioInterface):
    """
    GPIO implementation for the NodeMCU.
    """
    NODEMCU_GPIO_COUNT = const(15)

    def __init__(self, *args, **kwargs):
        from machine import Pin
        #TODO Pin.ALT and PULL_DOWN check in next micropython releases if they are already implemented
        self._dir_mapping = { self.GPIO_MODE_OUT: Pin.OUT,
                              self.GPIO_MODE_IN: Pin.IN,
                              self.GPIO_MODE_ALT: -1,
                              self.GPIO_MODE_NONE: -1 }
        self._pud_mapping = { self.GPIO_PUD_OFF: None,
                              self.GPIO_PUD_DOWN: None,
                              self.GPIO_PUD_UP: Pin.PULL_UP }
        self._edge_mapping = { self.GPIO_EVENT_NONE: -1,
                               self.GPIO_EVENT_RISING: Pin.IRQ_RISING,
                               self.GPIO_EVENT_FALLING: Pin.IRQ_FALLING,
                               self.GPIO_EVENT_BOTH: Pin.IRQ_FALLING|Pin.IRQ_RISING }
        self._pins_irq = {}
        self._pins_irq_triggers = {}

        super(NodeMcuGpioInterface, self).__init__(num_gpio=self.NODEMCU_GPIO_COUNT, *args, **kwargs)


    def setup_pin(self, pin, mode=None, pull_up_down=None, init_value=False):
        """
        Set the input or output mode for a specified pin. Mode should be
        either OUTPUT or INPUT.
        """
        if mode is None:
            mode = self.GPIO_MODE_NONE
        if pull_up_down is None:
            pull_up_down = self.GPIO_PUD_OFF

        self._pins[pin] = Pin(pin,
                              mode=self._dir_mapping[mode],
                              pull=self._pud_mapping[pull_up_down],
                              value=init_value)

        self._pins_irq[pin] = PinIrq()

    def get_pin(self, pin):
        """
        Return pin object specified by its number
        """
        if pin in self._pins.keys():
            return self._pins[pin]
        else:
            return 'None'

    def output(self, pin, value):
        """
        Set the specified pin the provided high/low value. Value should be
        either HIGH/LOW or a boolean (true = high).
        """
        self._pins[pin].value(value)

    def input(self, pin):
        """
        Read the specified pin and return HIGH/true if the pin is pulled high,
        or LOW/false if pulled low.
        """
        return self._pins[pin].value()

    def input_pins(self, pins):
        """
        Read multiple pins specified in the given list and return list of pin values
        GPIO.HIGH/True if the pin is pulled high, or GPIO.LOW/False if pulled low.
        """
        return [self._pins[pin].value() for pin in pins]

    def add_event_detect(self, pin, edge, callback=None, bouncetime=-1, priority=1):
        """
        Enable edge detection events for a particular GPIO channel. Pin 
        should be type IN. Edge must be RISING or FALLING. Callback is a
        function for the event. Bouncetime is switch bounce timeout in ms for 
        callback.
        """
        if callback is not None:
            self._pins_irq[pin].setup_callback(callback)
        self._pins_irq_triggers[pin] = self._edge_mapping[edge]
        self._pins[pin].irq(handler=self._pins_irq[pin].irq_handler, 
                            trigger=self._pins_irq_triggers[pin])


    def remove_event_detect(self, pin):
        """
        Remove edge detection for a particular GPIO channel. Pin should be
        type IN.
        """
        if pin in self._pins_irq_triggers.keys():
            del(self._pins_irq_triggers[pin]) 
        self._pins_irq[pin].clear_event_detect()
        self._pins[pin].irq(trigger=self._edge_mapping[self.GPIO_EVENT_NONE])
                          

    def add_event_callback(self, pin, callback, bouncetime=-1, priority=1):
        """
        Add a callback for an event already defined using add_event_detect().
        Pin should be type IN.  Bouncetime is switch bounce timeout in ms for 
        callback
        """
        self._pins_irq[pin].setup_callback(callback)

    def event_detected(self, pin):
        """
        Returns True if an edge has occured on a given GPIO.  You need to 
        enable edge detection using add_event_detect() first.   Pin should be 
        type IN.
        """
        return self._pins_irq[pin].is_event_detected()

    def wait_for_edge(self, pin, edge):
        """
        Wait for an edge.   Pin should be type IN.  Edge must be RISING, 
        FALLING or BOTH.
        """
        while self._pins_irq[pin].is_event_detected() is False:
            # TODO timeout
            pass


class PinIrq():
    def __init__(self, callback=None):
        self._pin_event_detected = False
        self._callback = callback


    def clear_event_detect(self):
        self._pin_event_detected = False
        self._callback = None


    def is_event_detected(self):
        if self._pin_event_detected is True:
            self._pin_event_detected = False
            return True
        else:
            return False

    def setup_callback(self, callback):
        self._callback = callback

    def irq_handler(self, pin):
        self._pin_event_detected = True
        if self._callback is not None:
            self._callback()
