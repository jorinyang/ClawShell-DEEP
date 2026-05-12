import tomllib
with open('pyproject.toml', 'rb') as f:
    data = f.read()
print("RAW first 200 bytes:", data[:200])
try:
    tomllib.loads(data.decode())
    print("TOML OK")
except Exception as e:
    print(f"TOML ERROR: {e}")
