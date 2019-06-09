# Sonata

Komunikace Sonoff jeden kanál s Tasmotou přes http

MQTT může být vypnuto

jediné co potřebujete je ip adresa na místní síti

Pro test můžete zkusit
- http://ip_zarizeni/cm?&cmnd=POWER
- pokud bude odpověděď ve stylu {"POWER":"OFF"} nebo {"POWER":"ON"} mělo by to fungovat


příklad minimální konfigurace:

*configuration.yaml*
```yaml
switch:
    - platform: sonata
      switches:
        muj_switch:
          ip_address: ip_zarizeni
```
Instalace:
- tam kde máte soubor *configuration.yaml* vytvořit složku, pokud ji již nemáte *custom_components* a do ní přidat složku *sonata*
- nakopírovat vše co je zde v adresáři 
- restart HA a úprava *configuration.yaml* v sekci *switch* viz výše, další se přidávají pod sebe
- znovu restart HA a měl by být k dispozici například *switch.muj_switch*.
