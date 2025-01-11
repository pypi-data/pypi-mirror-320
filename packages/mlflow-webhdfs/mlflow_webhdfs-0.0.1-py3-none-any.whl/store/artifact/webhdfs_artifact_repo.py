import os
import posixpath
import urllib.parse
from hdfs import InsecureClient, TokenClient
from mlflow.entities import FileInfo
from mlflow.environment_variables import MLFLOW_KERBEROS_USER
from mlflow.store.artifact.artifact_repo import ArtifactRepository
from mlflow.utils.file_utils import relative_path_to_artifact_path


class WebHdfsArtifactRepository(ArtifactRepository):
    """
    Stores artifacts on WebHDFS.
    This repository is used with URIs of the form `webhdfs://<host>:<port>/<path>`.
    """

    def __init__(self, artifact_uri):
        self.scheme, self.host, self.port, self.path = _resolve_connection_params(artifact_uri)
        super().__init__(artifact_uri)

        # Initialize the WebHDFS client
        self.client = self._initialize_client()

    def _initialize_client(self):
        # Check if Kerberos token is available
        token = os.environ.get("MLFLOW_KERBEROS_TOKEN")
        if token:
            return TokenClient(self._get_hdfs_url(), token=token)
        else:
            user = os.environ.get("MLFLOW_KERBEROS_USER")
            return InsecureClient(self._get_hdfs_url(), user=user)

    def _get_hdfs_url(self):
        return f"http://{self.host}:{self.port}"

    def log_artifact(self, local_file, artifact_path=None):
        """
        Log artifact to WebHDFS.
        """
        hdfs_base_path = _resolve_base_path(self.path, artifact_path)
        _, file_name = os.path.split(local_file)
        destination_path = posixpath.join(hdfs_base_path, file_name)

        with open(local_file, "rb") as source:
            self.client.write(destination_path, source)

    def log_artifacts(self, local_dir, artifact_path=None):
        """
        Log artifacts in WebHDFS.
        Missing remote sub-directories will be created if needed.
        """
        hdfs_base_path = _resolve_base_path(self.path, artifact_path)

        if not self.client.status(hdfs_base_path, strict=False):
            self.client.makedirs(hdfs_base_path)

        for subdir_path, _, files in os.walk(local_dir):
            relative_path = _relative_path_local(local_dir, subdir_path)

            hdfs_subdir_path = posixpath.join(hdfs_base_path, relative_path) if relative_path else hdfs_base_path

            if not self.client.status(hdfs_subdir_path, strict=False):
                self.client.makedirs(hdfs_subdir_path)

            for each_file in files:
                source_path = os.path.join(subdir_path, each_file)
                destination_path = posixpath.join(hdfs_subdir_path, each_file)
                with open(source_path, "rb") as source:
                    self.client.write(destination_path, source)

    def list_artifacts(self, path=None):
        """
        Lists files and directories under the artifacts directory for the current run_id.
        """
        hdfs_base_path = _resolve_base_path(self.path, path)
        if path is None:
            path = ""

        paths = []
        if self.client.status(hdfs_base_path, strict=False):
            for filestat in self.client.list(hdfs_base_path, status=True):
                filename, fileinfo = filestat
                size = fileinfo["length"]
                rel_path = posixpath.join(path, filename)
                paths.append(FileInfo(rel_path, is_dir=fileinfo["type"] == "DIRECTORY", file_size=size))

        return sorted(paths, key=lambda f: f.file_size)

    def _is_directory(self, artifact_path):
        """
        Check if a given artifact path is a directory.
        """
        hdfs_base_path = _resolve_base_path(self.path, artifact_path)
        try:
            file_info = self.client.status(hdfs_base_path)
            return file_info["type"] == "DIRECTORY"
        except:
            return False

    def _download_file(self, remote_file_path, local_path):
        """
        Download a file from WebHDFS.
        """
        hdfs_base_path = _resolve_base_path(self.path, remote_file_path)
        self.client.download(hdfs_base_path, local_path)

    def delete_artifacts(self, artifact_path=None):
        """
        Delete artifacts from WebHDFS.
        """
        path = posixpath.join(self.path, artifact_path) if artifact_path else self.path
        try:
            self.client.delete(path, recursive=True)
        except:
            pass


def _resolve_connection_params(artifact_uri):
    parsed = urllib.parse.urlparse(artifact_uri)
    return parsed.scheme, parsed.hostname, parsed.port, parsed.path


def _resolve_base_path(path, artifact_path):
    if path == artifact_path:
        return path
    if artifact_path:
        return posixpath.join(path, artifact_path)
    return path


def _relative_path(base_dir, subdir_path, path_module):
    relative_path = path_module.relpath(subdir_path, base_dir)
    return relative_path if relative_path != "." else None


def _relative_path_local(base_dir, subdir_path):
    rel_path = _relative_path(base_dir, subdir_path, os.path)
    return relative_path_to_artifact_path(rel_path) if rel_path is not None else None


def _relative_path_remote(base_dir, subdir_path):
    return _relative_path(base_dir, subdir_path, posixpath)
