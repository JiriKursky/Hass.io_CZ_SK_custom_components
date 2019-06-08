# Sonata

Nahrazení doplňku MQTT přímou komunikací s Tasmotou
Používá sice konfiguraci MQTT na tasmotě, ale komunikuje přes http na místní síti

Zatím absolutně bez kontroly, alfa verze

dvě domény:

- sonoff:           - pro všechny ketré je potřeba zapínat a vypínat
- sonoff_sensor:    - se sensorem

přípustné hodnoty sensoru:
- sensor_temperature - teplota
- sensor_current proud
za ním následuje entita sensoru, nemusí existovat


*configuration.yaml*
```yaml
sonoff:
    filtrace:
      url: 192.168.X.XX
      name: Filtrace sonoff
      control: input_boolean.filtrace_zapni
    televize:
      name: TV sonoff
      url: 192.168.X.XX      
    subwoofer:
      name: Subwoofer
      url: 192.168.X.XX    
sonoff_sensor:
    cerpadlo:
      url: 192.168.X.XX
      name: Čerpadlo sonoff
      control: input_boolean.cerpadlo_zapni
      sensor_current: sensor.okamzity_proud_cerpadlo
    bazen_svetlo:
      url: 192.168.X.XX
      name: Bazen_svetlo sonoff
      control: input_boolean.bazen_svetlo_zapni
      sensor_temperature: sensor.teplota_bazen
#
input_boolean:
    filtrace_zapni: 
        name: Filtrace
    cerpadlo_zapni:
        name: Čerpadlo
```
a po restartu a zachování duševní rovnováhy přidejte na kartu mezi entities *input_boolean.filtrace_zapni* a *input_bolean.cerpadlo_zapni*
