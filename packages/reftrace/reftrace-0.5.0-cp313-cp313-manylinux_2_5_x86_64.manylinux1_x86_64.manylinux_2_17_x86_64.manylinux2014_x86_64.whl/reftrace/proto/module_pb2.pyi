from proto import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Directive(_message.Message):
    __slots__ = ("line", "accelerator", "after_script", "arch", "array", "before_script", "cache", "cluster_options", "conda", "container", "container_options", "cpus", "debug", "disk", "echo", "error_strategy", "executor", "ext", "fair", "label", "machine_type", "max_submit_await", "max_errors", "max_forks", "max_retries", "memory", "module", "penv", "pod", "publish_dir", "queue", "resource_labels", "resource_limits", "scratch", "shell", "spack", "stage_in_mode", "stage_out_mode", "store_dir", "tag", "time", "dynamic", "unknown")
    LINE_FIELD_NUMBER: _ClassVar[int]
    ACCELERATOR_FIELD_NUMBER: _ClassVar[int]
    AFTER_SCRIPT_FIELD_NUMBER: _ClassVar[int]
    ARCH_FIELD_NUMBER: _ClassVar[int]
    ARRAY_FIELD_NUMBER: _ClassVar[int]
    BEFORE_SCRIPT_FIELD_NUMBER: _ClassVar[int]
    CACHE_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    CONDA_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    CPUS_FIELD_NUMBER: _ClassVar[int]
    DEBUG_FIELD_NUMBER: _ClassVar[int]
    DISK_FIELD_NUMBER: _ClassVar[int]
    ECHO_FIELD_NUMBER: _ClassVar[int]
    ERROR_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    EXECUTOR_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    FAIR_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    MACHINE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MAX_SUBMIT_AWAIT_FIELD_NUMBER: _ClassVar[int]
    MAX_ERRORS_FIELD_NUMBER: _ClassVar[int]
    MAX_FORKS_FIELD_NUMBER: _ClassVar[int]
    MAX_RETRIES_FIELD_NUMBER: _ClassVar[int]
    MEMORY_FIELD_NUMBER: _ClassVar[int]
    MODULE_FIELD_NUMBER: _ClassVar[int]
    PENV_FIELD_NUMBER: _ClassVar[int]
    POD_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_DIR_FIELD_NUMBER: _ClassVar[int]
    QUEUE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_LABELS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    SCRATCH_FIELD_NUMBER: _ClassVar[int]
    SHELL_FIELD_NUMBER: _ClassVar[int]
    SPACK_FIELD_NUMBER: _ClassVar[int]
    STAGE_IN_MODE_FIELD_NUMBER: _ClassVar[int]
    STAGE_OUT_MODE_FIELD_NUMBER: _ClassVar[int]
    STORE_DIR_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FIELD_NUMBER: _ClassVar[int]
    line: int
    accelerator: AcceleratorDirective
    after_script: AfterScriptDirective
    arch: ArchDirective
    array: ArrayDirective
    before_script: BeforeScriptDirective
    cache: CacheDirective
    cluster_options: ClusterOptionsDirective
    conda: CondaDirective
    container: ContainerDirective
    container_options: ContainerOptionsDirective
    cpus: CpusDirective
    debug: DebugDirective
    disk: DiskDirective
    echo: EchoDirective
    error_strategy: ErrorStrategyDirective
    executor: ExecutorDirective
    ext: ExtDirective
    fair: FairDirective
    label: LabelDirective
    machine_type: MachineTypeDirective
    max_submit_await: MaxSubmitAwaitDirective
    max_errors: MaxErrorsDirective
    max_forks: MaxForksDirective
    max_retries: MaxRetriesDirective
    memory: MemoryDirective
    module: ModuleDirective
    penv: PenvDirective
    pod: PodDirective
    publish_dir: PublishDirDirective
    queue: QueueDirective
    resource_labels: ResourceLabelsDirective
    resource_limits: ResourceLimitsDirective
    scratch: ScratchDirective
    shell: ShellDirective
    spack: SpackDirective
    stage_in_mode: StageInModeDirective
    stage_out_mode: StageOutModeDirective
    store_dir: StoreDirDirective
    tag: TagDirective
    time: TimeDirective
    dynamic: DynamicDirective
    unknown: UnknownDirective
    def __init__(self, line: _Optional[int] = ..., accelerator: _Optional[_Union[AcceleratorDirective, _Mapping]] = ..., after_script: _Optional[_Union[AfterScriptDirective, _Mapping]] = ..., arch: _Optional[_Union[ArchDirective, _Mapping]] = ..., array: _Optional[_Union[ArrayDirective, _Mapping]] = ..., before_script: _Optional[_Union[BeforeScriptDirective, _Mapping]] = ..., cache: _Optional[_Union[CacheDirective, _Mapping]] = ..., cluster_options: _Optional[_Union[ClusterOptionsDirective, _Mapping]] = ..., conda: _Optional[_Union[CondaDirective, _Mapping]] = ..., container: _Optional[_Union[ContainerDirective, _Mapping]] = ..., container_options: _Optional[_Union[ContainerOptionsDirective, _Mapping]] = ..., cpus: _Optional[_Union[CpusDirective, _Mapping]] = ..., debug: _Optional[_Union[DebugDirective, _Mapping]] = ..., disk: _Optional[_Union[DiskDirective, _Mapping]] = ..., echo: _Optional[_Union[EchoDirective, _Mapping]] = ..., error_strategy: _Optional[_Union[ErrorStrategyDirective, _Mapping]] = ..., executor: _Optional[_Union[ExecutorDirective, _Mapping]] = ..., ext: _Optional[_Union[ExtDirective, _Mapping]] = ..., fair: _Optional[_Union[FairDirective, _Mapping]] = ..., label: _Optional[_Union[LabelDirective, _Mapping]] = ..., machine_type: _Optional[_Union[MachineTypeDirective, _Mapping]] = ..., max_submit_await: _Optional[_Union[MaxSubmitAwaitDirective, _Mapping]] = ..., max_errors: _Optional[_Union[MaxErrorsDirective, _Mapping]] = ..., max_forks: _Optional[_Union[MaxForksDirective, _Mapping]] = ..., max_retries: _Optional[_Union[MaxRetriesDirective, _Mapping]] = ..., memory: _Optional[_Union[MemoryDirective, _Mapping]] = ..., module: _Optional[_Union[ModuleDirective, _Mapping]] = ..., penv: _Optional[_Union[PenvDirective, _Mapping]] = ..., pod: _Optional[_Union[PodDirective, _Mapping]] = ..., publish_dir: _Optional[_Union[PublishDirDirective, _Mapping]] = ..., queue: _Optional[_Union[QueueDirective, _Mapping]] = ..., resource_labels: _Optional[_Union[ResourceLabelsDirective, _Mapping]] = ..., resource_limits: _Optional[_Union[ResourceLimitsDirective, _Mapping]] = ..., scratch: _Optional[_Union[ScratchDirective, _Mapping]] = ..., shell: _Optional[_Union[ShellDirective, _Mapping]] = ..., spack: _Optional[_Union[SpackDirective, _Mapping]] = ..., stage_in_mode: _Optional[_Union[StageInModeDirective, _Mapping]] = ..., stage_out_mode: _Optional[_Union[StageOutModeDirective, _Mapping]] = ..., store_dir: _Optional[_Union[StoreDirDirective, _Mapping]] = ..., tag: _Optional[_Union[TagDirective, _Mapping]] = ..., time: _Optional[_Union[TimeDirective, _Mapping]] = ..., dynamic: _Optional[_Union[DynamicDirective, _Mapping]] = ..., unknown: _Optional[_Union[UnknownDirective, _Mapping]] = ...) -> None: ...

class AcceleratorDirective(_message.Message):
    __slots__ = ("num_gpus", "gpu_type")
    NUM_GPUS_FIELD_NUMBER: _ClassVar[int]
    GPU_TYPE_FIELD_NUMBER: _ClassVar[int]
    num_gpus: int
    gpu_type: str
    def __init__(self, num_gpus: _Optional[int] = ..., gpu_type: _Optional[str] = ...) -> None: ...

class AfterScriptDirective(_message.Message):
    __slots__ = ("script",)
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    script: str
    def __init__(self, script: _Optional[str] = ...) -> None: ...

class ArchDirective(_message.Message):
    __slots__ = ("name", "target")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    name: str
    target: str
    def __init__(self, name: _Optional[str] = ..., target: _Optional[str] = ...) -> None: ...

class ArrayDirective(_message.Message):
    __slots__ = ("size",)
    SIZE_FIELD_NUMBER: _ClassVar[int]
    size: int
    def __init__(self, size: _Optional[int] = ...) -> None: ...

class BeforeScriptDirective(_message.Message):
    __slots__ = ("script",)
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    script: str
    def __init__(self, script: _Optional[str] = ...) -> None: ...

class CacheDirective(_message.Message):
    __slots__ = ("enabled", "deep", "lenient")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    DEEP_FIELD_NUMBER: _ClassVar[int]
    LENIENT_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    deep: bool
    lenient: bool
    def __init__(self, enabled: bool = ..., deep: bool = ..., lenient: bool = ...) -> None: ...

class ClusterOptionsDirective(_message.Message):
    __slots__ = ("options",)
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    options: str
    def __init__(self, options: _Optional[str] = ...) -> None: ...

class CondaDirective(_message.Message):
    __slots__ = ("possible_values",)
    POSSIBLE_VALUES_FIELD_NUMBER: _ClassVar[int]
    possible_values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, possible_values: _Optional[_Iterable[str]] = ...) -> None: ...

class ContainerDirective(_message.Message):
    __slots__ = ("format", "simple_name", "condition", "true_name", "false_name")
    class Format(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SIMPLE: _ClassVar[ContainerDirective.Format]
        TERNARY: _ClassVar[ContainerDirective.Format]
    SIMPLE: ContainerDirective.Format
    TERNARY: ContainerDirective.Format
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_NAME_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    TRUE_NAME_FIELD_NUMBER: _ClassVar[int]
    FALSE_NAME_FIELD_NUMBER: _ClassVar[int]
    format: ContainerDirective.Format
    simple_name: str
    condition: str
    true_name: str
    false_name: str
    def __init__(self, format: _Optional[_Union[ContainerDirective.Format, str]] = ..., simple_name: _Optional[str] = ..., condition: _Optional[str] = ..., true_name: _Optional[str] = ..., false_name: _Optional[str] = ...) -> None: ...

class ContainerOptionsDirective(_message.Message):
    __slots__ = ("options",)
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    options: str
    def __init__(self, options: _Optional[str] = ...) -> None: ...

class CpusDirective(_message.Message):
    __slots__ = ("num",)
    NUM_FIELD_NUMBER: _ClassVar[int]
    num: int
    def __init__(self, num: _Optional[int] = ...) -> None: ...

class DebugDirective(_message.Message):
    __slots__ = ("enabled",)
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    def __init__(self, enabled: bool = ...) -> None: ...

class DiskDirective(_message.Message):
    __slots__ = ("space",)
    SPACE_FIELD_NUMBER: _ClassVar[int]
    space: str
    def __init__(self, space: _Optional[str] = ...) -> None: ...

class EchoDirective(_message.Message):
    __slots__ = ("enabled",)
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    def __init__(self, enabled: bool = ...) -> None: ...

class ErrorStrategyDirective(_message.Message):
    __slots__ = ("strategy",)
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    strategy: str
    def __init__(self, strategy: _Optional[str] = ...) -> None: ...

class ExecutorDirective(_message.Message):
    __slots__ = ("executor",)
    EXECUTOR_FIELD_NUMBER: _ClassVar[int]
    executor: str
    def __init__(self, executor: _Optional[str] = ...) -> None: ...

class ExtDirective(_message.Message):
    __slots__ = ("version", "args")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    version: str
    args: str
    def __init__(self, version: _Optional[str] = ..., args: _Optional[str] = ...) -> None: ...

class FairDirective(_message.Message):
    __slots__ = ("enabled",)
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    def __init__(self, enabled: bool = ...) -> None: ...

class LabelDirective(_message.Message):
    __slots__ = ("label",)
    LABEL_FIELD_NUMBER: _ClassVar[int]
    label: str
    def __init__(self, label: _Optional[str] = ...) -> None: ...

class MachineTypeDirective(_message.Message):
    __slots__ = ("machine_type",)
    MACHINE_TYPE_FIELD_NUMBER: _ClassVar[int]
    machine_type: str
    def __init__(self, machine_type: _Optional[str] = ...) -> None: ...

class MaxSubmitAwaitDirective(_message.Message):
    __slots__ = ("max_submit_await",)
    MAX_SUBMIT_AWAIT_FIELD_NUMBER: _ClassVar[int]
    max_submit_await: str
    def __init__(self, max_submit_await: _Optional[str] = ...) -> None: ...

class MaxErrorsDirective(_message.Message):
    __slots__ = ("num",)
    NUM_FIELD_NUMBER: _ClassVar[int]
    num: int
    def __init__(self, num: _Optional[int] = ...) -> None: ...

class MaxForksDirective(_message.Message):
    __slots__ = ("num",)
    NUM_FIELD_NUMBER: _ClassVar[int]
    num: int
    def __init__(self, num: _Optional[int] = ...) -> None: ...

class MaxRetriesDirective(_message.Message):
    __slots__ = ("num",)
    NUM_FIELD_NUMBER: _ClassVar[int]
    num: int
    def __init__(self, num: _Optional[int] = ...) -> None: ...

class MemoryDirective(_message.Message):
    __slots__ = ("memory_gb",)
    MEMORY_GB_FIELD_NUMBER: _ClassVar[int]
    memory_gb: float
    def __init__(self, memory_gb: _Optional[float] = ...) -> None: ...

class ModuleDirective(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class PenvDirective(_message.Message):
    __slots__ = ("environment",)
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    environment: str
    def __init__(self, environment: _Optional[str] = ...) -> None: ...

class PodDirective(_message.Message):
    __slots__ = ("env", "value")
    ENV_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    env: str
    value: str
    def __init__(self, env: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class PublishDirDirective(_message.Message):
    __slots__ = ("path", "params", "content_type", "enabled", "fail_on_error", "mode", "overwrite")
    PATH_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    FAIL_ON_ERROR_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    path: str
    params: str
    content_type: bool
    enabled: bool
    fail_on_error: bool
    mode: str
    overwrite: bool
    def __init__(self, path: _Optional[str] = ..., params: _Optional[str] = ..., content_type: bool = ..., enabled: bool = ..., fail_on_error: bool = ..., mode: _Optional[str] = ..., overwrite: bool = ...) -> None: ...

class QueueDirective(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class ResourceLabelsDirective(_message.Message):
    __slots__ = ("keys",)
    KEYS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, keys: _Optional[_Iterable[str]] = ...) -> None: ...

class ResourceLimitsDirective(_message.Message):
    __slots__ = ("cpus", "disk", "memory", "time")
    CPUS_FIELD_NUMBER: _ClassVar[int]
    DISK_FIELD_NUMBER: _ClassVar[int]
    MEMORY_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    cpus: int
    disk: str
    memory: str
    time: str
    def __init__(self, cpus: _Optional[int] = ..., disk: _Optional[str] = ..., memory: _Optional[str] = ..., time: _Optional[str] = ...) -> None: ...

class ScratchDirective(_message.Message):
    __slots__ = ("enabled", "directory")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    directory: str
    def __init__(self, enabled: bool = ..., directory: _Optional[str] = ...) -> None: ...

class ShellDirective(_message.Message):
    __slots__ = ("command",)
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    command: str
    def __init__(self, command: _Optional[str] = ...) -> None: ...

class SpackDirective(_message.Message):
    __slots__ = ("dependencies",)
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    dependencies: str
    def __init__(self, dependencies: _Optional[str] = ...) -> None: ...

class StageInModeDirective(_message.Message):
    __slots__ = ("mode",)
    MODE_FIELD_NUMBER: _ClassVar[int]
    mode: str
    def __init__(self, mode: _Optional[str] = ...) -> None: ...

class StageOutModeDirective(_message.Message):
    __slots__ = ("mode",)
    MODE_FIELD_NUMBER: _ClassVar[int]
    mode: str
    def __init__(self, mode: _Optional[str] = ...) -> None: ...

class StoreDirDirective(_message.Message):
    __slots__ = ("directory",)
    DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    directory: str
    def __init__(self, directory: _Optional[str] = ...) -> None: ...

class TagDirective(_message.Message):
    __slots__ = ("tag",)
    TAG_FIELD_NUMBER: _ClassVar[int]
    tag: str
    def __init__(self, tag: _Optional[str] = ...) -> None: ...

class TimeDirective(_message.Message):
    __slots__ = ("duration",)
    DURATION_FIELD_NUMBER: _ClassVar[int]
    duration: str
    def __init__(self, duration: _Optional[str] = ...) -> None: ...

class DynamicDirective(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class UnknownDirective(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class ModuleResult(_message.Message):
    __slots__ = ("file_path", "module", "error")
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    MODULE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    file_path: str
    module: Module
    error: _common_pb2.ParseError
    def __init__(self, file_path: _Optional[str] = ..., module: _Optional[_Union[Module, _Mapping]] = ..., error: _Optional[_Union[_common_pb2.ParseError, _Mapping]] = ...) -> None: ...

class ModuleListResult(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ModuleResult]
    def __init__(self, results: _Optional[_Iterable[_Union[ModuleResult, _Mapping]]] = ...) -> None: ...

class Module(_message.Message):
    __slots__ = ("path", "dsl_version", "processes")
    PATH_FIELD_NUMBER: _ClassVar[int]
    DSL_VERSION_FIELD_NUMBER: _ClassVar[int]
    PROCESSES_FIELD_NUMBER: _ClassVar[int]
    path: str
    dsl_version: int
    processes: _containers.RepeatedCompositeFieldContainer[Process]
    def __init__(self, path: _Optional[str] = ..., dsl_version: _Optional[int] = ..., processes: _Optional[_Iterable[_Union[Process, _Mapping]]] = ...) -> None: ...

class Process(_message.Message):
    __slots__ = ("name", "line", "directives")
    NAME_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    DIRECTIVES_FIELD_NUMBER: _ClassVar[int]
    name: str
    line: int
    directives: _containers.RepeatedCompositeFieldContainer[Directive]
    def __init__(self, name: _Optional[str] = ..., line: _Optional[int] = ..., directives: _Optional[_Iterable[_Union[Directive, _Mapping]]] = ...) -> None: ...
