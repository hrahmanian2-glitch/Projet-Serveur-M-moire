
#!/usr/bin/env python3

import sys
argv = sys.argv
if len(argv) != 2:
    print("Usage: python server_mem_backend.py memsize", file=sys.stderr)
    sys.exit(1)
else:
    if memsize := int(argv[1]) <= 0:
        print("Usage: python server_mem_backend.py memsize", file=sys.stderr)
        sys.exit(1)
    else:
        memsize = int(argv[1])
    BYA_Octects = bytearray([32] * memsize)


for line in sys.stdin :
    line = line.strip()
    if not line :
        continue
    parts = line.split()
    cmd = parts[0]
    if cmd == "GET" and len(parts) == 2:
        try:
            offset = int(parts[1])
            if offset < 0 or offset >= memsize:
                print(f'ERROR: index "{offset}" out of bounds')
                continue
            print(BYA_Octects[offset])
        except ValueError:
            print("ERROR: Invalid offset")

    elif cmd == "POST" and len(parts) == 3:
        try:
            offset = int(parts[1])
            value = int(parts[2])
            if offset < 0 or offset >= memsize:
                print("ERROR: Offset out of bounds")
                continue
            if value < 0 or value > 255:
                print(f'ERROR: POST instruction requires a byte as a second argument "{value}" out of byte range (0-255)')
                continue
            BYA_Octects[offset] = value 
            print("ok")
        except ValueError:
            print("ERROR: invalid offset or value") 

    else:
        print("ERROR: invalid command")

print("bye")
