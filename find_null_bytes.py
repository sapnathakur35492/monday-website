import os

def check_for_null_bytes(directory):
    print(f"Scanning {directory} for null bytes...")
    for root, dirs, files in os.walk(directory):
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'rb') as f:
                        content = f.read()
                        if b'\x00' in content:
                            print(f"FOUND NULL BYTES: {path}")
                except Exception as e:
                    print(f"Could not read {path}: {e}")

check_for_null_bytes('.')
