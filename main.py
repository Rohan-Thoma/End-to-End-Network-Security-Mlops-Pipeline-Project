from networksecurity_project.components.data_ingestion import DataInjestion
from networksecurity_project.components.data_validation import DataValidation
from networksecurity_project.components.data_transformation import DataTransformation
from networksecurity_project.components.model_trainer import ModelTrainer

from networksecurity_project.exception.exception import NetworkSecurityException
from networksecurity_project.logging.logger import logging
from networksecurity_project.entity.config_entity import DataIngestionConfig, DataValidationConfig,\
    DataTransformationConfig, ModelTrainerConfig,  TrainingPipelineConfig
import sys

if __name__=="__main__":
    try:
        training_pipeline_config= TrainingPipelineConfig() 
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        data_ingestion = DataInjestion(data_ingestion_config=data_ingestion_config)

        logging.info("Initiated the data ingestion config")
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        
        print(data_ingestion_artifact)
        logging.info("Data ingestion completed")

        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact, data_validation_config=data_validation_config)
        logging.info("Initiated the data validation config")
        data_validation_artifact = data_validation.initiate_data_validation()
        
        print(data_validation_artifact)
        logging.info("Data Validation completed")

        data_transformation_config = DataTransformationConfig(training_pipeline_config)
        data_transformation=DataTransformation(data_validation_artifact=data_validation_artifact, data_transformation_config= data_transformation_config)
        logging.info("Initiated the data transformation config")
        data_transformation_artifact = data_transformation.initiate_data_transformation()

        print(data_transformation_artifact)
        logging.info("Data Transformation completed")

        logging.info("Model Training started")
        model_trainer_config = ModelTrainerConfig(training_pipeline_config)
        model_trainer=ModelTrainer(model_trainer_config=model_trainer_config, data_transformation_artifact=data_transformation_artifact)
        model_trainer_artifact = model_trainer.initiate_model_trainer()

        logging.info("Model training artifact created")


    except Exception as e:
        raise NetworkSecurityException(e,sys)
    