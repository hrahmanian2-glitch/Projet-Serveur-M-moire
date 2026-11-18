#!/usr/bin/env python3
import sys, os

argv = sys.argv

if len(argv) < 3:
    print(f"Usage: {argv[0]} <memsize> <port> [--debug] [--periodic-log fichier]", file=sys.stderr)
    sys.exit(1)

memsize = argv[1]
port = argv[2]
debug = "--debug" in argv
log_file = None
if "--periodic-log" in argv:
    i = argv.index("--periodic-log")
    log_file = argv[i + 1]

r_1, w_1 = os.pipe()   
r_2, w_2 = os.pipe()   

pidbd = os.fork()
if pidbd == 0:
    os.close(w_1)
    os.close(r_1)
    os.close(w_2)

    os.dup2(r_2, 0)    
    os.close(r_2)

    if log_file:
        fd = os.open(log_file, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
        os.dup2(fd, 2)   # stderr du backend = fichier de log
        os.close(fd)

    if log_file:
        os.execlp("python3", "python3", "-u", "server_mem_backend.py", memsize, "--periodic-log")
    else:
        os.execlp("python3", "python3", "-u", "server_mem_backend.py", memsize)


pidfd = os.fork()
if pidfd == 0:
    os.close(w_1)
    os.close(r_2)

    os.dup2(r_1, 0)   
    os.dup2(w_2, 1)    
    os.close(r_1)
    os.close(w_2)

    if debug:
        os.execlp("python3", "python3", "-u", "server_mem_frontend.py", memsize, "--debug")
    else:
        os.execlp("python3", "python3", "-u", "server_mem_frontend.py", memsize)


os.close(r_1)
os.close(w_2)
os.close(r_2)

for line in sys.stdin:
    os.write(w_1, line.encode())

os.close(w_1)
os.waitpid(pidfd, 0)
os.waitpid(pidbd, 0)