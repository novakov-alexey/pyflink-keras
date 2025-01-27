from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from pyflink.common import Configuration
from pyflink.datastream import StreamExecutionEnvironment

def accuracy():
    """
    This function is a hello-world function for scikit-learn.
    It loads the Iris dataset, splits it into training and testing sets, and trains a random forest classifier.
    :return: The model
    """
    # Load the Iris dataset
    iris = load_iris()
    X = iris.data
    y = iris.target

    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Train a random forest classifier
    model = RandomForestClassifier()
    model.fit(X_train, y_train)    
    return f'Model accuracy: {model.score(X_test, y_test)}'


if __name__ == '__main__':    
    config = Configuration()    
    env = StreamExecutionEnvironment.get_execution_environment(config)
    # env.set_python_requirements(
    #     requirements_file_path="/flink/usrlib/ann-requirements.txt"        
    # )

    env.from_collection(["Check Model"]).map(lambda _: accuracy()).print()
    env.execute("Check Model")