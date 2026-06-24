from generated.aegis import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetRepoStatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetRepoStatusResponse(_message.Message):
    __slots__ = ("status", "branch", "commit_hash", "is_clean", "modified_files", "ahead_commits", "behind_commits")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    BRANCH_FIELD_NUMBER: _ClassVar[int]
    COMMIT_HASH_FIELD_NUMBER: _ClassVar[int]
    IS_CLEAN_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_FILES_FIELD_NUMBER: _ClassVar[int]
    AHEAD_COMMITS_FIELD_NUMBER: _ClassVar[int]
    BEHIND_COMMITS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    branch: str
    commit_hash: str
    is_clean: bool
    modified_files: _containers.RepeatedScalarFieldContainer[str]
    ahead_commits: int
    behind_commits: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., branch: _Optional[str] = ..., commit_hash: _Optional[str] = ..., is_clean: _Optional[bool] = ..., modified_files: _Optional[_Iterable[str]] = ..., ahead_commits: _Optional[int] = ..., behind_commits: _Optional[int] = ...) -> None: ...

class GetTestResultsRequest(_message.Message):
    __slots__ = ("target", "extra_args")
    TARGET_FIELD_NUMBER: _ClassVar[int]
    EXTRA_ARGS_FIELD_NUMBER: _ClassVar[int]
    target: str
    extra_args: str
    def __init__(self, target: _Optional[str] = ..., extra_args: _Optional[str] = ...) -> None: ...

class TestResult(_message.Message):
    __slots__ = ("suite", "total", "passed", "failed", "errors", "duration_sec", "output")
    SUITE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PASSED_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    DURATION_SEC_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    suite: str
    total: int
    passed: int
    failed: int
    errors: int
    duration_sec: float
    output: str
    def __init__(self, suite: _Optional[str] = ..., total: _Optional[int] = ..., passed: _Optional[int] = ..., failed: _Optional[int] = ..., errors: _Optional[int] = ..., duration_sec: _Optional[float] = ..., output: _Optional[str] = ...) -> None: ...

class GetTestResultsResponse(_message.Message):
    __slots__ = ("status", "results")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    results: _containers.RepeatedCompositeFieldContainer[TestResult]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., results: _Optional[_Iterable[_Union[TestResult, _Mapping]]] = ...) -> None: ...

class GetDiffRequest(_message.Message):
    __slots__ = ("from_branch", "to_branch")
    FROM_BRANCH_FIELD_NUMBER: _ClassVar[int]
    TO_BRANCH_FIELD_NUMBER: _ClassVar[int]
    from_branch: str
    to_branch: str
    def __init__(self, from_branch: _Optional[str] = ..., to_branch: _Optional[str] = ...) -> None: ...

class FileDiff(_message.Message):
    __slots__ = ("path", "status", "diff", "additions", "deletions")
    PATH_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DIFF_FIELD_NUMBER: _ClassVar[int]
    ADDITIONS_FIELD_NUMBER: _ClassVar[int]
    DELETIONS_FIELD_NUMBER: _ClassVar[int]
    path: str
    status: str
    diff: str
    additions: int
    deletions: int
    def __init__(self, path: _Optional[str] = ..., status: _Optional[str] = ..., diff: _Optional[str] = ..., additions: _Optional[int] = ..., deletions: _Optional[int] = ...) -> None: ...

class GetDiffResponse(_message.Message):
    __slots__ = ("status", "files")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    files: _containers.RepeatedCompositeFieldContainer[FileDiff]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., files: _Optional[_Iterable[_Union[FileDiff, _Mapping]]] = ...) -> None: ...

class CreateBranchRequest(_message.Message):
    __slots__ = ("branch_name", "base_branch")
    BRANCH_NAME_FIELD_NUMBER: _ClassVar[int]
    BASE_BRANCH_FIELD_NUMBER: _ClassVar[int]
    branch_name: str
    base_branch: str
    def __init__(self, branch_name: _Optional[str] = ..., base_branch: _Optional[str] = ...) -> None: ...

class CreateBranchResponse(_message.Message):
    __slots__ = ("status", "branch_name")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    BRANCH_NAME_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    branch_name: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., branch_name: _Optional[str] = ...) -> None: ...

class ApplyPatchRequest(_message.Message):
    __slots__ = ("file_path", "patch_content")
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    PATCH_CONTENT_FIELD_NUMBER: _ClassVar[int]
    file_path: str
    patch_content: str
    def __init__(self, file_path: _Optional[str] = ..., patch_content: _Optional[str] = ...) -> None: ...

class ApplyPatchResponse(_message.Message):
    __slots__ = ("status", "applied", "error_detail")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPLIED_FIELD_NUMBER: _ClassVar[int]
    ERROR_DETAIL_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    applied: bool
    error_detail: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., applied: _Optional[bool] = ..., error_detail: _Optional[str] = ...) -> None: ...

class RunTestsRequest(_message.Message):
    __slots__ = ("target", "extra_args", "timeout_seconds")
    TARGET_FIELD_NUMBER: _ClassVar[int]
    EXTRA_ARGS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    target: str
    extra_args: str
    timeout_seconds: int
    def __init__(self, target: _Optional[str] = ..., extra_args: _Optional[str] = ..., timeout_seconds: _Optional[int] = ...) -> None: ...

class RunTestsResponse(_message.Message):
    __slots__ = ("status", "result")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    result: TestResult
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., result: _Optional[_Union[TestResult, _Mapping]] = ...) -> None: ...

class RunLintRequest(_message.Message):
    __slots__ = ("target", "linter")
    TARGET_FIELD_NUMBER: _ClassVar[int]
    LINTER_FIELD_NUMBER: _ClassVar[int]
    target: str
    linter: str
    def __init__(self, target: _Optional[str] = ..., linter: _Optional[str] = ...) -> None: ...

class RunLintResponse(_message.Message):
    __slots__ = ("status", "passed", "error_count", "warning_count", "output")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PASSED_FIELD_NUMBER: _ClassVar[int]
    ERROR_COUNT_FIELD_NUMBER: _ClassVar[int]
    WARNING_COUNT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    passed: bool
    error_count: int
    warning_count: int
    output: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., passed: _Optional[bool] = ..., error_count: _Optional[int] = ..., warning_count: _Optional[int] = ..., output: _Optional[str] = ...) -> None: ...

class CreateCommitRequest(_message.Message):
    __slots__ = ("message", "files")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    message: str
    files: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, message: _Optional[str] = ..., files: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateCommitResponse(_message.Message):
    __slots__ = ("status", "commit_hash")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    COMMIT_HASH_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    commit_hash: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., commit_hash: _Optional[str] = ...) -> None: ...

class CreatePullRequestRequest(_message.Message):
    __slots__ = ("title", "description", "head_branch", "base_branch")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    HEAD_BRANCH_FIELD_NUMBER: _ClassVar[int]
    BASE_BRANCH_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    head_branch: str
    base_branch: str
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., head_branch: _Optional[str] = ..., base_branch: _Optional[str] = ...) -> None: ...

class CreatePullRequestResponse(_message.Message):
    __slots__ = ("status", "pr_url", "pr_number")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PR_URL_FIELD_NUMBER: _ClassVar[int]
    PR_NUMBER_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    pr_url: str
    pr_number: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., pr_url: _Optional[str] = ..., pr_number: _Optional[int] = ...) -> None: ...

class RevertChangesRequest(_message.Message):
    __slots__ = ("target", "commit_hash")
    TARGET_FIELD_NUMBER: _ClassVar[int]
    COMMIT_HASH_FIELD_NUMBER: _ClassVar[int]
    target: str
    commit_hash: str
    def __init__(self, target: _Optional[str] = ..., commit_hash: _Optional[str] = ...) -> None: ...

class RevertChangesResponse(_message.Message):
    __slots__ = ("status", "reverted_files")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REVERTED_FILES_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    reverted_files: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ..., reverted_files: _Optional[_Iterable[str]] = ...) -> None: ...
