# Sonata

Nahrazení doplňku MQTT přímou komunikací s Tasmotou

Komunikuje přes http na místní síti, MQTT může být vypnuto

příklad minimální konfigurace:

*configuration.yaml*
```yaml
switch:
    - platform: sonata
      switches:
        filtrace:
          ip_address: 192.168.X.XX
```
