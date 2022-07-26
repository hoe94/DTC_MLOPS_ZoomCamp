from datetime import datetime
import pandas as pd
import os
import sys

year = int(sys.argv[1])
month = int(sys.argv[2])
S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')

def dt(hour, minute, second=0):
    return datetime(2021, 1, 1, hour, minute, second)

data = [
    (None, None, dt(1, 2), dt(1, 10)),
    (1, 1, dt(1, 2), dt(1, 10)),
    (1, 1, dt(1, 2, 0), dt(1, 2, 50)),
    (1, 1, dt(1, 2, 0), dt(2, 2, 1)),        
]

def main(year, month):
    input_file = f"s3://nyc-duration-hoe/taxi_type=fhv/year={year:04d}/month={month:02d}/predictions.parquet"
    columns = ['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime']
    df_input = pd.DataFrame(data, columns=columns)

    if S3_ENDPOINT_URL is None:
        options = {
        'client_kwargs': {
            'endpoint_url': S3_ENDPOINT_URL
            }
        }
        df_input.to_parquet(
            input_file,
            engine='pyarrow',
            compression=None,
            index=False,
            storage_options=options
        )
    else:
        df_input.to_parquet(
            input_file,
            engine='pyarrow',
            compression=None,
            index=False,
            storage_options=options
        )

main(year, month)