# sfu-upass
Inspired by: https://github.com/Armour/upass-sfu
A script for an SFU student to automatically renew their monthly Translink U-Pass, updated to SFU's current MFA login requirements and written with the Selenium framework.

## Instructions
### 1. Update the config.json file with your SFU username and password
```json
{
  "username": "username",
  "password": "password"
}
```

### 2. Run the script
Windows:
```shell
python sfu-upass.py
```

Unix:
```shell
python3 sfu-upass.py
```
