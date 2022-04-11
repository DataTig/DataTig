import os
import subprocess
from typing import Optional

from datatig.models.git_commit import GitCommitModel


class RepositoryAccess:
    def __init__(self, source_dir: str):
        self._source_dir = source_dir
        self._commit_hash: Optional[str] = None

    def set_commit_hash(self, commit_hash: str) -> None:
        self._commit_hash = commit_hash if commit_hash != "HEAD" else None

    def list_files_in_directory(self, directory_name: str):
        out = []
        if self._commit_hash:
            process = subprocess.Popen(
                ["git", "ls-tree", "-r", self._commit_hash],
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
        else:
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

    def get_contents_of_file(self, file_name: str):
        if self._commit_hash:
            process = subprocess.Popen(
                ["git", "show", self._commit_hash + ":" + file_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self._source_dir,
            )
            stdout, stderr = process.communicate()
            return stdout.decode("utf-8").strip()
        else:
            with open(os.path.join(self._source_dir, file_name)) as fp:
                return fp.read()

    def get_current_commit(self):
        if self._commit_hash:
            return GitCommitModel(self._commit_hash)
        else:
            process = subprocess.Popen(
                ["git", "rev-parse", "HEAD"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self._source_dir,
            )
            stdout, stderr = process.communicate()
            output = stdout.decode("utf-8").strip()
            return GitCommitModel(output)
