from datetime import datetime
import pandas as pd

def dt(hour, minute, second=0):
    return datetime(2021, 1, 1, hour, minute, second)

data = [
    (None, None, dt(1, 2), dt(1, 10)),
    (1, 1, dt(1, 2), dt(1, 10)),
    (1, 1, dt(1, 2, 0), dt(1, 2, 50)),
    (1, 1, dt(1, 2, 0), dt(2, 2, 1)),        
]

columns = ['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime']
test_df = pd.DataFrame(data, columns=columns)
test_df_dict = test_df.to_dict(orient = 'records')

def prepare_data():
    categorical = ['PUlocationID', 'DOlocationID']
    df = pd.read_parquet(f'https://raw.githubusercontent.com/alexeygrigorev/datasets/master/nyc-tlc/fhv/fhv_tripdata_2021-02.parquet')
    
    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    df = df[['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime']]
    expected_df_dict = df.head(4).to_dict(orient='records')


    assert expected_df_dict == test_df_dict

#prepare_data()
#expected_data = [
#    ('1/2/2021 12:01 AM',	'1/2/2021 1:33 AM' ,	'152',	'244'),
#    ('1/2/2021 12:55 AM',	'1/2/2021 1:06 AM ',	'173',	'82'),     
#    ('1/2/2021 12:14 AM',	'1/2/2021 12:28 AM',	'173',	'56'),     
#    ('1/2/2021 12:27 AM',	'1/2/2021 12:35 AM',	'82',	'129'),   
#    ('1/2/2021 12:12 AM',	'1/2/2021 12:26 AM',	'23', 	'225'),
#]
#expected_columns = ['dispatching_batch_num', 'pickup_datetime', 'PUlocationID', 'DOlocationID']
#expected_df = pd.DataFrame(expected_data, columns = expected_columns)
#
#def prepare_data():
#    assert expected_df == df

#print(df.reset_index().drop(column = index))