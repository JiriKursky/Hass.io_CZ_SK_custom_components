# Sonata

Nahrazení doplňku MQTT přímou komunikací s Tasmotou

Zatím absolutně bez kontroly, alfa verze
```yaml
user: access
password: !secret password_mqtt
sonoff:
    filtrace:
      url: 192.168.0.54
      # url zařízení
      
      control: input_boolean.test
      # čím bude ovládáno - musí existovat!
```yaml
