# Vk Bot
## Description

Vk bot for buying a flight ticket, the list of which is automatically generated. The cities for the flight are configured separately
---
## Installation
```
pip install -r requirments.txt
```
---
## Bot сommands
* /help 
* помощь
* /ticket
* регистрация
After the command "/ticket" or "регистрация" the scenario is running.
The scenario can be viewed in the file intent_settings.py in the "SCENARIOS" dictionary by the "step" key
---
## Technologies in the project
* Pillow 8.2.0
* pony 0.7.14
* vk-api 11.9.1
