#!/usr/bin/env python3

import sys, signal

def main():
    argv = sys.argv
    if len(sys.argv) not in (2, 3):
        print("Usage: python server_mem_backend.py memsize <--periodic-log (o)>", file=sys.stderr)
        sys.exit(1)


    try:
        memsize = int(argv[1])
    except ValueError:
        print(f'error: memsize must be an integer ("{argv[1]}" given)', file=sys.stderr)
        sys.exit(1)
    if memsize <= 0:
        print(f'error: memsize must be strictly positive ({memsize} given)', file=sys.stderr)
        sys.exit(1)

    BYA_Octets = bytearray([32] * memsize)
    
    if "--periodic-log" in argv:
        
        def handler(_signum, _frame):
            print(list(BYA_Octets), file=sys.stderr)
            signal.alarm(1)
        
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(1)
        
        command_loop(BYA_Octets, memsize)
    
    else:
        
        command_loop(BYA_Octets, memsize)

def command_loop(BYA_Octets, memsize):
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        cmd = parts[0]
        if cmd == "GET" and len(parts) == 2:
            try:
                offset = int(parts[1])
                if offset < 0 or offset >= memsize:
                    print(f'ERROR: index "{offset}" out of bounds')
                    continue
                print(BYA_Octets[offset])
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
                BYA_Octets[offset] = value
                print("ok")
            except ValueError:
                print("ERROR: invalid offset or value")

        else:
            print("ERROR: invalid command")

    print("bye")

if __name__ == "__main__":
    main()