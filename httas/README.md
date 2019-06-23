# Httas

Komunikace Sonoff jeden kanál s Tasmotou přes http 

MQTT může být vypnuto

jediné co potřebujete je ip adresa na místní síti

Pro test můžete zkusit
- http://ip_zarizeni/cm?&cmnd=POWER
- pokud bude odpověď ve stylu {"POWER":"OFF"} nebo {"POWER":"ON"} mělo by to fungovat


příklad minimální konfigurace:
# zap/vyp
*configuration.yaml*
```yaml
switch:
    - platform: httas
      switches:
        muj_switch:
          ip_address: ip_zarizeni
```
# sensor
Podpora poue DS18B20 v případě teploty
```yaml
sensor:
    - platform: httas     
      sensors:
        bazen:      
          ip_address: 192.168.X.XX
          friendly_name: Teplota vody
          sensor_type: temperature    
        cerpadlo:      
          ip_address: 192.168.X.XX
          friendly_name: Čerpadlo      
          sensor_type: current    # Proud - pozor, zde dotazování s vysokou frekvencí
```                                  
      
Instalace:
- tam kde máte soubor *configuration.yaml* vytvořit složku, pokud ji již nemáte *custom_components* a do ní přidat složku *httas*
- nakopírovat vše co je zde v adresáři 
- restart HA a úprava *configuration.yaml* v sekci *switch* viz výše, další se přidávají pod sebe
- znovu restart HA a měl by být k dispozici například *switch.muj_switch*.

Popis chování:
- pokud daný switch či sensor neodpoví do 0.3 vteřiny, je indikovaná chyba
- pokud neodpoví do 0.3 vteřiny je zaslána předchozí hodnota (max. 5x)
- je-li na daném zařízení chyba více jak 5x za sebou - oznámení uživateli a další dotazy budou po 59 vteřinách
- v případě stavu (je-li zap/vyp, teploty), je zařízení dotazováno jednou za 30 vteřin
- u proudu přibližně jednou za 10 vteřin
