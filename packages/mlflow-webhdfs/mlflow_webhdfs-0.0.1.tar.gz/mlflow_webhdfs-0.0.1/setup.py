from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mlflow-webhdfs",
    version="0.0.1",
    description="MLflow WebHDFS Plugins",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    author="roach231428",
    author_email="roach231428@gmail.com",
    url="https://github.com/roach231428/mlflow-webhdfs",
    install_requires=[
        "mlflow",
        "hdfs",
    ],
    entry_points={
        "mlflow.artifact_repository": [
            "webhdfs=store.artifact.webhdfs_artifact_repo:WebHdfsArtifactRepository",
        ],
    },
    license="Apache License 2.0",
)
