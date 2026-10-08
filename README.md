# **Projeto ITOPS - Sistemas Operacionais em Nuvem**

## **1. Arquitetura do Projeto**

<img src="./assets/arquitetura-projeto.png" alt="Arquitetura do Projeto" />

## **2. Camadas (Medallion Architecture)**

### _- Camada 01: **01-bronze/**_

Antenas JSON - Formato
```json
    {
        "id_antena": "AP-000000000000",
        "active_conn": 60,
        "bytes_sent": 123123123123,
        "bytes_recv": 123123123123,
        "cpu_usage": 99.9,
        "ram_usage": 99.9
    }
```

Firewall JSON - Formato
```json
    {
        "id_dispositivo": "FW-000000000000",
        "active_sessions": 10000,
        "dropped_packets": 9999,
        "top_blocked_ip": "255.255.255.255",
        "bytes_sent": 123123123123,
        "bytes_recv": 123123123123,
        "cpu_usage": 99.9,
        "ram_usage": 99.9
    }
```

### _- Camada 02: **02-silver/**_
```csv
    id;tipo_dispositivo;timestamp;active_conn;active_sessions;bytes_sent_mbps;bytes_recv_mbps;cpu_usage;ram_usage;status_carga
AP-000000000000;Antena;YYYY-MM-DD HH:MM:SS;60;0;123123123123;123123123123;99.9;99.9;Alta Densidade, Gargalo de Processamento, OOM
```

### _- Camada 03: **03-gold/**_
```csv
id;amostras_analisadas;media_trafego_mbps;media_cpu_usage;razao_trafego_consumo_medio;recomendacao
AP-000000000000;10;0.57;37.34;115.95;Revisão de Hardware
```