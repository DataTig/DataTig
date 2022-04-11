class GitCommitModel:
    def __init__(self, commit_hash):
        self._commit_hash = commit_hash

    def get_commit_hash(self):
        return self._commit_hash
