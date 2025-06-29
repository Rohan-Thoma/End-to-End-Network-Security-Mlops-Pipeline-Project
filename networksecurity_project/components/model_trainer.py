import os, sys

from networksecurity_project.exception.exception import NetworkSecurityException
from networksecurity_project.logging.logger import logging

from networksecurity_project.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from networksecurity_project.entity.config_entity import ModelTrainerConfig

from networksecurity_project.utils.ml_utils.model.estimator import NetworkModel
from networksecurity_project.utils.main_utils.utils import save_object, load_object
from networksecurity_project.utils.main_utils.utils import load_numpy_array_data, evaluate_models
from networksecurity_project.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier
)
import mlflow 
import dagshub
dagshub.init(repo_owner='lolguy699', repo_name='End-to-End-Network-Security-Mlops-Pipeline-Project', mlflow=True)

mlflow.set_tracking_uri("https://dagshub.com/lolguy699/End-to-End-Network-Security-Mlops-Pipeline-Project.mlflow")

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) # type: ignore
        
    def track_mlflow(self,best_model, classificationmetric, model_name):
        with mlflow.start_run():
            f1_score= classificationmetric.f1_score
            precision_score = classificationmetric.precision_score
            recall_score = classificationmetric.recall_score

            mlflow.log_metric("f1_score", f1_score)
            mlflow.log_metric("precision_score", precision_score)
            mlflow.log_metric("recall_score", recall_score)
            mlflow.sklearn.log_model(best_model, artifact_path=model_name)


    def train_model(self, X_train, y_train, X_test, y_test):
        models={
            "Random_Forest": RandomForestClassifier(verbose=1),
            "Decision_Tree": DecisionTreeClassifier(),
            "Gradient_Boosting": GradientBoostingClassifier(verbose=1),
            "Logistic_Regression": LogisticRegression(verbose=1),
            "AdaBoost": AdaBoostClassifier()
        }

        params={
            "Decision_Tree": {
                "criterion": ["gini", "entropy", "log_loss"]
                # 'spitter': ['best', 'random'],
                # 'max_features': ['sqrt', 'log2']
            },
            "Random_Forest":{
                # "criterion": ["gini", "entropy", "log_loss"],
                # "max_features" : ['sqrt', 'log2', None],
                'n_estimators': [8,16,32,64,128,256]
            },
            "Gradient_Boosting":{
                # 'loss': ['log_loss', 'exponential'],
                'learning_rate': [.1,.01,.05,.001],
                'subsample': [0.6,0.7,0.75,0.8,0.85,0.9],
                # "criterion": ["squared_error", "friedman_mse"],
                # "max_features" : ['sqrt', 'log2', 'auto'],
                'n_estimators': [8,16,32,64,128,256]
            },
            "Logistic_Regression":{},
            "AdaBoost":{
                'learning_rate':[0.1, 0.01, 0.5, 0.001],
                'n_estimators': [8,16,32,64,128,256]
            }
        }
        model_report:dict = evaluate_models(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test, models=models, params=params)

        #to get the best model score from dict
        best_model_score = max(sorted(model_report.values()))

        #to the best model name from dict
        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]

        best_model = models[best_model_name]

        y_train_pred= best_model.predict(X_train)

        classification_train_metric=get_classification_score(y_true=y_train, y_pred=y_train_pred)

        ## track the train metrics with mlflow
        self.track_mlflow(best_model, classification_train_metric, best_model_name)


        y_test_pred = best_model.predict(X_test)
        classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)

        ## track the testn metrics with mlflow
        self.track_mlflow(best_model, classification_test_metric, best_model_name)

        preprocessor = load_object(file_path= self.data_transformation_artifact.transformed_object_file_path)

        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path, exist_ok=True)

        Network_Model=NetworkModel(preprocessor=preprocessor, model=best_model)

        save_object(self.model_trainer_config.trained_model_file_path, obj=Network_Model)

        #save the best model in another folder
        save_object("final_model/model.pkl", best_model)

        ## Model trainer Artifact
        model_trainer_artifact = ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                                                      train_metric_artifact= classification_train_metric,
                                                      test_metric_artifact=classification_test_metric)
        
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")

        return model_trainer_artifact

    def initiate_model_trainer(self)-> ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            #loading the training and testing array
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:,-1],
                test_arr[:,:-1],
                test_arr[:,-1]
            )

            model_trainer_artifact = self.train_model(x_train,y_train, x_test, y_test)
            return model_trainer_artifact
    
        except Exception as e:
            raise NetworkSecurityException(e, sys) # type: ignore