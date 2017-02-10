
import robophery.gpio


class SwitchModule(gpio.GpioModule):

    DEVICE_NAME = 'gpio-switch'


    def __init__(self, **kwargs):
        super(SwitchModule, self, **kwargs).__init__()
        self._pin = kwargs.get('pin')
        self.set_input(self._pin)


    @property
    def get_data(self):
        """
        Switch status readings.
        """
        state = self.input(self._pin)
        press_count = press_delta = state
        data = [
            ('%s.press_count' % self._name, press_count, ),
            ('%s.press_delta' % self._name, press_delta, ),
        ]
        return data


    @property
    def get_meta_data(self):
        """
        Get the readings meta-data.
        """
        return {
            'press_count': {
                'type': 'counter',
                'unit': 's',
                'precision': 0.1,
                'range_low': 0,
                'range_high': None,
                'sensor': 'switch'
            },
            'press_delta': {
                'type': 'delta',
                'unit': 's',
                'precision': 0.1,
                'range_low': 0,
                'range_high': None,
                'sensor': 'switch'
            }
        }
