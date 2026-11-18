#!/usr/bin/env python3
import sys

def main():
    argv = sys.argv
    if len(argv) > 3 or len(argv) == 1:
        print(f'usage: {argv[0]} <memsize> [--debug]', file=sys.stderr)
        sys.exit(1)

    memsize = int(argv[1])
    segments_table = {}
    debug = "--debug" in argv[2]
    command_loop(memsize, segments_table, debug)


def command_loop(memsize, segments_table, debug):

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        cmd = parts[0]

        if cmd == "PUT":
            if len(parts) != 3:
                print(f"error: invalid PUT command", file=sys.stderr)
                continue
            name = parts[1]
            size = int(parts[2])

            if name in segments_table:
                print(f"error: segment {name} already exists", file=sys.stderr)
                continue
            if size > memsize or size <= 0:
                print(f"error: {size} out of bounds, memsize is {memsize}", file=sys.stderr)
                continue

            list_sum = [0]
            for seg in segments_table.values():
                list_sum.append(seg["base"] + seg["size"])

            for i in list_sum:
                if size + i > memsize:
                    continue
                for seg in segments_table.values():
                    if i < seg["base"] + seg["size"] and seg["base"] < i + size:
                        break
                else:
                    
                    segments_table[name] = {"base": i, "size": size}
                    if debug:
                        print(f"[debug] segments_table={segments_table}", file=sys.stderr)
                    print("ok", file=sys.stderr)
                    break
            else:
                if debug:
                    print(f"[debug] segments_table={segments_table}", file=sys.stderr)
                print(f"error: not enough memory to create segment {name} of size {size}", file=sys.stderr)

        

        elif cmd == "DELETE":
            if len(parts) != 2:
                print(f"error: invalid DELETE command", file=sys.stderr)
                continue
            name = parts[1]
            if name not in segments_table:
                if debug:
                    print(f"[debug] segments_table={segments_table}", file=sys.stderr)
                print(f"error: segment {name} does not exist", file=sys.stderr)
                continue
            del segments_table[name]
            if debug:
                print(f"[debug] segments_table={segments_table}", file=sys.stderr)
            print("ok", file=sys.stderr)

        

        elif cmd == "GET":
            if len(parts) != 3:
                print(f"error: invalid GET command", file=sys.stderr)
                continue
            name = parts[1]
            index = int(parts[2])
            if name not in segments_table:
                print(f"error: segment {name} does not exist", file=sys.stderr)
                continue
            elem = segments_table[name]
            if index < 0 or index >= elem["size"]:
                print(f"error: index {index} out of bounds, {name} size is {elem['size']}", file=sys.stderr)
                continue
            print(f"GET {elem['base'] + index}")

        elif cmd == "POST":
            if len(parts) != 4:
                print(f"error: invalid POST command", file=sys.stderr)
                continue
            name = parts[1]
            index = int(parts[2])
            value = int(parts[3])
            if name not in segments_table:
                print(f"error: segment {name} does not exist", file=sys.stderr)
                continue
            elem = segments_table[name]
            if index < 0 or index >= elem["size"]:
                print(f"error: index {index} out of bounds, {name} size is {elem['size']}", file=sys.stderr)
                continue
            print(f"POST {elem['base'] + index} {value}")

        else:
            print(f"error: unknown command {cmd}", file=sys.stderr)

            print(f"error: unknown command {cmd}", file=sys.stderr)


if __name__ == "__main__":
    main()