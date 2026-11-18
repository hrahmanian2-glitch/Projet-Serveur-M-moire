#!/usr/bin/env python3
import sys, signal

def main():
    argv = sys.argv
    if len(sys.argv) not in (2, 3):
        print("Usage: python server_mem_backend.py memsize <--periodic-log>", file=sys.stderr)
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

def command_loop(BYA_Octets, memsize):
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        cmd = parts[0]

        if cmd == "GET" and len(parts) == 3:
            try:
                debut_page  = int(parts[1])
                pagesize = int(parts[2])
                if debut_page < 0 or debut_page + pagesize > memsize:
                    print(f'error: index "{debut_page}" out of bounds', flush=True)
                    continue
                page = BYA_Octets[debut_page:debut_page + pagesize]
                print(page.hex(), flush=True)
            except ValueError:
                print("error: invalid arguments", flush=True)

        elif cmd == "POST" and len(parts) == 4:
            try:
                debut_page = int(parts[1])
                pagesize = int(parts[2])
                hexdata = parts[3]
                data = bytearray.fromhex(hexdata)
                if debut_page < 0 or debut_page + pagesize > memsize:
                    print("error: debut_page out of bounds", flush=True)
                    continue
                BYA_Octets[debut_page:debut_page + pagesize] = data
                print("ok", flush=True)
            except ValueError:
                print("error: invalid arguments", flush=True)

        else:
            print("error: invalid command", flush=True)

    print("bye", flush=True)

if __name__ == "__main__":
    main()