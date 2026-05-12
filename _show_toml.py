lines = open('pyproject.toml').readlines()
for i, l in enumerate(lines[15:30]):
    print(f"{i+16}: {l}", end='')
