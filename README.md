# CanSat
TODO:
- Auswurfhöhe ermitteln
- Sinkgeschwindigkeit ermitteln
- zusätzlicher Sensor für Sekundärmission
- Lora-Funk testen und einbauen
- Fallschirm-Test mit 5.1 kg
- MPU6050 bei über 16 testen

## Entwicklungsumgebung

### Quickstart

- github account anlegen (falls nicht vorhanden)
- git installieren (siehe unten)
- python installieren
- vscode + python plugin installieren (siehe unten)

### Links

- Git
    - https://git-scm.com/download/win (command line, unbedingt notwendig)
    - https://tortoisegit.org/download/ (gui plugin für windows explorer, angenehm)

- Python
    - https://www.python.org/ftp/python/3.12.1/python-3.12.1-embed-amd64.zip
    irgendwo entpacken und in VSCode (siehe unten) beim ersten Mal starten eines Python-Programs den Pfad zu python.exe angeben

- [VSCode](https://code.visualstudio.com/)
    - [Python PlugIn](https://marketplace.visualstudio.com/items?itemName=ms-python.python), einfach direkt in VSCode suchen/installieren

- Code, Tutorials, Datasheets, ...
    - https://randomnerdtutorials.com/raspberry-pi-bme280-data-logger/
    - https://www.laub-home.de/wiki/Raspberry_Pi_BME280_Luftdruck_Sensor
    - https://learn.adafruit.com/adafruit-bmp280-barometric-pressure-plus-temperature-sensor-breakout/circuitpython-test    
    - https://www.laub-home.de/wiki/Raspberry_Pi_GPIO_Pin_Belegung_ausgeben
    - https://www.electronicwings.com/raspberry-pi/mpu6050-accelerometergyroscope-interfacing-with-raspberry-pi
    - https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf
    - https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf
    - https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf
    - https://lora-developers.semtech.com/documentation/tech-papers-and-guides/lora-and-lorawan/
    - https://pypi.org/project/smbus2/
    - https://docs.python.org/3/library/time.htm
    - https://docs.python.org/3/library/struct.html


### TortoiseGit mit SSH Key konfigurieren

1. Git Bash terminal öffnen
    - `ssh-keygen -t ed25519 -C "your_email@example.com"`
2. `C:\Users\YOUR_USERNAME\.ssh\id_ed25519.pub` auf github unter settings/SSH... dazufügen (New SSH Key)
3. Puttygen starten
    - File/Load Private Key   (`.ssh\id_ed25519`, das File OHNE .pub)
    - Save Private Key Button -> speichern als `.ssh\id_ed25519.ppk`
4. in tortoisegit/settings/git/remote/origin/putty-key die Datei `.ssh\id_ed25519.ppk` angeben

### Raspberry Pi Zero 2 W

- `sudo apt update`
- `sudo apt upgrade`

- `sudo apt install git`
    - `git config --global user.email "your@email.org"`
    - `git config --global user.name "Your Name"`

- `sudo raspi-config`
    - enable ssh
    - enable i2c

- `ssh-keygen -t ecdsa -b 521`
    - `more .ssh/id_ecdsa.pub` und den public ssh key bei github registrieren

- `sudo apt install python3-pip`
- `sudo apt-get install python3-numpy`
- `sudo pip3 install adafruit-circuitpython-bme280 --break-system-packages`
- `sudo pip install mpu6050-raspberrypi --break-system-packages`
