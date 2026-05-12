lines = open('pyproject.toml').readlines()
new_lines = []
for i, l in enumerate(lines):
    stripped = l.rstrip()
    if i == 15 and stripped.endswith('",'):
        new_lines.append(stripped + '\n')
        new_lines.append(']\n')
    elif i == 16 and stripped == '':
        pass
    else:
        new_lines.append(l)
open('pyproject.toml', 'w').writelines(new_lines)
print("Fixed closing bracket")
