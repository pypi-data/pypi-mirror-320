# PyPI: IID42

PyPi: https://pypi.org/project/iid42


-----------------


## Commencez à apprendre : `pip install iid42`

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


## Start Learning: `pip install iid42`

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
- Open Window terminal and type `pip install iid42`
- Create the following file: 

``` py
# pip install iid42
import iid42
from iid42 import SendUdpIID
# Send IID to a UDP Gate Relay
# Replace 127.0.0.1 with the computer you want to target or the game server
# Example: 192.168.1.42  http://apint.ddns.net 
target = SendUdpIID("127.0.0.1",3615,True)
# Send the action 42 to the target with UDP to 127.0.0.1 computer on the applicaton behind 3615 port.
target.push_integer(42)
# Send the action 42 to the player 2 to the target with UDP to 127.0.0.1 computer on the applicaton behind 3615 port.
target.push_index_integer(2,42)

# Send the action 42 to all the player to the target with UDP to 127.0.0.1 computer on the applicaton behind 3615 port.
target.push_index_integer(0,42)
```



**IID**, short for **Index Integer Date**, is a 4/8/12/16-byte format designed for seamless communication across various network systems, including UDP, WebSocket, and Mirror.

By standardizing the code and API to work exclusively with integer values:
- It enables the creation of action index tables.
- It supports the development of specialized tools for specific tasks, allowing IID to facilitate remote actions effectively.

The **IID format** was developed to streamline QA testing across multiple devices and computers with precise timing coordination.

### Key Features of IID:
1. **Index on your own server**: Identifies the target device.
2. **Index on a shared server**: Identifies the user.
3. **Value**: Represents the transported integer value.
4. **Date**: Encoded in a specific `ulong` format:
   - **01.....TICK**: Sent using NTP time.
   - **02.....TICK**: Intended for execution at a designated NTP time.
   - **.......TICK**: Sent from an unknown source time but uses `DateTime.Now` in UTC since 1970.

If you need assistance or are interested in contributing to this project, feel free to reach out.  
Since 2024, all my tools have been built around this principle.

---

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



**Sample of code to show how to use a console version to play on the server from "chat":**  

``` py
import os
import sys

if False:
    cmd = "pip install iid42 --force-reinstall"
    os.system(cmd)

import iid42
from iid42 import HelloWorldIID

HelloWorldIID.console_loop_to_push_iid_apintio()

```


**Play on the Twitch Play server with a loop:**
``` py
import os
import sys

if False:
    cmd = "pip install iid42 --force-reinstall"
    os.system(cmd)

import iid42
from iid42 import SendUdpIID
import time

target = SendUdpIID("apint.ddns.net", 3615, use_ntp= True)
while True:
        # Request to press a key in 50 ms from now on ntp time
        target.push_bytes(iid42.iid_ms(0,1001,50))
        # Request to release it a key in 550 ms from now on ntp time
        target.push_bytes(iid42.iid_ms(0,2001,550))
        # Every 2 seconds
        time.sleep(2)
        t = time.time()+1000
        t_offset = t + target.ntp_offset_local_to_server_in_milliseconds
        print(f"TIME:{t} NTP:{t_offset}")

```



Example using a local time queue as a thread clock.
``` py 
import os
import sys

if False:
    cmd = "pip install iid42 --force-reinstall"
    os.system(cmd)

import iid42
from iid42 import SendUdpIID

target = SendUdpIID("apint.ddns.net",3615,True,True)
print("IVP4", target.ivp4)
target.push_index_integer_in_queue(1,1082,0)
target.push_index_integer_in_queue(1,2082,1000)
target.push_index_integer_in_queue(1,1037,2000)
target.push_index_integer_in_queue(1,2037,4000)
target.push_index_integer_in_queue(1,1038,5000)
target.push_index_integer_in_queue(1,2038,6000)
target.push_index_integer_in_queue(1,1039,7000)
target.push_index_integer_in_queue(1,2039,8000)

target.push_integer_in_queue(2082,11000)
target.push_integer_in_queue(1037,12000)
target.push_integer_in_queue(2037,14000)
target.push_integer_in_queue(1038,15000)
target.push_integer_in_queue(2038,16000)
target.push_integer_in_queue(1039,17000)
target.push_integer_in_queue(2039,18000)


```