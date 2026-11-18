import sys, random
from remotememory import RemoteMemory
from controledmemory import ControledMemory

write_rate = 0.1
sigma = 3
num_accesses = 1000
debug = False
alloc = True
pagesize = 8
cachesize = 64

try:
    if "--write_rate" in sys.argv:
        write_rate = float(sys.argv[sys.argv.index("--write_rate") + 1])
    if "--sigma" in sys.argv:
        sigma = float(sys.argv[sys.argv.index("--sigma") + 1])
    if "--num_accesses" in sys.argv:
        num_accesses = int(sys.argv[sys.argv.index("--num_accesses") + 1])
    if "--debug" in sys.argv:
        debug = True
    if "--no-alloc" in sys.argv:
        alloc = False
    if "--pagesize" in sys.argv:
        pagesize = int(sys.argv[sys.argv.index("--pagesize") + 1])
    if "--cachesize" in sys.argv:
        cachesize = int(sys.argv[sys.argv.index("--cachesize") + 1])
    host = sys.argv[1]
    port = int(sys.argv[2])
    segname = sys.argv[3]
    segsize = int(sys.argv[4])
except:
    print("Usage: python client.py <host> <port> <segname> <segsize> OPTIONS", file=sys.stderr)
    sys.exit(1)

index = 0

with ControledMemory(RemoteMemory(host, port, segname, segsize, debug, alloc, pagesize, cachesize)) as mem:
    for i in range(num_accesses):
        index = int(random.gauss(index, sigma)) % segsize
        if random.random() < write_rate:
            mem[index] = random.randint(0, 255)
        else:
            _ = mem[index]