import io
import boto3
import pandas as pd
from datetime import datetime

BUCKET_NAME = "itops-04261042"


# Relatório de Eficiência de Hardware: Um ranking das antenas que possuem a maior relação Tráfego
# de Rede / Consumo de CPU. Identificar equipamentos antigos ou com firmware problemático que
# consomem muita CPU para processar pouco tráfego

def main():
    s3_client = boto3.client("s3")

    # Pegando todas as leituras em 02-silver da data atual
    today = datetime.now().strftime("%Y-%m-%d")
    prefix = f"02-silver/{today}_"
    suffix = "_metricas_consolidadas.csv"

    paginator = s3_client.get_paginator("list_objects_v2")
    dataframes = []

    for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]

            if key.endswith(suffix):
                response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
                df_temp = pd.read_csv(io.BytesIO(response["Body"].read()), sep=";")
                dataframes.append(df_temp)

    # Juntando todas as leituras em um único Dataframe
    if dataframes:
        df_final = pd.concat(dataframes, ignore_index=True)
        print(f"[ INFO ] Total de registros carregados: {len(df_final)}")
    else:
        print(f"[ INFO ] Nenhum arquivo encontrado em {BUCKET_NAME} para a data {today}.")



if __name__ == "__main__":
    main()