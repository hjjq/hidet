import os
import time
from typing import List, Optional
import numpy as np

from hidet.ir.type import TensorType
from hidet.ir.expr import Constant
from hidet.ir.func import IRModule
from hidet.ir.task import Task
from hidet.utils import TableBuilder, strict_zip, error_tolerance
from hidet.graph.tensor import randn, zeros, ones, Tensor, array
from hidet.backend import BuildInstance, batch_build_ir_modules
from hidet.runtime import CompiledFunction
from .common import Schedule


def dummy_inputs_from_task(task: Task) -> List[Tensor]:
    """
    Create dummy inputs values for given task.

    Parameters
    ----------
    task: Task
        The task to generate dummy inputs for.

    Returns
    -------
    ret: List[Tensor]
        The dummy input tensors.
    """
    inputs = []
    for idx, param in enumerate(task.parameters):
        param_type = param.data_type

        if not isinstance(param_type, TensorType):
            raise ValueError('Currently, only support create dummy scalar inputs.')
        if any(not isinstance(s, Constant) for s in param_type.shape):
            raise ValueError('Currently, only support create dummy values for static tensor inputs.')
        dtype = param_type.scalar_type.name
        scope = param_type.scope.name
        shape = [int(s) for s in param_type.shape]
        scope2device = {
            'global': 'cuda',
            'host': 'cpu'
        }
        device = scope2device[scope]
        if dtype in ['float32', 'float16', 'bfloat16']:
            x = randn(shape, dtype, device=device, layout=param_type.layout)
        elif dtype in ['int64', 'int32', 'int8', 'uint64', 'uint32', 'uint8']:
            x = zeros(shape, dtype, device=device, layout=param_type.layout)
        elif dtype == 'bool':
            x = ones(shape, dtype, device=device, layout=param_type.layout)
        else:
            raise ValueError('Currently do not support generate random array for data type {}'.format(dtype))
        inputs.append(x)
    return inputs


def resolve_ir_modules(ir_modules: List[IRModule], schedules: List[Schedule], output_dir: str, parallel: bool = True, verbose: bool = True, validate: bool = False) -> IRModule:
    """
    Resolve the ir modules of the same task by comparing the latency of each kernel.

    Parameters
    ----------
    ir_modules: List[IRModule]
        The ir modules to resolve.
    schedules: List[Schedule]
        The schedules corresponding to each ir module. The order of schedules must be consistent with ir modules'.
    output_dir: str
        The output directory to store the summary and lowered source code of each ir module.
    parallel: bool
        Whether to parallelize the building. Default True.
    verbose: bool
        Whether to show the progress of parallel building.
    validate: bool
        Whether to mutual validate the correctness of different schedules. To perform the mutual validation, we will
        run all successful built ir modules with the same dummy inputs, compare their outputs, and make sure their outputs
        are within error threshold. Default: False.
    Returns
    -------
    ret: IRModule
        The best ir module we can find.
    """
    if len(ir_modules) == 0:
        raise ValueError('Require at least one ir module.')
    if len(ir_modules) == 1:
        return ir_modules[0]
    if len(schedules) != len(ir_modules):
        raise ValueError('The number of ir modules and schedules does not match.')
    if any(ir_module.task != ir_modules[0].task for ir_module in ir_modules):
        raise ValueError('Require all ir modules are from the same task.')

    # build ir modules
    build_instances = [BuildInstance(ir_module=ir_module,
                                     output_dir=os.path.join(output_dir, 'resolve', str(idx)),
                                     keep_ir=False,
                                     nvcc_keep=False,
                                     verbose=False) for idx, ir_module in enumerate(ir_modules)]
    compiled_funcs: List[Optional[CompiledFunction]] = batch_build_ir_modules(build_instances, parallel=parallel, verbose=verbose)
    dummy_inputs = dummy_inputs_from_task(ir_modules[0].task)
    best_latency = 1e30
    best_ir_module = None
    latencies = []
    time.sleep(1.0)

    if all(f is None for f in compiled_funcs):
        raise ValueError('All ir modules are failed in building.')

    # mutual validate
    errors: List[float] = []
    if validate:
        task = ir_modules[0].task
        num_inputs, num_outputs = len(task.inputs), len(task.outputs)
        inputs, outputs = dummy_inputs[:num_inputs], dummy_inputs[num_inputs:]
        example_outputs: Optional[List[Tensor]] = None
        for func in compiled_funcs:
            if not func:
                errors.append(float('NaN'))
            else:
                func(*inputs, *outputs)
                if example_outputs is None:
                    example_outputs = [v.copy() for v in outputs]
                    errors.append(0.0)
                else:
                    errors.append(max(error_tolerance(a, b) for a, b in zip(outputs, example_outputs)))
    else:
        errors = [float('NaN')] * len(compiled_funcs)

    # measure latency
    for ir_module, compiled_func in strict_zip(ir_modules, compiled_funcs):
        if compiled_func:
            repeat_latency = compiled_func.profile(*dummy_inputs, warmup=5, number=10, repeat=3)
            latency = float(np.median(repeat_latency))
        else:
            # this ir module failed in building, skip
            latency = 1e30
        latencies.append(latency)
        if best_latency > latency:
            best_latency = latency
            best_ir_module = ir_module

    # generate summary
    with TableBuilder(headers=['idx'] + [v[0] for v in (schedules[0].keys() + schedules[0].derived_keys())] + ['Error', 'latency']) as tb:
        rows = []
        for idx, (schedule, error, latency) in enumerate(zip(schedules, errors, latencies)):
            row = [idx] + [v[1] for v in schedule.keys() + schedule.derived_keys()] + [error, latency]
            rows.append(row)
        # sort by latency, low to high
        rows = sorted(rows, key=lambda v: v[-1])
        for row in rows:
            tb += row
    with open(os.path.join(output_dir, 'summary.txt'), 'w') as f:
        f.write(str(tb))

    return best_ir_module