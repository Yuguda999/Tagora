import mlflow
import os


def init_mlflow():
    mlflow.set_tracking_uri(f"file://{os.getcwd()}/mlruns")
    mlflow.set_experiment("visual_search")

def log_run(params: dict, metrics: dict, artifacts: dict = None):
    with mlflow.start_run():
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        if artifacts:
            for name, path in artifacts.items():
                mlflow.log_artifact(path, artifact_path=name)
