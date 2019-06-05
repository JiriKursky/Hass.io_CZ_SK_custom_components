# Sonata

Nahrazení doplňku MQTT přímou komunikací s Tasmotou
Používá sice konfiguraci MQTT na tasmmotě, ale komunikuje přes http na místní síti

Zatím absolutně bez kontroly, alfa verze
```yaml
user: access
# MQTT user
password: !secret password_mqtt
# MQTT heslo
sonoff:
    filtrace:
      url: 192.168.0.54
      # url zařízení
      
      control: input_boolean.test
      # čím bude ovládáno - musí existovat!
```yaml
