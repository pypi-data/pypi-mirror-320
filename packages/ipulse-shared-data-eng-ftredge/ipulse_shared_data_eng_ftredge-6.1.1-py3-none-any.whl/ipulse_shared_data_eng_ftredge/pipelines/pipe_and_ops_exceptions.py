from typing import Any, Dict, Optional, Union
import logging
import inspect
import json
from ipulse_shared_base_ftredge import (StructLog,
                                        LogLevel,
                                        log_warning,
                                        ProgressStatus,
                                        Resource,
                                        Action,
                                        Alert,
                                        Unit,
                                        format_exception,
                                        stringify_multiline_msg)

from .pipelineflow import  PipelineTask
from .function_result import FunctionResult


class PipelineEarlyTerminationError(Exception):
    """
    Exception raised for controlled pipeline termination.
    
    Attributes:
        reason: Detailed explanation of termination
        task_name: Name of task that triggered termination
        status_code: Optional status code for different termination types
        log_level: LogLevel for this termination
    """
    def __init__(
        self,
        reason: str,
        task: PipelineTask,
        context:str = "unknown",
        already_logged: bool = False
    ):
        self.reason = reason
        self.task_name = task.name
        task.status=ProgressStatus.FAILED
        self.already_logged = already_logged
        super().__init__(f"Exception in context {context}, task '{task.name}': {reason} . - Pipeline Early Termination")


class PipelineSequenceTerminationError(Exception):
    """
    Exception raised for controlled pipeline iteration termination.
    
    Attributes:
        reason: Detailed explanation of termination
        task_name: Name of task that triggered termination
        status_code: Optional status code for different termination types
        log_level: LogLevel for this termination
    """
    def __init__(
        self,
        reason: str,
        task: PipelineTask,
        context:str = "_unknown_",
        already_logged: bool = False
    ):
        self.reason = reason
        self.task_name = task.name
        task.status=ProgressStatus.FAILED
        self.already_logged = already_logged
        
        super().__init__(f"Exception in context {context} , task '{task.name}': {reason} . - Pipeline Iteration Termination")


def handle_pipeline_step_exception(
    e: Exception,
    context:Optional[str]=None,
    pipelinemon = None,
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    raise_e: bool = False
) -> None:
    """Centralized error handler for pipeline steps"""
    
    caller_frame = inspect.currentframe().f_back
    func_name = caller_frame.f_code.co_name if caller_frame else "unknown_step"
    
    error_details = format_exception(e, func_name)
    error_str = stringify_multiline_msg(error_details)
    log_warning(
        msg=f"EXCEPTION in {context}: {error_str}" if context else f"EXCEPTION in {func_name}: {error_str}",
        logger=logger,
        print_out=print_out
    )
    if pipelinemon:
        pipelinemon.add_log(StructLog(
            level=LogLevel.ERROR,
            e=e,
            description=error_str
        ))

    if raise_e:
        raise e from e


def handle_pipeline_operation_exception(
    e: Exception,
    result: Union[Dict[str, Any], FunctionResult],
    action: Optional[Union[Action,str]] = None,
    resource: Optional[Union[Resource,str]] = None,
    alert: Optional[Alert] = None,
    q: Optional[Union[int, float]] = None,
    q_unit: Optional[Unit] = None,
    pipelinemon = None,
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    raise_e: bool = False
) -> None:
    """Centralized error handler for operations"""
    
    caller_frame = inspect.currentframe().f_back
    operation_name = caller_frame.f_code.co_name if caller_frame else "unknown_operation"
    error_details = format_exception(e, operation_name)
    result_status_info=""
    # Handle both Dict and OpResult
    if isinstance(result, FunctionResult):
        result.add_state("EXCEPTION")
        result.add_issue(json.dumps(error_details, indent=2, default=str))
        result.final(status=ProgressStatus.FAILED)
        result_status_info = result.get_status_info
    elif isinstance(result, dict):
        # Legacy dict handling
        result["status"]["execution_state"] += ">>EXCEPTION "
        result["status"]["overall_status"] = ProgressStatus.FAILED
        result["status"]["issues"] += f'>> {json.dumps(error_details, indent=2, default=str)}'
        result_status_info = stringify_multiline_msg(result['status'])

    log_warning(
        msg=f"EXCEPTION: {result_status_info}",
        logger=logger,
        print_out=print_out
    )

    if pipelinemon:
        pipelinemon.add_log(StructLog(
            level=LogLevel.ERROR,
            progress_status=ProgressStatus.FAILED,
            action=action,
            resource=resource,
            alert=alert,
            q=q,
            q_unit=q_unit,
            e=e,
            description=result_status_info
        ))
    if raise_e:
        raise e from e