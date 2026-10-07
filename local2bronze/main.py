import os
import json
import boto3
import psutil
import random
import logging
import ipaddress
from datetime import datetime
from botocore.exceptions import ClientError

OUTPUT_DIR = "./out"
CHARACTERS = "ABCDEFGHIJKLMNPQRSTUVWXYZ123456789"

PREFIX = "01-bronze"
BUCKET_NAME="itops-04261042"

MIN_POSSIBLE_CONN = 5
MAX_POSSIBLE_CONN = 60

MIN_POSSIBLE_SESSIONS = 1
MAX_POSSIBLE_SESSIONS = 10000

def main():
    session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
            region_name=os.getenv("AWS_REGION")
        )
    s3_client = session.client("s3")
    
    # os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 3 Antenas e 1 Firewall
    antenas_ids = ["AP-BGGDCIHGJ", "AP-DDDBFIAJA", "AP-GDCBIFCGE"]
    firewall_id = "FW-CFIBEFJBJ"

    antenas = []
    for id in antenas_ids:
        captura = gerar_captura_antena(id)
        antenas.append(captura)
        enviar_json_s3(s3_client, id, captura)

    enviar_json_s3(s3_client, firewall_id, gerar_captura_firewall(firewall_id, antenas))

    # Envio das capturas ao Bucket
    # files = os.listdir(OUTPUT_DIR)
    # try:
    #     for f in files:
    #         fpath = f"{OUTPUT_DIR}/{f}"
    #         bpath = f"{PREFIX}/{f}"

    #         s3_client.upload_file(fpath, BUCKET_NAME, bpath)
    #         print(f"[ INFO ] Arquivo: {f} enviado para: s3://{BUCKET_NAME}/{PREFIX}")
    # except ClientError as e:
    #     logging.error(e)

def gerar_captura_antena(id):
    netio = psutil.net_io_counters()
    active_conn = random.randint(MIN_POSSIBLE_CONN, MAX_POSSIBLE_CONN)
    
    base_cpu = psutil.cpu_percent(interval=0.1)
    load_factor_ap = active_conn / MAX_POSSIBLE_CONN
    
    cpu_usage = round(min(100.0, base_cpu + (load_factor_ap * 40.0) + random.uniform(0.0, 5.0)), 2)

    mem = psutil.virtual_memory()
    ram_impact = (active_conn / MAX_POSSIBLE_CONN) * 6.0
    ram_usage = round(min(100.0, mem.percent + ram_impact), 2)

    return {
        "id_antena": id,
        "active_conn": active_conn,
        "bytes_sent": netio.bytes_sent,
        "bytes_recv": netio.bytes_recv,
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage
    }


def gerar_captura_firewall(id, antenas):
    top_blocked_ip = gerar_ip_randomico()
    netio = psutil.net_io_counters()

    active_sessions = random.randint(MIN_POSSIBLE_SESSIONS, MAX_POSSIBLE_SESSIONS)
    load_factor_fw = active_sessions / MAX_POSSIBLE_SESSIONS
    
    base_cpu = psutil.cpu_percent(interval=0.1)
    cpu_usage = round(min(100.0, base_cpu + (load_factor_fw * 60.0) + random.uniform(0.0, 10.0)), 2)

    mem = psutil.virtual_memory()
    ram_impact = load_factor_fw * 35.0
    ram_usage = round(min(100.0, mem.percent + ram_impact), 2)

    if cpu_usage > 85.0:
        dropped_packets = random.randint(200, 1500)
    elif cpu_usage > 70.0:
        dropped_packets = random.randint(10, 100)
    else:
        dropped_packets = random.randint(0, 5)

    # Qtd. de Bytes enviados pelo Firewall é a mesma enviada pelas antenas
    bytes_sent = 0
    for antena in antenas:
        bytes_sent += antena["bytes_sent"]

    return {
        "id_dispositivo": id,
        "active_sessions": active_sessions,
        "dropped_packets": dropped_packets,
        "top_blocked_ip": top_blocked_ip,
        "bytes_sent": bytes_sent,
        "bytes_recv": netio.bytes_recv,
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage
    }

def gerar_id_randomico(prefix, length = 12):
    size = length - len(prefix)
    id = prefix

    for _ in range(size):
        id += CHARACTERS[random.randint(0, size)] 
    return id

def gerar_ip_randomico():
    while True:
        ip = ipaddress.IPv4Address(random.randint(0, 2 ** 32))
        if ip.is_global:
            return str(ip)

def gerar_json(fname, body):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    fpath = f"{OUTPUT_DIR}/{now}_{fname}.json"

    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(body, f, indent=2)

def enviar_json_s3(s3_client, fname, body):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    bpath = f"{PREFIX}/{now}_{fname}.json"
    
    json_bytes = json.dumps(body, indent=2).encode('utf-8')
    
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=bpath,
        Body=json_bytes,
        ContentType="application/json"
    )
    print(f"[ INFO ] Enviado direto ao S3: s3://{BUCKET_NAME}/{bpath}")

if __name__ == "__main__":
    main()
