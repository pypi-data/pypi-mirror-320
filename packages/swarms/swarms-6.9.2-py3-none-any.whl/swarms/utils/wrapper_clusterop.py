from typing import Any, Callable
from clusterops import (
    execute_on_gpu,
    execute_on_multiple_gpus,
    list_available_gpus,
    execute_with_all_cpu_cores,
    execute_on_cpu,
)
from swarms.utils.loguru_logger import initialize_logger

logger = initialize_logger(log_folder="clusterops_wrapper")


def exec_callable_with_clusterops(
    device: str = "cpu",
    device_id: int = 0,
    all_cores: bool = True,
    all_gpus: bool = False,
    func: Callable = None,
    enable_logging: bool = True,
    *args,
    **kwargs,
) -> Any:
    """
    Executes a given function on a specified device, either CPU or GPU.

    Args:
        device (str, optional): The device to use for execution. Defaults to "cpu".
        device_id (int, optional): The ID of the GPU or CPU core to use. Defaults to 0.
        all_cores (bool, optional): If True, use all available CPU cores. Defaults to True.
        all_gpus (bool, optional): If True, use all available GPUs. Defaults to False.
        func (Callable): The function to execute.
        enable_logging (bool, optional): If True, enables logging. Defaults to True.
        *args: Additional positional arguments for the function.
        **kwargs: Additional keyword arguments for the function.

    Returns:
        Any: The result of the execution.

    Raises:
        ValueError: If `func` is None or an invalid device is specified.
        RuntimeError: If `device_id` is invalid or an error occurs during execution.
    """
    if func is None:
        raise ValueError("A callable function must be provided.")

    device = device.lower()
    if enable_logging:
        logger.info(f"Execution requested on device: {device}")

    try:
        if device == "cpu":
            if enable_logging:
                logger.info(f"CPU configuration - all_cores: {all_cores}, device_id: {device_id}")
            if all_cores:
                return execute_with_all_cpu_cores(func, *args, **kwargs)
            else:
                return execute_on_cpu(device_id, func, *args, **kwargs)

        elif device == "gpu":
            available_gpus = list_available_gpus()
            if enable_logging:
                logger.info(f"Available GPUs: {available_gpus}")
            if all_gpus:
                return execute_on_multiple_gpus(available_gpus, func, *args, **kwargs)
            else:
                return execute_on_gpu(device_id, func, *args, **kwargs)
                
            if device_id not in available_gpus:
                raise RuntimeError(f"Invalid GPU ID: {device_id}. Available GPUs: {available_gpus}")
            

        else:
            raise ValueError(f"Invalid device specified: {device}. Supported devices are 'cpu' and 'gpu'.")

    except ValueError as ve:
        if enable_logging:
            logger.error(f"Configuration error: {ve}")
        raise
    except RuntimeError as re:
        if enable_logging:
            logger.error(f"Runtime error: {re}")
        raise
    except Exception as e:
        if enable_logging:
            logger.error(f"An unexpected error occurred: {e}")
        raise
