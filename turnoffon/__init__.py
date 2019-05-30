import logging
import datetime
import time

import voluptuous as vol

from homeassistant.const import ATTR_ENTITY_ID, CONF_ICON, CONF_NAME, SERVICE_TURN_ON, SERVICE_TURN_OFF
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util
from homeassistant.core import split_entity_id
from homeassistant.helpers.event import async_track_time_interval


DOMAIN = 'turnoffon'

CONF_CASY = 'timers'
CONF_ACTION_ENTITY_ID = 'action_entity_id'
CONF_COMMAND_ON = 'command_on'
CONF_COMMAND_OFF = 'command_off'
CONF_CONDITION = 'condition_run'

# Navratove hodnoty z run_casovac
R_HASS = 'HASS'
R_TODO = 'TO_DO'
R_ENTITY_ID = "ENTITY_ID"

# Nazvy attributu
ATTR_ZACATEK = 'start_time'
ATTR_KONEC = 'konec'

# Konstanta definice sluzby
SERVICE_RUN_CASOVAC = 'run_turnoffon'
SERVICE_SET_CASOVAC_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTITY_ID): cv.entity_id
})


# Konstanta definice sluzby
SERVICE_SET_TIME = 'set_time'
SERVICE_SET_TIME_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTITY_ID): cv.entity_id,
    vol.Optional(ATTR_ZACATEK): cv.time,
    vol.Optional(ATTR_KONEC): cv.time,    
})

_LOGGER = logging.getLogger(__name__)
ENTITY_ID_FORMAT = DOMAIN + '.{}'

ERR_CONFIG_TIME_SCHEMA = 'Chybne zadefinovane casy'
ERR_CONFIG_TIME_2 = 'Delka musi byt v rozsahu 1 - 59'

def kontrolaCasy(hodnota):
    try:    
        for start, cosi in hodnota.items():        
            cv.time(start)        
            if  isinstance(cosi, int):                
                if (cosi<0) or (cosi > 59):
                    raise vol.Invalid(ERR_CONFIG_TIME_2)    
            else:                
                cv.time(cosi)            
        return hodnota
    except:
        raise vol.Invalid(ERR_CONFIG_TIME_SCHEMA)    
        
        

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: cv.schema_with_slug_keys(
        vol.All({                        
            vol.Required(CONF_CASY): kontrolaCasy,
            vol.Required(CONF_ACTION_ENTITY_ID): cv.entity_id,            
            vol.Optional(CONF_CONDITION): cv.entity_id,
            vol.Optional(CONF_NAME): cv.string,
            vol.Optional(CONF_COMMAND_ON, default = SERVICE_TURN_ON): cv.string,
            vol.Optional(CONF_COMMAND_OFF, default = SERVICE_TURN_OFF): cv.string
        })
    )
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    """Uvodni nastaveni pri zavedeni."""
    component = EntityComponent(_LOGGER, DOMAIN, hass)

    entities = []

    # Nacteni konfigurace
    for name, cfg in config[DOMAIN].items():                
        casy = cfg.get(CONF_CASY)

        # citac
        i = 0    
        for zacatek, delka in casy.items():
            i = i + 1
            sI = "_" + str(i)            
            entities.append(Casovac(hass, name + sI, name + sI, zacatek, delka))

        object_id = name
        name = cfg.get(CONF_NAME)
        if name == None:
            name = object_id
        casovacHlavni = CasovacHlavni(hass, object_id, name, i, cfg)
        
        async_track_time_interval(hass,casovacHlavni.pravidelny_interval, datetime.timedelta(minutes = 1))
        
        entities.append(casovacHlavni)        
    if not entities:
        return False
    _LOGGER.info('Zaregistrovan casovac. Celkem: ' + str(i))

    # Musi byt pridano az po definici vyse - je potreba znat pocet zaregistrovanych casovacu


    async def async_run_casovac_service(entity, call):
        """Spusteni behu."""        
        _LOGGER.debug("Volam hledani")
        retVal = entity.run_casovac()
        _LOGGER.debug("Navrat:")
        _LOGGER.debug(retVal)
        hass = retVal[R_HASS]
        target_domain, _ = split_entity_id(retVal[R_ENTITY_ID])

        # volam sluzbu               
        await hass.services.async_call(target_domain, retVal[R_TODO], { "entity_id": retVal[R_ENTITY_ID] }, False)

    async def async_set_time_service(entity, call):
        """Spusteni behu."""
        zacatek = call.data.get(ATTR_ZACATEK)
        konec = call.data.get(ATTR_KONEC)        
        entity.async_set_time(zacatek, konec)        

    # Velmi nebezpecna registrace - zde udelat chybu pri volani druheho parametru hrozi spadnuti celeho systemu
    component.async_register_entity_service(
        SERVICE_RUN_CASOVAC, SERVICE_SET_CASOVAC_SCHEMA, 
        async_run_casovac_service
    )

    component.async_register_entity_service(
        SERVICE_SET_TIME, SERVICE_SET_TIME_SCHEMA, 
        async_set_time_service
    )

    await component.async_add_entities(entities)
    return True

def prevedCasPar(sCas, praveTed):
    tCas = time.strptime(sCas, '%H:%M')         
    praveTed = datetime.datetime.now()    
    return praveTed.replace(hour=tCas.tm_hour, minute=tCas.tm_min, second=0)

def prevedCas(sCas):
    return prevedCasPar(sCas,  datetime.datetime.now())

def zobrazCas(tCas):
    return tCas.strftime('%H:%M')

class CasovacHlavni(RestoreEntity):
    def __init__(self, hass, object_id, name, pocet, cfg):
        """Inicializace hlavni ridici class"""
        self.entity_id = ENTITY_ID_FORMAT.format(object_id) # definice identifikatoru
        self._name = name                                   # friendly_name
        self._pocet = pocet                                 # pocet zadefinovanych casovacu
        self._cfg = cfg                                     # konfigurace v dane domene
        self._hass = hass                                   # uschovani classu hass

    @property
    def should_poll(self):
        """If entity should be polled."""
        return False

    @property
    def name(self):
        """Navrat nazvu hlavniho casovace"""
        return self._name

    def pravidelny_interval(self, now):        
        _LOGGER.debug("Pravidelny interval:" + self.entity_id)
        podminka = self._cfg.get(CONF_CONDITION)
        if podminka != None:
            if self.hass.states.get(podminka).state != "on":                
                _LOGGER.debug("Podminka shodila volani")
                return        
        _LOGGER.debug("Volam sluzbu "+ DOMAIN + " - " + SERVICE_RUN_CASOVAC + " pro: " + self.entity_id)
        self._hass.services.call(DOMAIN, SERVICE_RUN_CASOVAC, { "entity_id": self.entity_id }, False) 

    @property
    def state(self):
        """Return the state of the component."""
        return "on"

    def run_casovac(self):        
        """ Hlavni funkce ktera vraci jaka sluzba se bude volat v zavislosti na casovych intervalech """
        
        _LOGGER.debug("Hledam aktivni interval pro: "+self.entity_id)

        # Vlastni hledani aktivniho intervalu
        i = 1
        hledam = True
        praveTed = datetime.datetime.now() 

        while hledam and i <= self._pocet:        
            entity_id = self.entity_id + '_' + str(i)                    
            attr = self.hass.states.get(entity_id).attributes
            zacatek = attr[ATTR_ZACATEK]
            konec = attr[ATTR_KONEC]
            if (praveTed >= prevedCasPar(zacatek, praveTed)) and (praveTed <= prevedCasPar(konec, praveTed)):        
                # aktivni cas a nasel jsem
                hledam = False
            i = i + 1

        # V zavislosti je-li v casovem intervalu spoustim prikaz
        if hledam :
            toDo =self._cfg.get(CONF_COMMAND_OFF)
        else:
            toDo =self._cfg.get(CONF_COMMAND_ON)

        # navratova hodnota
        retVal = {
            R_HASS: self.hass,                                  # mozna to jde jinak, ale neumim            
            R_TODO: toDo,                                       # volany prikaz (turn_off/turn_on)
            R_ENTITY_ID: self._cfg.get(CONF_ACTION_ENTITY_ID)   # volana entita
        }        
        self.async_schedule_update_ha_state()                        
        return retVal


    def async_set_time(self, zacatek, konec):
        """ Prazdna funkce v pripade volani pro tuto entitu """ 
        return


class Casovac(RestoreEntity):
    """Casovac entita pro jednotlive zadefinovane casy."""

    def __init__(self, hass, object_id, name, zacatek, delka):
        """Inicializace casovac"""
        self.entity_id = ENTITY_ID_FORMAT.format(object_id)
        self._name = name
        self._zacatek = zacatek  # zacatek casoveho intervalu

        if isinstance(delka, int):
            tKonec = prevedCas(zacatek) + datetime.timedelta(minutes = delka)
            self._konec = zobrazCas(tKonec)                
        else:
            self._konec = delka
        
    async def async_added_to_hass(self):
      """Run when entity about to be added."""
      await super().async_added_to_hass()

    @property
    def should_poll(self):
        """If entity should be polled."""
        return False

    @property
    def name(self):
        """Navrat jmena pro Casovac."""
        return self._name

    @property
    def state(self):
        """Return the state of the component."""
        return self._zacatek + " - " + self._konec


    @property
    def state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_ZACATEK: self._zacatek,
            ATTR_KONEC: self._konec            
        }
        return attrs

    def async_set_time(self, zacatek, konec):
        """ Sluzba uvnitr jednotliveho casovace. Zatim neaktivni."""
        self._zacatek = zacatek
        self._konec = konec        
        self.async_schedule_update_ha_state()

    def async_run_casovac(self):
        """V tomto pripade se nepouziva."""
        return 
