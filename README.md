# sfu-upass
Inspired by: https://github.com/Armour/upass-sfu

A utility script for an SFU student to automatically renew their monthly TransLink U-Pass, updated to accommodate SFU's MFA requirements. Written with the Selenium framework, which makes this slower than the original script that uses the requests API.

Currently limited to chromedriver. I plan to implement other toggleable browsers in the future.

## Instructions
### 1. Update the config.json file with your SFU username and password.
```json
{
  "username": "username",
  "password": "password",
  "secret_key": "MFA key"
}
```

### 2. Running the script
```shell
python sfu-upass.py [OPTIONS] (Windows)
python-3 sfu-pass.py [OPTIONS] (Unix)

  --browser (chrome, firefox, safari)
     Toggle a specific browser driver for Selenium to use. Defaults to Chrome.
```
