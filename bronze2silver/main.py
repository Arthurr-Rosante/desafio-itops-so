import os
import io
import csv
import json
import boto3
import subprocess
from datetime import datetime

SYNCED_DIR = "./capturas"

BUCKET_NAME="itops-04261042"
PREFIX = "02-silver"

def main():
    os.makedirs(SYNCED_DIR, exist_ok=True)

    comando_sync = ["aws", "s3", "sync", f"s3://{BUCKET_NAME}/01-bronze/", SYNCED_DIR]
    resultado = subprocess.run(comando_sync, capture_output=True, text=True)
    
    if resultado.returncode == 0:
        print("[ INFO ] Sincronização com S3 concluída com sucesso!")
        if resultado.stdout.strip():
            print(resultado.stdout)
    else:
        print("[ ERRO ] Falha ao executar aws s3 sync:")
        print(resultado.stderr)

    s3_client = boto3.client("s3")
    lista_csv = []

    capturas = [f for f in os.listdir(SYNCED_DIR) if f.endswith(".json")]
    if len(capturas) == 0:
        print("[ INFO ] Nenhum arquivo sincronizado, encerrando ETL...")
        return
    else:
        print(f"[ INFO ] {len(capturas)} arquivo(s) sincronizado(s), iniciando ETL...")

    # Arranja os elementos em ordem cronológica
    capturas.sort()

    capturas_set = set()
    for c in capturas:
        fname = c[20:].replace(".json", "")
        capturas_set.add(fname)

    for c in capturas_set:
        lista_json = []
        files = [f for f in capturas if c in f]

        for file in files:
            with open(f"{SYNCED_DIR}/{file}", "r") as current:
                lista_json.append(json.load(current))

        for i in range(len(lista_json)):
            current = lista_json[i]
            prev = current if i == 0 else lista_json[i-1]

            tipo_dispositivo = "Antena" if c.startswith("AP-") else "Firewall"

            timestamp_dt = datetime.strptime(files[i][:19], "%Y-%m-%d_%H-%M-%S")
            timestamp_str = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S")

            prev_timestamp_dt = datetime.strptime(files[i-1][:19], "%Y-%m-%d_%H-%M-%S") if i > 0 else timestamp_dt
            
            time_delta = (timestamp_dt - prev_timestamp_dt).total_seconds()
            if time_delta <= 0: time_delta = 60     # por padrão, delta de 1min

            delta_bytes_sent = abs(current.get("bytes_sent", 0) - prev.get("bytes_sent", 0))
            delta_bytes_recv = abs(current.get("bytes_recv", 0) - prev.get("bytes_recv", 0))

            if i == 0:
                bytes_sent_mbps = 0.0
                bytes_recv_mbps = 0.0
            else:
                # delta_bytes_sent                                  --> Bytes
                # (delta_bytes_sent * 8)                            --> bits
                # (delta_bytes_sent * 8) / 1_000_000                --> Megabits
                # (delta_bytes_sent * 8) / 1_000_000) / time_delta  --> Mbps
                bytes_sent_mbps = round(((delta_bytes_sent * 8) / 1_000_000) / time_delta, 2)
                bytes_recv_mbps = round(((delta_bytes_recv * 8) / 1_000_000) / time_delta, 2)

            status = []
            if current.get("active_conn", 0) > 40: status.append("Alta Densidade")
            if current.get("cpu_usage", 0) > 80.0: status.append("Gargalo de Processamento")
            if current.get("ram_usage", 0) > 75.0: status.append("OOM")

            lista_csv.append({
                "id": c,
                "tipo_dispositivo": tipo_dispositivo,
                "timestamp": timestamp_str,
                "active_conn": current.get("active_conn", 0),
                "active_sessions": current.get("active_sessions", 0),
                "bytes_sent_mbps": bytes_sent_mbps,
                "bytes_recv_mbps": bytes_recv_mbps,
                "cpu_usage": current.get("cpu_usage", 0.0),
                "ram_usage": current.get("ram_usage", 0.0),
                "status_carga": ", ".join(status) if status else "Normal"
            })

    enviar_csv_consolidado(s3_client, lista_csv)

def enviar_csv_consolidado(s3_client, capturas):
    csv_buffer = io.StringIO()
    header = capturas[0].keys()

    writer = csv.DictWriter(csv_buffer, fieldnames=header, delimiter=";")
    writer.writeheader()
    writer.writerows(capturas)

    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    bpath = f"{PREFIX}/{now}_metricas_consolidadas.csv"
    
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=bpath,
        Body=csv_buffer.getvalue().encode("utf-8"),
        ContentType="text/csv"
    )

    print(f"[ INFO ] CSV consolidado enviado ao S3: s3://{BUCKET_NAME}/{bpath}")

if __name__ == "__main__":
    main()
