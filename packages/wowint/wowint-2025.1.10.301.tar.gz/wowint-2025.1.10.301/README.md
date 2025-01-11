# PyPI: WowInt

PyPi: https://pypi.org/project/iid42
PyPi: https://pypi.org/project/wowint


-----------------


## Commencez à apprendre : `pip install iid42 wowint`

Cet outil a été créé pour aider à apprendre la programmation par le jeu.

Vous trouverez dans *Scratch To Warcraft* du code permettant de simuler des touches de clavier :  
- [https://github.com/EloiStree/2024_08_29_ScratchToWarcraft](https://github.com/EloiStree/2024_08_29_ScratchToWarcraft)

Vous pouvez également utiliser *XOMI* pour simuler des manettes Xbox sur Windows :  
- [https://github.com/EloiStree/2022_01_24_XOMI](https://github.com/EloiStree/2022_01_24_XOMI)

Si vous préférez injecter des touches, vous trouverez du code compatible avec Raspberry Pi Pico et ESP32 ici :  
- [https://github.com/EloiStree/2024_11_16_WowIntegerWorkshopPicoW](https://github.com/EloiStree/2024_11_16_WowIntegerWorkshopPicoW)  
- [https://github.com/EloiStree/2024_11_21_ESP32HC05RC](https://github.com/EloiStree/2024_11_21_ESP32HC05RC)

Si vous souhaitez héberger un serveur Raspberry Pi avec des clés d'accès pour IID42 :  
- Installer Raspberry Pi : [https://github.com/EloiStree/2024_12_05_RaspberryPiGate](https://github.com/EloiStree/2024_12_05_RaspberryPiGate)  
- Serveur : [https://github.com/EloiStree/2025_01_01_HelloMegaMaskPushToIID](https://github.com/EloiStree/2025_01_01_HelloMegaMaskPushToIID)  
  - Client Unity3D : [https://github.com/EloiStree/2025_01_01_UnityToServerTunnelingMetaMaskWS](https://github.com/EloiStree/2025_01_01_UnityToServerTunnelingMetaMaskWS)  
  - Client Python : [https://github.com/EloiStree/2025_01_01_PythonToServerTunnelingMetaMaskWS](https://github.com/EloiStree/2025_01_01_PythonToServerTunnelingMetaMaskWS)

Vous trouverez un tutoriel pour IID42 en Python, C#, et Unity3D ici :  
[https://github.com/EloiStree/2025_02_03_MonsLevelUpInGroup/issues/21](https://github.com/EloiStree/2025_02_03_MonsLevelUpInGroup/issues/21)


## Start Learning: `pip install iid42 wowint`

This tool was created to help you learn programming through games.

In *Scratch To Warcraft*, you'll find code to simulate keyboard inputs:  
- [https://github.com/EloiStree/2024_08_29_ScratchToWarcraft](https://github.com/EloiStree/2024_08_29_ScratchToWarcraft)

You can also use *XOMI* to simulate Xbox controllers on Windows:  
- [https://github.com/EloiStree/2022_01_24_XOMI](https://github.com/EloiStree/2022_01_24_XOMI)

If you're more interested in injecting key inputs, you'll find code for the Raspberry Pi Pico and ESP32 here:  
- [https://github.com/EloiStree/2024_11_16_WowIntegerWorkshopPicoW](https://github.com/EloiStree/2024_11_16_WowIntegerWorkshopPicoW)  
- [https://github.com/EloiStree/2024_11_21_ESP32HC05RC](https://github.com/EloiStree/2024_11_21_ESP32HC05RC)

If you'd like to host a Raspberry Pi server with access keys for IID42:  
- Install Raspberry Pi: [https://github.com/EloiStree/2024_12_05_RaspberryPiGate](https://github.com/EloiStree/2024_12_05_RaspberryPiGate)  
- Server: [https://github.com/EloiStree/2025_01_01_HelloMegaMaskPushToIID](https://github.com/EloiStree/2025_01_01_HelloMegaMaskPushToIID)  
  - Unity3D Client: [https://github.com/EloiStree/2025_01_01_UnityToServerTunnelingMetaMaskWS](https://github.com/EloiStree/2025_01_01_UnityToServerTunnelingMetaMaskWS)  
  - Python Client: [https://github.com/EloiStree/2025_01_01_PythonToServerTunnelingMetaMaskWS](https://github.com/EloiStree/2025_01_01_PythonToServerTunnelingMetaMaskWS)

You can find a tutorial for IID42 in Python, C#, and Unity3D here:  
[https://github.com/EloiStree/2025_02_03_MonsLevelUpInGroup/issues/21](https://github.com/EloiStree/2025_02_03_MonsLevelUpInGroup/issues/21)  


--- 



**It is as easy as this:**
- Download python: https://www.python.org/downloads/
- Open Window terminal and type `pip install iid42 wowint`
- Create the following file: 

``` py
# pip install iid42
import wowint
from wowint import WowIntegerTarget
# Send IID to a UDP Gate Relay
# Replace 127.0.0.1 with the computer you want to target or the game server
# Example: 192.168.1.42  http://apint.ddns.net 
target = WowIntegerTarget("127.0.0.1",3615,0,True)
# Send the action 42 to the target with UDP to 127.0.0.1 computer on the applicaton behind 3615 port.
target.press_key_int(WowIntegerKeyboard.arrow_left,0)
# Send the action 42 to the player 2 to the target with UDP to 127.0.0.1 computer on the applicaton behind 3615 port.
target.release_key_int(WowIntegerKeyboard.arrow_left,50)

```


```
/*
 * ----------------------------------------------------------------------------
 * "PIZZA LICENSE":
 * https://github.com/EloiStree wrote this file.
 * As long as you retain this notice, you
 * can do whatever you want with this code.
 * If you think my code saved you time,
 * consider sending me a 🍺 or a 🍕 at:
 *  - https://buymeacoffee.com/apintio
 * 
 * You can also support my work by building your own DIY input device
 * using these Amazon links:
 * - https://github.com/EloiStree/HelloInput
 *
 * May the code be with you.
 *
 * Updated version: https://github.com/EloiStree/License
 * ----------------------------------------------------------------------------
 */
```


