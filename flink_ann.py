import tensorflow as tf
import numpy as np
import pandas as pd
import argparse
import logging
import sys
import argparse

from sklearn.preprocessing import LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import (DataTypes, TableDescriptor, Schema, StreamTableEnvironment, TableEnvironment, EnvironmentSettings)
from pyflink.table.udf import ScalarFunction, udf
from pyflink.table.expressions import col, range_, with_columns
from pyflink.common import Row, Configuration

class Predict(ScalarFunction):
    def __init__(self, transform, kerasModelPath: str):
        self.transform = transform
        self.kerasModelPath = kerasModelPath

    def open(self, func_context):
        import tensorflow as tf        
        self.ann = tf.keras.models.load_model(self.kerasModelPath)        

    def eval(self, *args):        
        a = np.array([args])
        features = self.transform(a).flatten()
        prediction = self.ann.predict(np.array([features]))[0, 0]        
        return Row(raw_prediction=prediction, exited=prediction > 0.5)

def churn_analysis(trainDataPath: str, liveDataPath: str, kerasModelPath: str):    
    dataset = pd.read_csv(trainDataPath)
    features = dataset.iloc[:, 3:-1].values

    le = LabelEncoder()
    features[:, 2] = le.fit_transform(features[:, 2])

    ct = ColumnTransformer(transformers=[('encoder', OneHotEncoder(), [1])], remainder='passthrough')
    features = np.array(ct.fit_transform(features))

    sc = StandardScaler()
    sc.fit(features)

    def transform(arr_2d):
        arr_2d[:, 2] = le.transform(arr_2d[:, 2])
        a = ct.transform(arr_2d)
        return sc.transform(a)
    
    t_env = TableEnvironment.create(EnvironmentSettings.in_streaming_mode())

    schema = (Schema.new_builder()              
              .column("RowNumber", DataTypes.INT())
              .column("CustomerId", DataTypes.INT())
              .column("Surname", DataTypes.STRING())
              .column("CreditScore", DataTypes.DOUBLE())
              .column("Geography", DataTypes.STRING())
              .column("Gender", DataTypes.STRING())
              .column("Age", DataTypes.DOUBLE())
              .column("Tenure", DataTypes.DOUBLE())
              .column("Balance", DataTypes.DOUBLE())
              .column("NumOfProducts", DataTypes.DOUBLE())
              .column("HasCrCard", DataTypes.DOUBLE())
              .column("IsActiveMember", DataTypes.DOUBLE())
              .column("EstimatedSalary", DataTypes.DOUBLE())
              .column("Exited", DataTypes.DOUBLE())              
              .build())
        
    tableDesc = (TableDescriptor
                .for_connector('filesystem')
                .schema(schema)
                .option("path", liveDataPath)
                .option("format", "csv")
                .option("csv.allow-comments", "true")
                .build())
    
    predict = udf(Predict(transform, kerasModelPath), result_type=DataTypes.ROW(
        [
            DataTypes.FIELD('raw_prediction', DataTypes.FLOAT()),
            DataTypes.FIELD('exited', DataTypes.BOOLEAN())
        ]))
    t_env.create_temporary_function("predict", predict)

    clients = t_env.from_descriptor(tableDesc)
    cols = with_columns(range_('CreditScore', 'EstimatedSalary'))

    clients.select(predict(cols)) \
        .execute() \
        .print()

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--extractor-train-file',
        dest='trainDataPath',
        required=False,
        default='./Churn_Modelling.csv',
        help='Path to CSV trainining file for the Feature Exractor')
    parser.add_argument(
        '--live-data-file',
        dest='liveDataPath',
        required=False,
        default='./test_data/Churn_Modelling.csv',
        help='Path to CSV live data file for model inference')
        
    parser.add_argument(
        '--keras-model-file',
        dest='kerasModelPath',
        required=False,
        default='./saved_model/ann-customer-churn.keras',
        help='Path to Kearas Model file')

    argv = sys.argv[1:]
    known_args, _ = parser.parse_known_args(argv)
    
    churn_analysis(known_args.trainDataPath, known_args.liveDataPath, known_args.kerasModelPath)