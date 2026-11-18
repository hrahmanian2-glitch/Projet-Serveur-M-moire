#!/usr/bin/env python3
import sys, os, socket

argv = sys.argv
if len(argv) < 3:
    print(f"Usage: {argv[0]} <memsize> <port>", file=sys.stderr)
    sys.exit(1)

memsize = argv[1]
port = int(argv[2])

r_1, w_1 = os.pipe()
r_2, w_2 = os.pipe()
r_3, w_3 = os.pipe()

pidbd = os.fork()
if pidbd == 0:
    os.close(w_1)
    os.close(r_1)
    os.close(w_2)
    os.close(r_3)
    os.dup2(r_2, 0)
    os.close(r_2)
    os.dup2(w_3, 1)
    os.close(w_3)
    os.execlp("python3", "python3", "-u", "server_mem_backend.py", memsize)

pidfd = os.fork()
if pidfd == 0:
    os.close(w_1)
    os.close(r_2)
    os.close(r_3)
    os.dup2(r_1, 0)
    os.close(r_1)
    os.dup2(w_2, 1)
    os.close(w_2)
    os.dup2(w_3, 2)
    os.close(w_3)
    os.execlp("python3", "python3", "-u", "server_mem_frontend.py", memsize)

os.close(r_1)
os.close(w_2)
os.close(r_2)
os.close(w_3)

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    srv.bind(("", port))
except OSError:
    print(f"erreur: port {port} déjà utilisé", file=sys.stderr)
    sys.exit(1)

srv.listen(1)

while True:
    client, addr = srv.accept()
    data = client.recv(1024).decode("utf-8", errors="ignore").strip()
    if not data:
        client.close()
        continue
    os.write(w_1, (data + "\n").encode())
    reponse = b""
    while not reponse.endswith(b"\n"):
        reponse += os.read(r_3, 1024)
    client.sendall(reponse)
    client.close()