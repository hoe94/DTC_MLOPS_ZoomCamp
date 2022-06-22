import pickle
import pandas as pd

with open('model.bin', 'rb') as f_in:
    dv, lr = pickle.load(f_in)


categorical = ['PUlocationID', 'DOlocationID']

def customize_file_name(year, month):
    #return f"C:/Users/Hoe/Desktop/Learning/DataTalksClub_MLOPS/data/fhv_tripdata_{year}-{month}.parquet"
    return f"/app/fhv_tripdata_{year}-{month}.parquet"

def read_data(filename):
    df = pd.read_parquet(filename)
    
    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    return df


def main():
    file_name = customize_file_name('2021', '06')
    df = read_data(file_name)
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)
    print(f'Mean predicted duration: {y_pred.mean()}')

if __name__ == "__main__":
    main()


