class GitCommitModel:
    def __init__(self, commit_hash, refs: list = []):
        self._commit_hash = commit_hash
        self._refs: list = refs

    def get_commit_hash(self):
        return self._commit_hash

    def get_refs(self):
        return self._refs
