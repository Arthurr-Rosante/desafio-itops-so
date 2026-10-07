import io
import boto3
import numpy as np
import pandas as pd
from datetime import datetime

BUCKET_NAME = "itops-04261042"
PREFIX = "03-gold"

def main():
    s3_client = boto3.client("s3")

    # Pegando todas as leituras em 02-silver da data atual
    today = datetime.now().strftime("%Y-%m-%d")
    prefix_busca = f"02-silver/{today}_"
    suffix = "_metricas_consolidadas.csv"

    paginator = s3_client.get_paginator("list_objects_v2")
    dataframes = []

    for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix_busca):
        for obj in page.get("Contents", []):
            key = obj["Key"]

            if key.endswith(suffix):
                response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
                df_temp = pd.read_csv(io.BytesIO(response["Body"].read()), sep=";")
                dataframes.append(df_temp)

    # Juntando todas as leituras em um único Dataframe
    if dataframes:
        # Concatenando todos os Dataframes em um único DF consolidado
        df_final = pd.concat(dataframes, ignore_index=True)
        print(f"[ INFO ] Total de registros carregados: {len(df_final)}")

        # DF exclusivo para registros de Antenas
        df_antenas = df_final[df_final["tipo_dispositivo"] == "Antena"].copy()

        # Descobrindo o tráfego de rede de cada antena
        df_antenas['trafego_total_mbps'] = df_antenas['bytes_sent_mbps'] + df_antenas['bytes_recv_mbps']
    
        # Previne divisão por zero caso a antena tenha ficado ociosa (0 tráfego)
        df_antenas['trafego_total_mbps'] = df_antenas['trafego_total_mbps'].replace(0, np.nan)
        
        # Quanto maior a razão, pior a eficiência da Antena
        df_antenas['razao_trafego_consumo'] = df_antenas['cpu_usage'] / df_antenas['trafego_total_mbps']

        relatorio = df_antenas.groupby('id').agg(
            amostras_analisadas=('timestamp', 'count'),
            media_trafego_mbps=('trafego_total_mbps', 'mean'),
            media_cpu_usage=('cpu_usage', 'mean'),
            razao_trafego_consumo_medio=('razao_trafego_consumo', 'mean')
        ).reset_index()

        relatorio = relatorio.sort_values(by='razao_trafego_consumo_medio', ascending=False)

        # Identifica o pior quartil (os 25% com a maior razão)
        piorQuartil = relatorio['razao_trafego_consumo_medio'].quantile(0.75)

        relatorio['recomendacao'] = np.where(
            relatorio['razao_trafego_consumo_medio'] >= piorQuartil,
            'Revisão de Hardware',
            'Adequado'
        )
        relatorio = relatorio.round(2)

        csv_buffer = io.StringIO()
        relatorio.to_csv(csv_buffer, index=False, sep=";")
        
        bpath = f"{PREFIX}/{today}_relatorio_eficiencia.csv"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=bpath,
            Body=csv_buffer.getvalue().encode('utf-8'),
            ContentType="text/csv"
        )

        print(f"[ INFO ] Relatório enviado ao S3: s3://{BUCKET_NAME}/{bpath}")
        print("[ INFO ] Relatório Gold gerado. Top equipamentos ineficientes:")
        print(relatorio[['id', 'razao_trafego_consumo_medio', 'recomendacao']].head())
    else:
        print(f"[ INFO ] Nenhum arquivo encontrado em {BUCKET_NAME} para a data {today}.")

if __name__ == "__main__":
    main()