# mlflow-webhdfs

The `mlflow-webhdfs` package is a plugin for MLFlow that enables WebHDFS as an artifact store. This allows you to use `webhdfs://` URLs as a storage location for your MLFlow artifacts, facilitating the integration of HDFS (Hadoop Distributed File System) with MLFlow.

## Features
- Integration of WebHDFS with MLFlow as an artifact store.
- Supports `webhdfs://` as an artifact URL.
- Seamlessly upload and download MLFlow artifacts to and from HDFS.
- Supports Kerberos authentication via `MLFLOW_KERBEROS_TOKEN` and `MLFLOW_KERBEROS_USER` environment variables.

## Requirements
- **MLFlow**: Version 2.4.0 or later.
- **HDFS**: The Python `hdfs` library for interacting with WebHDFS.
- **Environment Variables (optional)**: If using authentication, set the appropriate environment variables (`MLFLOW_KERBEROS_TOKEN` or `MLFLOW_KERBEROS_USER`).

## Installation

To install `mlflow-webhdfs`, use `pip` to install it directly from the Python Package Index (PyPI) or from source:

### Install from PyPI

```bash
pip install mlflow-webhdfs
```

### Install from Source

Clone the repository and install via `setup.py`:

```bash
git clone https://github.com/roach231428/mlflow-webhdfs.git
cd mlflow-webhdfs
pip install -e .
```

## Setup

Once the package is installed, you can use WebHDFS as an artifact store in your MLFlow project. The plugin allows you to specify a `webhdfs://` URL when configuring artifact locations.

### Usage

In your MLFlow script, use the `webhdfs` protocol when setting the artifact location. Here's an example of how to use the plugin in your MLFlow code:

```python
import mlflow

# Set the WebHDFS artifact location
artifact_uri = "webhdfs://<webhdfs_host>:<port>/path/to/store/artifacts"

# Set the artifact URI for the MLflow run
mlflow.set_tracking_uri(artifact_uri)

# Log your MLFlow experiments
with mlflow.start_run():
    mlflow.log_param("param1", 5)
    mlflow.log_metric("metric1", 0.92)
    mlflow.log_artifact("my_artifact.txt")
```

### Environment Variables
- `MLFLOW_KERBEROS_USER`: Specifies the username for `hdfs.InsecureClient`.
- `MLFLOW_KERBEROS_TOKEN`: Specifies the token for `hdfs.TokenClient`. If set, the plugin will use `hdfs.TokenClient` instead.

If neither of these environment variables is set, the plugin will fall back to using the `hdfs.InsecureClient`.

## Configuration

No additional configuration is needed beyond specifying the `webhdfs://` artifact URI and setting up the authentication environment variables if needed.

## Development

To contribute or modify the plugin, follow these steps:

1. Clone the repository.
2. Install the development dependencies.

    ```bash
    pip install -r requirements.txt
    ```

3. Make your changes, and run tests (if any) to ensure the plugin functions correctly.
4. Create a pull request with your changes.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more details.

## Contact

For any issues, please open an issue on the [GitHub repository](https://github.com/roach231428/mlflow-webhdfs). For questions or comments, you can reach out to the author at [roach231428@gmail.com](mailto:roach231428@gmail.com).