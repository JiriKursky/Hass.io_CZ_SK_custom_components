# Sonata

Nahrazení doplňku MQTT přímou komunikací s Tasmotou

Komunikuje přes http na místní síti, MQTT může být vypnuto

jediné co potřebujete je ip na místní síti

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
- tam kde máte soubor *configuration.yaml" vytvořit adresář, pokud ho již nemáte *custom_components/sonata/*
