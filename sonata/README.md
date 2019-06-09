# Sonata

Komunikace Sonoff jeden kanál s Tasmotou přes http

MQTT může být vypnuto

jediné co potřebujete je ip adresa na místní síti

příklad minimální konfigurace:

*configuration.yaml*
```yaml
switch:
    - platform: sonata
      switches:
        filtrace:
          ip_address: 192.168.XX.YY
```
Instalace:
- tam kde máte soubor *configuration.yaml* vytvořit adresář, pokud ho již nemáte *custom_components/sonata/*
- nakopírovat vše co je zde v adresáři 
- restart HA a úprava *configuration.yaml*
