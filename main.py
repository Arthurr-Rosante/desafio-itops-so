import io, os, boto3, psutil, json, logging
from datetime import datetime

from utils.random_antena import gen_random_antena_capture

OUTPUT_DIR = "out"

def main():
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        region_name=os.getenv("AWS_REGION")
    )
    s3_client = session.client("s3")

    bucket_name="itops-04261042"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    captura_antena = gen_random_antena_capture()

    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    fpath = f"./{OUTPUT_DIR}/{now}_ap01.json"

    data_list = []
    if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
        with open(fpath, "r") as f:
            data_list = json.load(f)

    data_list.append(captura_antena)
    with open(fpath, "w") as f:
        json.dump(data_list, f, indent=2)

if __name__ == "__main__":
    main()
