# Časovač pro řízení filtrace nebo čehokoli během dne
Navazuje na původní python_script verzi, která mi přišla šílená na instalaci

Postup:
zkopírovat odsud 

https://github.com/JiriKursky/Hass.io_CZ_SK_custom_components/tree/master/turnoffon

config/custom_components
vše do stejnojmenné složky

configuration.yaml:

```yaml```
turnoffon:
    filtrace:
      action_entity_id: input_boolean.filtrace_zapni
      timers: { "6:10":50, "10:10":30, "12:00":30, "13:10":2, "15:00":20, "17:00":20, "18:00":50, "20:00":30, "21:20":5 }      
      condition_run: input_boolean.filtrace_timer
    cerpadlo:
      action_entity_id: input_boolean.cerpadlo_zapni
      timers: { "6:05":15, "07:00":15, "08:05":15, "08:45":15, "09:30":15, "10:15":15, "14:00":15, "16:05":15, "18:00":15, "19:00":15, "20:15":15, "21:05":15, "22:15":15, "22:55":15 }      
      condition_run: input_boolean.cerpadlo_timer
    postrik_1:
      action_entity_id: input_boolean.postrikovac_1
      name: Spodek
      timers: { "12:00":"16:00","21:00":"22:00" }      
    postrik_2:
      action_entity_id: input_boolean.postrikovac_2
      name: Horejsek
      timers: { "8:00":"10:00","16:00":"18:00" }      
    postrik_3:
      action_entity_id: input_boolean.postrikovac_4
      name: Jahody
      timers: { "6:00":"8:00","18:00":"20:00" }      
    postrik_4:
      action_entity_id: input_boolean.postrikovac_3
      name: Zadek
      timers: { "10:00":"12:00","22:00":"23:59" }
```
