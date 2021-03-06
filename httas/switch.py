""" Using switch with direct http """
import logging
import async_timeout
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import (SwitchDevice, PLATFORM_SCHEMA)
from homeassistant.const import (CONF_PASSWORD, CONF_USERNAME, CONF_SWITCHES, CONF_FRIENDLY_NAME,
     CONF_IP_ADDRESS, CONF_SCAN_INTERVAL, DEVICE_CLASS_POWER)
from homeassistant.helpers.event import async_call_later
from inspect import currentframe, getframeinfo

DOMAIN = 'httas'
ENTITY_ID_FORMAT = 'switch.{}'

R_POWER = 'POWER'                   # Return json
CMND_POWER = 'POWER'                # Get info if is ON/OFF
CMND_POWER_ON = 'Power%20On'        # Comnmand to turn on
CMND_POWER_OFF = 'Power%20Off'      # Comnmand to turn off
MAX_LOST = 5                        # Can be lost in commincation

_LOGGER = logging.getLogger(__name__)
HTTP_TIMEOUT = 5

# Validation of the user's configuration
SWITCH_SCHEMA = vol.Schema({
    vol.Required(CONF_IP_ADDRESS): cv.string,    
    vol.Optional(CONF_FRIENDLY_NAME): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default = 30): vol.All(cv.positive_int, vol.Range(min=3, max=59))
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_USERNAME, default = ''): cv.string,    
    vol.Optional(CONF_PASSWORD, default = ''): cv.string,    
    vol.Optional(CONF_SWITCHES, default={}):
        cv.schema_with_slug_keys(SWITCH_SCHEMA),
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the platform - switches."""
 
    # Assign configuration variables.
    # The configuration check takes care they are present.

    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    switches = config.get(CONF_SWITCHES)    
    
    entities = []
    for object_id, pars in switches.items():                        
        base_url = "http://{}/cm?".format(pars[CONF_IP_ADDRESS])
        # username and passord is using only when protected internal
        if len(username)>0:
            base_url += '&user='+username
        if len(password)>0:
            base_url += '&password='+password

        base_url += '&cmnd='    
        entity = Sonoff(object_id, pars.get(CONF_FRIENDLY_NAME), base_url, pars)
        entities.append(entity)
    add_entities(entities)

class Sonoff(SwitchDevice):
    """ Main entity definition. There is only this one """
    def __init__(self, object_id, name, base_url, pars):       
        self.entity_id = ENTITY_ID_FORMAT.format(object_id)
        self._name = name
        self._base_url = base_url # necessary to put there command
        self._is_on = False
        self._scan_interval = pars.get(CONF_SCAN_INTERVAL) # checked in vol for value between 3 and 59
        self._ip_address = pars[CONF_IP_ADDRESS]      
        self._lost = 0
        self._lost_informed = False

    def _debug(self, s):
        cf = currentframe()
        line = cf.f_back.f_lineno
        if s is None:
             s = ''
        _LOGGER.debug("line: {} ip_address: {} msg: {}".format(line, self._ip_address, s))

    @property
    def name(self):
        """Name of the device."""
        return self._name

    @property
    def should_poll(self):
        """If entity should be polled."""
        # It can have its own timer according configuration
        return False
    
    def _to_get(self, cmnd):
        """ Get command including URL """
        return  self._base_url + cmnd        

    async def _send(self, cmnd):
        self._debug("Command: {}".format(cmnd))
        websession = async_get_clientsession(self.hass)                
        value = None
        try:
            with async_timeout.timeout(HTTP_TIMEOUT):            
                response = await websession.post(self._to_get(cmnd))                        
            if response is not None:
                try:                
                    value = await response.json()            
                except:            
                    value = None
        except:
            self._debug("Exception")             
        if value is None:
            return False
        else:
            self._debug("returned with success power: {}".format(value[R_POWER]))
            self._lost = 0
            if self._lost_informed:
                self.hass.components.persistent_notification.create(
                        "{} is ok. Scan interval is {} seconds now".format(self._ip_address, self._scan_interval),
                        title=DOMAIN)                
            self._lost_informed = False
            self._is_on = value[R_POWER] == 'ON'                  
            self.async_schedule_update_ha_state()
            return True                                                            
        
    async def _do_update(self):
        """ Returning current state of sensor """
        self._debug("do update")
        if await self._send(CMND_POWER):
            self._debug("scan interval: {}".format(self._scan_interval))
            async_call_later(self.hass, self._scan_interval, self._do_update())        
        else:
            scan_interval = 5
            if self._lost > MAX_LOST:
                scan_interval = 59
                if not self._lost_informed:
                    self.hass.components.persistent_notification.create(
                        "{} has permanent error.<br/>Please fix device. Scan interval is {} seconds now".format(self._ip_address, scan_interval),
                        title=DOMAIN)                
                    self._lost_informed = True
            else:
                self._lost += 1
            self._debug("no success scan interval is now {} seconds, losted {}".format(scan_interval, self._lost))            
            async_call_later(self.hass, scan_interval, self._do_update())                
        return True

    async def async_added_to_hass(self):        
        """Run when entity about to be added."""
        await super().async_added_to_hass()                
        self._debug("entity added to hass and starting update")
        await self._do_update()
    
    def _send_cmnd(self, cmnd):
        """ Sending to async with delay """
        self._debug("Sending later: {}".format(cmnd))
        async_call_later(self.hass, 0.2, self._send(cmnd))        

    @property
    def is_on(self):
        """If the switch is currently on or off."""        
        return self._is_on        

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._is_on = True
        self.async_schedule_update_ha_state()
        self._send_cmnd(CMND_POWER_ON)        

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._is_on = False
        self.async_schedule_update_ha_state()
        self._send_cmnd(CMND_POWER_OFF)        
        
    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_POWER