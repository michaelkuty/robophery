
import Adafruit_DHT
import robophery.gpio


class Dht22Module(gpio.GpioModule):

    DEVICE_NAME = 'gpio-dht22'


    def __init__(self, **kwargs):
        super(Dht22Module, self, **kwargs).__init__()
        self._pin = kwargs.get('pin')
        self._type = 22


    @property
    def get_data(self):
        """
        Query DHT22 to get the humidity and temperature readings.
        """
        data = []
        humidity, temperature = Adafruit_DHT.read_retry(self._type, self._pin)
        if temperature == None or humidity == None:
            self._log('error', 'Data CRC failed')
        else:
            if humidity > 0 and humidity < 100:
                data.append(('%s.temperature' % (self._name), temperature, ))
                data.append(('%s.humidity' % (self._name), humidity, ))
            else:
                self._log('error', 'Humidity out of range')
        return data


    @property
    def get_meta_data(self):
        """
        Get the readings meta-data.
        """
        return {
            'temperature': {
                'type': 'gauge', 
                'unit': 'C',
                'precision': 0.5,
                'range_low': -40,
                'range_high': 80,
                'sensor': 'dht22'
            },
            'humidity': {
                'type': 'gauge',
                'unit': 'RH',
                'precision': 5,
                'range_low': 0,
                'range_high': 100,
                'sensor': 'dht22'
            }
        }
