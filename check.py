import requests, sys, getpass, re

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


def parse_line(line: str):
    """
    Parse a line into (package, [versions]).
    Handles scoped packages and multiple versions.
    """
    line = line.strip()
    if not line:
        return None, []

    # Look for last @ followed by digits (the version)
    m = re.search(r'(.+?)@([\d].*)$', line)
    if m:
        pkg, versions_str = m.group(1), m.group(2)
    else:
        # fallback: split by space
        parts = line.split()
        pkg, versions_str = parts[0], " ".join(parts[1:])

    # Normalize: drop scope if present (@scope/pkg → pkg)
    if pkg.startswith("@") and "/" in pkg:
        pkg = pkg.split("/", 1)[1]

    # Split versions by comma or space
    versions = re.split(r"[ ,]+", versions_str.strip())
    return pkg, [v for v in versions if v]


def exists(pkg, ver):
    r = requests.get(
        f"{url.rstrip('/')}/service/rest/v1/search",
        params={"repository": repo, "name": pkg, "version": ver},
        auth=auth,
        headers=headers,
    )
    return r.ok and r.json().get("items")


with open(file) as f:
    for line in f:
        pkg, versions = parse_line(line)
        if not pkg or not versions:
            continue
        for v in versions:
            found = exists(pkg, v)
            print(f"{pkg}@{v} -> {'✅ FOUND' if found else '❌ NOT FOUND'}")
