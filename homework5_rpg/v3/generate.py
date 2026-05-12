import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

write_file('models/__init__.py', '')
write_file('models/states/__init__.py', '')
write_file('models/strategies/__init__.py', '')
write_file('models/actions/__init__.py', '')
write_file('models/cor/__init__.py', '')
