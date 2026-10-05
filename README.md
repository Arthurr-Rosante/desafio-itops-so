# **Projeto ITOPS - Sistemas Operacionais em Nuvem**

## **1. Arquitetura do Projeto**

<img src="./assets/arquitetura-projeto.png" alt="Arquitetura do Projeto" />

## **2. Camadas**

### _- Camada 01:_

Antenas JSON - Formato

```json
{
    "id": "AP-XPTO",
    "timestamp": "YYYY-MM-DD HH:MM",
    "network": {
        "bytes": {
            "sent": 999,
            "received": 999
        },
        "connections": {
            "active": 99,
            "connectedIPs": [...]
        }
    },
    "components": [
        "cpu": {
            "usage": 0.99,
            "measuredIn": "pct"
        },
        "ram": {
            "usage": 0.99,
            "measuredIn": "pct"
        }
    ]
}
```

Firewall JSON - Formato

```json
{
    "id": "FW-XPTO",
    "timestamp": "YYYY-MM-DD HH:MM",
    "network": {
        "bytes": {
            "sent": 999,
            "received": 999
        },
        "packets": {
            "sent": 999,
            "received": 999,
            "dropped": 999,
        },
        "sessions": {
            "active": 99,
            "topBlockedIPs": [...],
            "connectedSessions": [
                {
                    "ipv4": "0.0.0.0",
                    "type": "tcp"   // ou "udp"
                },
                // demais sessões...
            ]
        }
    },
    "components": [
        "cpu": {
            "usage": 0.99,
            "measuredIn": "pct"
        },
        "ram": {
            "usage": 0.99,
            "measuredIn": "pct"
        }
    ]
}
Active_sessions,Dropped_packets,top_blocked_ip
```
