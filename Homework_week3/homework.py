import pandas as pd

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

from prefect import flow, task, logging
from prefect.task_runners import SequentialTaskRunner

from prefect.deployments import DeploymentSpec
from prefect.orion.schemas.schedules import CronSchedule
from prefect.flow_runners import SubprocessFlowRunner

import prefect

from datetime import date, datetime
import pickle

@task
def get_paths(date):
    if date is None:
        date = date.today()
        previous_2_months = date.month - 2
        previous_month = date.month - 1
        return f'/mnt/c/Users/Hoe/Desktop/Learning/DataTalksClub_MLOPS/data/fhv_tripdata_2021-0{previous_2_months}.parquet', f'/mnt/c/Users/Hoe/Desktop/Learning/DataTalksClub_MLOPS/data/fhv_tripdata_2021-0{previous_month}.parquet'
    else:
        date = datetime.strptime(date, '%Y-%m-%d')
        previous_2_months = date.month - 2
        previous_month = date.month - 1
        return f'/mnt/c/Users/Hoe/Desktop/Learning/DataTalksClub_MLOPS/data/fhv_tripdata_2021-0{previous_2_months}.parquet', f'/mnt/c/Users/Hoe/Desktop/Learning/DataTalksClub_MLOPS/data/fhv_tripdata_2021-0{previous_month}.parquet'
        

@task
def read_data(path):
    df = pd.read_parquet(path)
    return df

@task
def prepare_features(df, categorical, train=True):
    logger = logging.get_run_logger("prefect")
    
    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    mean_duration = df.duration.mean()
    if train:
        #print(f"The mean duration of training is {mean_duration}")
        logger.info(f"The mean duration of training is {mean_duration}")
    else:
        #print(f"The mean duration of validation is {mean_duration}")
        logger.info(f"The mean duration of validation is {mean_duration}")
    
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df

@task
def train_model(df, categorical):
    logger = logging.get_run_logger("prefect")
    
    train_dicts = df[categorical].to_dict(orient='records')
    dv = DictVectorizer()
    X_train = dv.fit_transform(train_dicts) 
    y_train = df.duration.values

    #print(f"The shape of X_train is {X_train.shape}")
    #print(f"The DictVectorizer has {len(dv.feature_names_)} features")
    
    logger.info(f"The shape of X_train is {X_train.shape}")
    logger.info(f"The DictVectorizer has {len(dv.feature_names_)} features")
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_train)
    mse = mean_squared_error(y_train, y_pred, squared=False)
    #print(f"The MSE of training is: {mse}")
    logger.info(f"The MSE of training is : {mse}")
    return lr, dv

@task
def run_model(df, categorical, dv, lr):
    logger = logging.get_run_logger("prefect")
    
    val_dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(val_dicts) 
    y_pred = lr.predict(X_val)
    y_val = df.duration.values

    mse = mean_squared_error(y_val, y_pred, squared=False)
    #print(f"The MSE of validation is: {mse}")
    logger.info(f"The MSE of validation is: {mse}")
    return

@flow(name = 'homework_week3', task_runner = SequentialTaskRunner())
def main(date=None):
#def main(train_path: str = '/mnt/c/Users/Hoe/Desktop/Learning/DataTalksClub_MLOPS/data/fhv_tripdata_2021-01.parquet', 
#           val_path: str = '/mnt/c/Users/Hoe/Desktop/Learning/DataTalksClub_MLOPS/data/fhv_tripdata_2021-02.parquet'):
    train_path, val_path = get_paths(date).result()
    
    categorical = ['PUlocationID', 'DOlocationID']

    df_train = read_data(train_path)
    df_train_processed = prepare_features(df_train, categorical)

    df_val = read_data(val_path)
    df_val_processed = prepare_features(df_val, categorical)

    # train the model
    lr, dv = train_model(df_train_processed, categorical).result()
    run_model(df_val_processed, categorical, dv, lr)
    
    with open(f'/mnt/c/Users/Hoe/Desktop/Learning/DataTalksClub_MLOPS/models/models-{date}.bin', 'wb') as f_out:
        pickle.dump(lr, f_out)
        
    with open(f'/mnt/c/Users/Hoe/Desktop/Learning/DataTalksClub_MLOPS/models/dv-{date}.b', 'wb') as f_out:
        pickle.dump(dv, f_out)
    
#main('2021-08-15')
DeploymentSpec(
    flow = main,
    name = "homework_model_training",
    schedule = CronSchedule(
        cron ="0 9 15 * *",
        timezone = "America/New_York"),
    flow_runner = SubprocessFlowRunner(),
    tags = ["ml"]
)