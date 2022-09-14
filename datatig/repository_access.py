import os
import subprocess
from abc import ABC, abstractmethod

from datatig.models.git_commit import GitCommitModel


class RepositoryAccess(ABC):
    @abstractmethod
    def list_files_in_directory(self, directory_name: str) -> list:
        return []

    @abstractmethod
    def get_contents_of_file(self, file_name: str) -> str:
        return ""

    @abstractmethod
    def has_file(self, file_name: str) -> bool:
        return False


class RepositoryAccessLocalFiles(RepositoryAccess):
    def __init__(self, source_dir: str):
        self._source_dir = source_dir

    def has_file(self, file_name: str) -> bool:
        full_start_dir = os.path.abspath(self._source_dir)
        for path, subdirs, files in os.walk(self._source_dir):
            for name in files:
                full_filename = os.path.abspath(os.path.join(path, name))
                found_filename = full_filename[len(full_start_dir) + 1 :]
                if found_filename == file_name:
                    return True
        return False

    def list_files_in_directory(self, directory_name: str) -> list:
        out = []
        start_dir = os.path.join(self._source_dir, directory_name)
        full_start_dir = os.path.abspath(start_dir)
        for path, subdirs, files in os.walk(full_start_dir):
            for name in files:
                full_filename = os.path.abspath(os.path.join(path, name))
                out.append(
                    {
                        "name": name,
                        "path_relative_to_dir": full_filename[
                            len(full_start_dir) + 1 :
                        ],
                    }
                )
        return out

    def get_contents_of_file(self, file_name: str) -> str:
        with open(os.path.join(self._source_dir, file_name)) as fp:
            return fp.read()


class RepositoryAccessLocalGit(RepositoryAccess):
    def __init__(self, source_dir: str):
        self._source_dir = source_dir
        self._ref: str = "HEAD"

    def set_ref(self, ref: str) -> None:
        self._ref = ref if ref else "HEAD"

    def has_file(self, file_name: str) -> bool:
        process = subprocess.Popen(
            ["git", "ls-tree", "-r", self._ref],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self._source_dir,
        )
        stdout, stderr = process.communicate()
        for line in stdout.decode("utf-8").strip().split("\n"):
            path_relative_to_repo = line.split("\t")[-1]
            if path_relative_to_repo == file_name:
                return True
        return False

    def list_files_in_directory(self, directory_name: str) -> list:
        out = []
        process = subprocess.Popen(
            ["git", "ls-tree", "-r", self._ref],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self._source_dir,
        )
        stdout, stderr = process.communicate()
        for line in stdout.decode("utf-8").strip().split("\n"):
            path_relative_to_repo = line.split("\t")[-1]
            if path_relative_to_repo.startswith(directory_name):
                out.append(
                    {
                        "name": os.path.basename(path_relative_to_repo),
                        "path_relative_to_dir": path_relative_to_repo[
                            len(directory_name) + 1 :
                        ],
                    }
                )
        return out

    def get_contents_of_file(self, file_name: str) -> str:
        process = subprocess.Popen(
            ["git", "show", self._ref + ":" + file_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self._source_dir,
        )
        stdout, stderr = process.communicate()
        return stdout.decode("utf-8").strip()

    def get_current_commit(self) -> GitCommitModel:
        process = subprocess.Popen(
            ["git", "rev-parse", self._ref],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self._source_dir,
        )
        stdout, stderr = process.communicate()
        output = stdout.decode("utf-8").strip()
        refs = [self._ref] if self._ref != output else []
        return GitCommitModel(output, refs)

    def list_branches(self) -> list:
        out = []
        process = subprocess.Popen(
            ["git", "branch"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self._source_dir,
        )
        stdout, stderr = process.communicate()
        for line in stdout.decode("utf-8").strip().split("\n"):
            line = line.strip()
            if line.startswith("* "):
                line = line[2:]
            if line:
                out.append(line)
        return out
