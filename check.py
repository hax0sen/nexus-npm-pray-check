import requests, sys, getpass

if len(sys.argv) < 4:
    sys.exit("Usage: python check.py <packages.txt> <nexus_url> <repo> [username]")

file, url, repo = sys.argv[1:4]

# Ask user if they want to use token or basic auth
use_token = input("Use token authentication? (y/n): ").strip().lower() == "y"

if use_token:
    token = getpass.getpass("Token: ")
    headers = {"Authorization": f"Bearer {token}"}
    auth = None
else:
    if len(sys.argv) < 5:
        sys.exit("Usage for basic auth: python check.py <packages.txt> <nexus_url> <repo> <username>")
    user = sys.argv[4]
    pwd = getpass.getpass("Password: ")
    headers = {}
    auth = (user, pwd)

with open(file) as f:
    for line in f:
        if "@" not in line.lstrip("@"):
            continue
        pkg, ver = line.strip().rsplit("@", 1)
        r = requests.get(
            f"{url.rstrip('/')}/service/rest/v1/search",
            params={"repository": repo, "name": pkg, "version": ver},
            auth=auth,
            headers=headers
        )
        print(f"{pkg}@{ver} -> {'✅ FOUND' if (r.ok and r.json().get('items')) else '❌ NOT FOUND'}")
