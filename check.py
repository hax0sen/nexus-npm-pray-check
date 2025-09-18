import requests, sys, getpass, re

if len(sys.argv) < 4:
    sys.exit("Usage: python check.py <packages.txt> <nexus_url> <repo> [username]")

file, url, repo = sys.argv[1:4]

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
    Parse a line into (group, name, [versions]).
    Uses the first '@' as the separator via:
      re.match(r'(@?[^@\s]+(?:/[^@\s]+)?)(@.+)', line)
    Falls back to a whitespace separator when no '@' separates name and versions.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None, None, []

    # match your provided regex: first '@' separates package from versions
    m = re.match(r'(@?[^@\s]+(?:/[^@\s]+)?)(@.+)', line)
    if m:
        pkg = m.group(1)            # e.g. "@scope/name" or "name"
        versions_str = m.group(2)  # e.g. "@1.2.3, @1.2.4"
    else:
        # fallback: "pkg <whitespace> versions..."
        m2 = re.match(r'(\S+)\s+(.+)', line)
        if not m2:
            return None, None, []
        pkg = m2.group(1)
        versions_str = m2.group(2)

    # Determine scope (group) and name
    if pkg.startswith("@") and "/" in pkg:
        group, name = pkg[1:].split("/", 1)  # remove leading '@'
    else:
        group = None
        # remove any stray leading '@' from unscoped pkg (defensive)
        name = pkg.lstrip("@")

    # Split versions by commas or whitespace, remove leading '@' from each version
    parts = re.split(r'[,\s]+', versions_str.strip())
    versions = [p.lstrip("@").strip() for p in parts if p.strip()]

    return group, name, versions


def exists(group, name, ver):
    params = {"repository": repo, "name": name, "version": ver}
    if group:
        params["group"] = group  # pass scope as group when present

    r = requests.get(
        f"{url.rstrip('/')}/service/rest/v1/search",
        params=params,
        auth=auth,
        headers=headers,
    )
    return r.ok and bool(r.json().get("items"))


with open(file) as f:
    for line in f:
        group, name, versions = parse_line(line)
        if not name or not versions:
            continue
        for v in versions:
            found = exists(group, name, v)
            scope_prefix = f"@{group}/" if group else ""
            print(f"{scope_prefix}{name}@{v} -> {'✅ FOUND' if found else '❌ NOT FOUND'}")
