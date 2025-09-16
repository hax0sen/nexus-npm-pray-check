# Nexus NPM Version Checker

This Python script checks if specific npm package versions exist in a Nexus repository (proxy or hosted).  
It supports both **basic authentication** (`username:password`) and **Bearer token authentication**.  

---

## Features

- Check single or scoped npm packages (e.g., `eslint@9.35.0` or `@scope/pkg@1.2.3`)  
- Supports multiple packages listed in a text file  
- Supports Nexus authentication:
  - Basic auth (username + password)  
  - Token auth (Bearer token)  
- Prints results in a simple, readable format:  


package@version -> ✅ FOUND

package@version -> ❌ NOT FOUND


---

## Requirements

- Python 3.6+  
- `requests` library  

Install `requests` via pip if needed:

```bash
pip install requests
```
## Usage
Command-line arguments
```bash
python check.py <packages.txt> <nexus_url> <repo> [username]
```

## Authentication
```
Basic Authentication

python check.py packages.txt <nexus_url> npm admin
Password: *****

Token Authentication (Bearer)

python check.py packages.txt <nexus_url> npm
Bearer Token: ******
