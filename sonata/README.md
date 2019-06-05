# Sonata

Nahrazení doplňku MQTT přímou komunikací s Tasmotou
Používá sice konfiguraci MQTT na tasmotě, ale komunikuje přes http na místní síti

Zatím absolutně bez kontroly, alfa verze
*configuration.yaml*
```yaml
sonata:
    user: access
    # MQTT user
    password: !secret password_mqtt
    # MQTT heslo
    sonoff:
        filtrace:
            url: 192.168.0.54
            # url zařízení
            #
            control: input_boolean.test
            # čím bude ovládáno - musí existovat!
#
input_boolean:
    test:
        name: Volunteer
```yaml

a po restartu a zachování duševní rovnováhy přidejte na kartu mezi entities *imput_boolean.test* a pro kontrolu *sonata.filtrace*
