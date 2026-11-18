import socket
MAXBYTES = 4096

class RemoteMemory:
    def __init__(self, host, port, segname, size, debug=False, alloc=True, pagesize=8, cachesize=64):
        self.host = host
        self.port = port
        self.segname = segname
        self.size = size
        self.with_debug = debug
        self.alloc = alloc
        self.pagesize = pagesize
        self.cachesize = cachesize

        if size % pagesize != 0:
            raise ValueError(f"segsize {size} must be divisible by pagesize {pagesize}")
        if cachesize % pagesize != 0:
            raise ValueError(f"cachesize {cachesize} must be a multiple of pagesize {pagesize}")

        self.num_pages_cache = cachesize // pagesize
        self.cache = {}
        self.cache_order = []

        if alloc:
            self.request(f"PUT {self.segname} {self.size} {self.pagesize}")

    def __enter__(self):
        return self

    def request(self, req):
        self.debug(f"Creating socket")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.debug(f"Connecting to remote memory at {self.host}:{self.port}")
        s.connect((self.host, self.port))
        self.debug(f"Connected")
        self.debug(f"Sending request: '{req}'")
        s.sendall(req.encode())
        responses = s.recv(MAXBYTES).decode().strip().splitlines()
        for response in responses:
            response = response.strip()
            if response.startswith("[debug]"):
                if self.with_debug:
                    self.debug(f"[from server] {response[8:]}")
                else:
                    continue
            else:
                self.debug(f"Received response: '{response}'")
                s.close()
                if response.startswith("error"):
                    raise ValueError(f"error from remote memory: {response}")
                return response

    def debug(self, message):
        if self.with_debug:
            print(f"[debug] {message}")

    def _flush_page(self, pagenum):
        if self.cache[pagenum]["dirty"]:
            data_hex = self.cache[pagenum]["data"].hex()
            self.request(f"POST {self.segname} {pagenum} {data_hex}")
            self.cache[pagenum]["dirty"] = False

    def _load_page(self, pagenum):
        if pagenum in self.cache:
            return
        if len(self.cache) >= self.num_pages_cache:
            victim = self.cache_order.pop(0)
            self._flush_page(victim)
            del self.cache[victim]
        response = self.request(f"GET {self.segname} {pagenum}")
        data = bytearray.fromhex(response)
        self.cache[pagenum] = {"data": data, "dirty": False}
        self.cache_order.append(pagenum)

    def _flush(self):
        for pagenum in list(self.cache.keys()):
            self._flush_page(pagenum)

    def __getitem__(self, index):
        pagenum = index // self.pagesize
        offset = index % self.pagesize
        self._load_page(pagenum)
        return self.cache[pagenum]["data"][offset]

    def __setitem__(self, index, value):
        pagenum = index // self.pagesize
        offset = index % self.pagesize
        self._load_page(pagenum)
        self.cache[pagenum]["data"][offset] = value
        self.cache[pagenum]["dirty"] = True

    def __len__(self):
        return self.size

    def __exit__(self, exc_type, exc_value, traceback):
        if self.alloc:
            self._flush()
            self.request(f"DELETE {self.segname}")

    def free(self):
        if self.alloc:
            self._flush()
            self.request(f"DELETE {self.segname}")