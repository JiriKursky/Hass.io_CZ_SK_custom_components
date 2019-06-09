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
- tam kde máte soubor *configuration.yaml* vytvořit složku, pokud ji již nemáte *custom_components* a do ní přidat složku *sonata*
- nakopírovat vše co je zde v adresáři 
- restart HA a úprava *configuration.yaml*
