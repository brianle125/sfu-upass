# sfu-upass
Inspired by: https://github.com/Armour/upass-sfu

A utility script for an SFU student to automatically renew their monthly TransLink U-Pass, updated to accommodate SFU's MFA requirements. Written with the Selenium framework, which makes this slower than the original script that uses the requests API.

## Instructions
Note: This will require the user to have their MFA code ready for manual input. 
### 1. Update the config.json file with your SFU username and password.
```json
{
  "username": "username",
  "password": "password"
}
```

### 2. Run the script.
Windows:
```shell
python sfu-upass.py
```

Unix:
```shell
python3 sfu-upass.py
```

### 3. Input the MFA code in the terminal when prompted.
```
>>> Enter your MFA code: <input code here>
```
