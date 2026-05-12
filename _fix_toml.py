with open('pyproject.toml', 'r') as f:
    content = f.read()
content = content.replace('\\"', '"')
with open('pyproject.toml', 'w') as f:
    f.write(content)
print("Fixed")
