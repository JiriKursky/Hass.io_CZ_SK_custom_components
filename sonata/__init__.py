import logging 
import json
import requests
import datetime
import time

from homeassistant.const import ATTR_ENTITY_ID, CONF_ICON, CONF_NAME, SERVICE_TURN_ON, SERVICE_TURN_OFF, STATE_ON, STATE_OFF, EVENT_COMPONENT_LOADED, EVENT_STATE_CHANGED
from homeassistant.setup import ATTR_COMPONENT
from homeassistant.core import callback
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.event import async_call_later, async_track_time_interval
import homeassistant.components.input_boolean as input_boolean


DOMAIN = 'sonata'
ENTITY_ID_FORMAT = DOMAIN + '.{}'
_LOGGER = logging.getLogger(__name__)

CONF_URL = 'url'
CONF_USER = 'user'
CONF_PASSWORD = 'password'
CONF_CONTROL = 'control'
CONF_ENTITY_SONOFF = 'sonoff'

CMND_STATUS = 'status%208'
CMND_POWER = 'POWER'
CMND_POWER_ON = 'Power%20On'
CMND_POWER_OFF = 'Power%20Off'

LI_NO_DEFINITION = 'No entity added'

R_STATUS_CODE = 'STATUS_CODE'
R_CONTENT = 'CONTENT'
R_POWER = 'POWER'

O_CHILDREN = 'CHILDREN'

TIME_INTERVAL_DEVICE_ON = 3
TIME_INTERVAL_DEVICE_STATUS = 8
TIME_INTERVAL_DEVICE_ERROR = 30

S_VOLTAGE = 'Voltage'
S_CURRENT = 'Current'

async def async_setup(hass, config) :
    """Starting."""
    component = EntityComponent(_LOGGER, DOMAIN, hass)


    hass.data[DOMAIN] = { O_CHILDREN: {} }

    entities = []

    
    for key, cfg in config[DOMAIN].items():
        if key != CONF_ENTITY_SONOFF:            
            hass.data[DOMAIN][key]=cfg

    # Reading in config
    _LOGGER.debug('-------------')
    _LOGGER.debug(config[DOMAIN])
    for key, cfg in config[DOMAIN].items():
        if key == CONF_ENTITY_SONOFF:
            for object_id, object_cfg in cfg.items():
                entity = sonoff_basic(hass, object_id, object_cfg)
                hass.data[DOMAIN][O_CHILDREN][object_id] = entity
                _LOGGER.info('Setting up ' + object_id)
                entities.append(entity)                    
    if not entities:
        _LOGGER.info(LI_NO_DEFINITION)    
        return False
    await component.async_add_entities(entities)       



    # This is not necessary however to be sure
    timer_defined = False     
    @callback       
    def component_loaded(event):
        """Handle a new component loaded."""   
        nonlocal timer_defined    
        component_name = event.data[ATTR_COMPONENT]
        if (component_name == DOMAIN) :
            _LOGGER.debug("My component loaded: "+component_name)
            if timer_defined:
                return
            timer_defined = True
            # Prevent to more calling - dangerous, but should not happened
            for entity in entities :
                _LOGGER.debug("15 seconds to start")                                
                async_call_later(hass, 15, entity.start_time_interval)                
    
    # fired in courutine _async_setup_component setup.py
    hass.bus.async_listen_once(EVENT_COMPONENT_LOADED, component_loaded)    
    
    return True


class _httpClass :
    def __init__(self, base_url):
        self._base_url = base_url                

    def _transfer_to_json(self, source) :
        """ Byte transforming to json. """
        my_json = source.decode('utf8').replace("'", '"')
        return json.loads(my_json)    

    def get_response(self, cmnd) :
        """
        Checked for state - ok        
        r.status_code
        r.headers
        r.content
        """
        to_get = self._base_url + cmnd
        _LOGGER.debug("to get:" + to_get)
        
        retVal = { R_STATUS_CODE: False, R_CONTENT: {} }

        try:
            r = requests.get(to_get)            
            if r.status_code == 200:
                retVal[R_STATUS_CODE] = True
                retVal[R_CONTENT] = self._transfer_to_json(r.content)
        except:
            retVal[R_STATUS_CODE] = False
        return retVal
    
    def get_state(self):
        retVal = STATE_OFF
        result = self.get_response(CMND_POWER)
        _LOGGER.debug(result)
        if result[R_STATUS_CODE]:
            if result[R_CONTENT][R_POWER] == 'ON':
                retVal = STATE_ON
        else:
            retVal = None
        return retVal

    def turn_on(self):
        retVal = self.get_response(CMND_POWER_ON)
        return retVal

    def turn_off(self):
        retVal = self.get_response(CMND_POWER_OFF)
        return retVal

class sonoff_basic(RestoreEntity) :        
    def __init__(self, hass, object_id, cfg):                
        self._hass = hass
        self.entity_id = ENTITY_ID_FORMAT.format(object_id)     # definice identifikatoru        
        self._name = cfg.get(CONF_NAME)
        if self._name is None:
            self._name = object_id
        self._url = cfg.get(CONF_URL)
        self._user = hass.data[DOMAIN][CONF_USER]
        self._password = hass.data[DOMAIN][CONF_PASSWORD]
        self._http_class =_httpClass('http://'+self._url+'/cm?&user='+self._user+'&password='+self._password+'&cmnd=')        
        self._state = None
        self._control = cfg.get(CONF_CONTROL)
        self._time_interval_running = False
        self._time_delay = TIME_INTERVAL_DEVICE_STATUS
        self._time_error_delay = TIME_INTERVAL_DEVICE_ERROR
        self._refresh_state(False)                

    @property
    def time_delay(self):
        return self._time_delay

    @time_delay.setter
    def set_time_delay(self, time_delay) :
        self._time_delay = time_delay

    @property
    def time_error_delay(self):
        return self._time_error_delay

    @time_error_delay.setter
    def set_time_error_delay(self, time_delay) :
        self._time_error_delay = time_delay

    def set_turn_on(self):
        raise ValueError('For children entity not allowed')

    def set_turn_off(self):
        raise ValueError('For children entity not allowed')

    @property
    def is_on(self):
        """Return true if entity is on."""
        return self._state

    @property
    def name(self):
        """Get friendly name"""
        return self._name

    @property
    def should_poll(self):
        """If entity should be polled."""        
        return False

    def get_state(self) :
        return self._http_class.get_state()
        
    def _refresh_state(self, publish):        
        new_state = self.get_state()
        if new_state is None :
            new_state = "N/A"
            return False
        if self._state != new_state:            
            self._state = new_state                
            if publish:
                 self.async_schedule_update_ha_state()
        return True

    def handle_event(self, event):        
        if event.data.get('entity_id') != self._control:
            return
        if input_boolean.is_on(self.hass, self._control):
            _LOGGER.debug('state on')
            retVal = self._http_class.turn_on()        
        else:
            _LOGGER.debug('state off')
            retVal = self._http_class.turn_off()
        self._refresh_state(True)
    
    def start_time_interval(self, now):                        
        self.hass.bus.async_listen(EVENT_STATE_CHANGED, self.handle_event)
        self.time_interval(now)

    def time_interval(self, now):                        
        """Regular called"""
        # missing of parameter 'now' caused not working without warning
        # not async!
        

        def _repeat_call(*time_delay):            
            if len(time_delay) == 0:
                 _time_delay = self.time_delay
            else:
                _time_delay = time_delay[0]
            async_call_later(self._hass, _time_delay, self.time_interval)
            self._time_interval_running = False
            # To be sure
            return True
        
        # Just to avoid cycle, can be omitted...maybe
        if self._time_interval_running:
             return True
        self._time_interval_running = True        
        if self._refresh_state(True):
            return _repeat_call()
        else:
            _LOGGER.error("Timeout trying for 30 seconds")        
            return _repeat_call(self.time_error_delay)            
        
    @property
    def state(self):
        """Return the state of the component."""                                
        return self._state    
        
class sonoff_POW(sonoff_basic):
    @property
    def state_attributes(self):
        """Return the state attributes."""
        attrs = {}
        return attrs