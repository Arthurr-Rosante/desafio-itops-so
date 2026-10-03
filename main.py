import io, os, boto3
import pandas as pd

def main():
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        region_name=os.getenv("AWS_REGION")
    )
    s3_client = session.client("s3")

    bucket_name="itops-04261042"
    file_key = "01-bronze/2026-02-10_22-30_ap01.json"

    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)

    df = pd.read_csv(io.BytesIO(response["Body"].read()), sep=";")
    print(df.head())


if __name__ == "__main__":
    main()
