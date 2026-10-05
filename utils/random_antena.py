import json, random, psutil
from datetime import datetime

from utils.random_id import gen_random_id
from utils.random_ip import gen_random_ip

MIN_ACTIVE_CONNECTIONS = 5
MAX_ACTIVE_CONNECTIONS = 50

def gen_random_antena_capture():
    # 1. Gerando os campos do registro
    id = gen_random_id("AP-")
    
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")

    # 1.1. Rede
    network_io = psutil.net_io_counters()
    connectedIPs = list()
    activeConnections = random.randint(MIN_ACTIVE_CONNECTIONS, MAX_ACTIVE_CONNECTIONS)
    for _ in range(activeConnections):
        connectedIPs.append(gen_random_ip())

    # 1.2. Componentes
    mem = psutil.virtual_memory()

    cpu_usage_pct = psutil.cpu_percent(0.1)
    ram_usage_pct = round(mem.used / mem.total, 2) * 10
    # 1.3. Construção do JSON
    body = {
        "id": id,
        "timestamp": timestamp,
        "network": {
            "bytes": { 
                "sent": network_io.bytes_sent, 
                "received": network_io.bytes_recv 
            },
            "connections": {
                "active": activeConnections,
                "connectedIPs": connectedIPs
            }
        },
        "components": {
            "cpu": { "usage": cpu_usage_pct, "measuredIn": "pct" },
            "ram": { "usage": ram_usage_pct, "measuredIn": "pct" }
        }
    }

    return body