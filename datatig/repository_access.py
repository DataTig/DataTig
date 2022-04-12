import os


class RepositoryAccess:
    def __init__(self, source_dir: str):
        self._source_dir = source_dir

    def list_files_in_directory(self, directory_name: str):
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

    def get_contents_of_file(self, file_name: str):
        with open(os.path.join(self._source_dir, file_name)) as fp:
            return fp.read()
