from typing import Sequence, Optional, List
from hidet.ir.type import TensorType, FuncType, VoidType
from hidet.ir.func import IRModule
from hidet.ir.task import Task


def func_type_from_task(task: Task) -> FuncType:
    """
    Get the function type for the given task.

    Each task will be lowered to an ir module with a packed function.
    The packed function will accept the packed format of parameters of the task.
    This function will return the function type of the un-packed parameters expected by the packed function.

    For example, if a task has inputs: f32[16, 16], f32[16, 8] and output f32[3, 4]
    Then this function would return a FuncType with param_types: [f32[16, 16], f32[16, 8], f32[3, 4]] and ret_type: None

    Parameters
    ----------
    task: Task
        The task to get the function type.

    Returns
    -------
    ret: FuncType
        The function type for the given task.
    """
    from hidet.ir.type import TensorType

    param_types: List[TensorType] = [tensor.data_type for tensor in task.parameters]
    return FuncType(param_types=param_types, ret_type=VoidType())


def validate_schedule(task: Task, device: str, dummy_inputs: Optional[Sequence] = None, rtol: float = 1e-5, atol: float = 1e-5) -> bool:
    """
    Validate the correctness of schedule in the given task.

    Parameters
    ----------
    task: Task
        The task to validate.

    device: str
        The target device.

    dummy_inputs: Optional[Sequence[hidet.graph.tensor.Tensor]]
        The dummy inputs to use for validation.
        If None is given, we will generate random inputs for validation.

    rtol: float
        The relative tolerance for validation.

    atol: float
        The absolute tolerance for validation.

    Returns
    -------
    ret: bool
        Whether the schedule for given device is valid.
    """
    from numpy import allclose
    from hidet.driver import build_ir_module
    from hidet.graph.ops.schedules.cuda.auto_scheduler import CudaAutoScheduler
    from hidet.graph.ops.schedules.cpu.auto_scheduler import CpuAutoScheduler
    from hidet.runtime import CompiledFunction
    from hidet.graph.tensor import Tensor, randn, zeros, empty, empty_like

    if dummy_inputs is None:
        dummy_inputs = []
        for input_tensor in task.task_graph.input_tensors:
            tensor_type: TensorType = input_tensor.data_type
            if tensor_type.scalar_type.is_float():
                dummy_inputs.append(randn(tensor_type.const_shape(), tensor_type.scalar_type.name, device=device))
            else:
                dummy_inputs.append(zeros(tensor_type.const_shape(), tensor_type.scalar_type.name, device=device))
    else:
        dummy_inputs = list(dummy_inputs)

    actual_outputs: List[Tensor] = [empty(output.data_type.const_shape(), output.data_type.scalar_type.name, device)
                                    for output in task.task_graph.output_tensors]
    desire_outputs: List[Tensor] = [empty_like(output) for output in actual_outputs]

    if len(dummy_inputs) != len(task.task_graph.input_tensors):
        raise ValueError("The number of dummy inputs does not match the number of task inputs.")
    device2scheduler = {
        "cuda": CudaAutoScheduler,
        "cpu": CpuAutoScheduler
    }

    ir_module_actual: IRModule = task.implement(device)
    ir_module_desire: IRModule = device2scheduler[device]().schedule_task(task, device)

    func_type: FuncType = func_type_from_task(task)
    func_actual: CompiledFunction = build_ir_module(ir_module_actual, func_name=task.name, func_type=func_type)
    func_desire: CompiledFunction = build_ir_module(ir_module_desire, func_name=task.name, func_type=func_type)

    func_actual(*dummy_inputs, *actual_outputs)
    func_desire(*dummy_inputs, *desire_outputs)

    for actual, desire in zip(actual_outputs, desire_outputs):
        if not allclose(actual.numpy(), desire.numpy(), rtol=rtol, atol=atol):
            return False
    return True