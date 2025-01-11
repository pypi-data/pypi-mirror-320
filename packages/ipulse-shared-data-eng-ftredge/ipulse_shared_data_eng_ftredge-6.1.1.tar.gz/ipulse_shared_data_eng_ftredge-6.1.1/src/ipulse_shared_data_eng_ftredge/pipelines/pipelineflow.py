""" Shared pipeline configuration utility. """
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Union,Any,Tuple
import copy
from collections import defaultdict
from datetime import datetime

from ipulse_shared_base_ftredge import (Action, DataResource, DatasetScope, ProgressStatus, calculate_progress_statuses_breakdown,)
from .function_result import FunctionResult




def calculate_overall_status(status_counts: Dict[str, int],
                             current_status: Optional[ProgressStatus] = None,
                             final: bool = False) -> ProgressStatus:
    """
    Calculate the overall status based on status counts and conditions.
    
    Args:
        status_counts: Dictionary containing status counts by category and detail
        current_status: Current status to consider (if not in pending state)
        final: Whether this is a final status calculation
        
    Returns:
        ProgressStatus: Calculated overall status
    """
    # Early return if current status is final
    if current_status and current_status in ProgressStatus.closed_or_skipped_statuses():
        return current_status

    failed_count=status_counts["detailed"].get('FAILED',0)
    done_with_warnings_count = status_counts["detailed"].get('DONE_WITH_WARNINGS', 0)
    done_with_notices_count = status_counts["detailed"].get('DONE_WITH_NOTICES', 0)
    # Get category counts
    pending_statuses_count = status_counts["by_category"].get('pending_statuses', 0)
    issue_statuses_count = status_counts["by_category"].get('issue_statuses', 0)
    skipped_statuses_count = status_counts["by_category"].get('skipped_statuses', 0)
    
    not_started_statuses_count = status_counts["by_category"].get('not_started_or_skipped_statuses', 0)
    total_statuses_count = status_counts['total_statuses']
    


    # For final status calculation
    if final:
        # Check for pending tasks first
        if pending_statuses_count > 0:
            return ProgressStatus.FAILED if issue_statuses_count > 0 else ProgressStatus.UNFINISHED

        # Check for issues when no pending tasks
        if issue_statuses_count > 0:
            failed_or_skipped = failed_count+skipped_statuses_count
            return ProgressStatus.FAILED if failed_or_skipped == total_statuses_count else ProgressStatus.FINISHED_WITH_ISSUES

        # Check for warnings and notices
        if done_with_warnings_count> 0:
            return ProgressStatus.DONE_WITH_WARNINGS
        if done_with_notices_count > 0:
            return ProgressStatus.DONE_WITH_NOTICES
            
        return ProgressStatus.DONE

    # For non-final status calculation
    if pending_statuses_count == 0:
        return calculate_overall_status(status_counts=status_counts, current_status=current_status, final=True)
    
    if not_started_statuses_count == total_statuses_count:
        return ProgressStatus.NOT_STARTED
    
    return ProgressStatus.IN_PROGRESS
class DependencyType:
    """Requirements for dependency resolution"""
    TO_CLOSED = "to_closed"  # Must be in closed statuses
    TO_SUCCESS = "to_success"  # Must be in success statuses
    TO_SUCCESS_OR_SKIPPED = "to_success_or_skipped"  # Must be in success or skipped statuses
    TO_AT_LEAST_STARTED = "to_at_least_started"  # Must be at least started (not in NOT_STARTED)
    TO_CLOSED = "to_closed"  # Must be finished (not in pending statuses)

    @staticmethod
    def validate_status(status: ProgressStatus, requirement: str) -> bool:
        """Check if status meets requirement"""
        if requirement == DependencyType.TO_CLOSED:
            return status in ProgressStatus.closed_statuses()
        elif requirement == DependencyType.TO_SUCCESS:
            return status in ProgressStatus.success_statuses()
        elif requirement == DependencyType.TO_SUCCESS_OR_SKIPPED:
            return status in ProgressStatus.success_statuses() or status in ProgressStatus.skipped_statuses()
        elif requirement == DependencyType.TO_AT_LEAST_STARTED:
            return status not in {ProgressStatus.NOT_STARTED, ProgressStatus.BLOCKED_BY_UNRESOLVED_DEPENDENCY}
        elif requirement == DependencyType.TO_CLOSED:
            return status in ProgressStatus.closed_statuses()
        return False

class Dependency:
    """Represents a dependency between pipeline steps"""
    
    def __init__(self,
                 step_name: str,
                 requirement: str = DependencyType.TO_SUCCESS_OR_SKIPPED,
                 optional: bool = False,
                 timeout_s: Optional[int] = None):
        self.step_name = step_name
        self.requirement = requirement
        self.optional = optional
        self.timeout_s = timeout_s
        self._start_time = None
        
    def start_timeout(self):
        """Start timeout tracking"""
        if self.timeout_s:
            self._start_time = datetime.now()
            
    def is_timeout(self) -> bool:
        """Check if dependency has timed out"""
        if not self.timeout_s or not self._start_time:
            return False
        elapsed = (datetime.now() - self._start_time).total_seconds()
        return elapsed > self.timeout_s

    def check_satisfied(self, step: 'Step') -> bool:
        """Check if dependency is satisfied by step's status"""
        # if self.is_timeout():
        #     return False
            
        return DependencyType.validate_status(step.status, self.requirement)

    def __str__(self):
        return f"Dependency({self.step_name}, req={self.requirement}, optional={self.optional})"


class Step:
    """Base class for all pipeline steps"""
    
    def __init__(self, name: str, disabled: bool = False, dependencies: Optional[List[Union[str, Dependency]]] = None):
        self.id = uuid.uuid4()
        self.name = name
        self.disabled = disabled
        self.dependencies = self._normalize_dependencies(dependencies or [])
        self._status = ProgressStatus.DISABLED if disabled else ProgressStatus.NOT_STARTED
        self.pipeline_flow = None
        
        # Operation tracking
        self._issues: List[Any] = []
        self._warnings: List[Any] = []
        self._notices: List[Any] = []
        self._execution_state: List[str] = []
        self._results_aggregated: int = 1
        self._start_time: Optional[datetime] = None
        self._duration_s: float = 0.0

    @property
    def duration_s(self) -> float:
        """Get execution duration in seconds"""
        if not self._start_time:
            return 0.0
        if self.is_closed_or_skipped:
            return self._duration_s
        return (datetime.now(timezone.utc) - self._start_time).total_seconds()

    def calculate_duration(self) -> None:
        """Calculate and store final duration"""
        if self._start_time:
            self._duration_s = (datetime.now(timezone.utc) - self._start_time).total_seconds()

    def add_state(self, state: str) -> None:
        """Add execution state with a timestamp"""
        timestamp = datetime.now(timezone.utc).isoformat()
        self._execution_state.append(f"[t:{timestamp}]--{state}")

    @property
    def issues(self) -> List[Any]:
        """Get issues"""
        return self._issues

    @property
    def issues_str(self) -> Optional[str]:
        """Get issues as a string"""
        if not self._issues:
            return None
        return "\n".join(f">>[i:{issue}]" for issue in self._issues)

    def add_issue(self, issue: Any, update_state:bool=True) -> None:
        """Add issue"""
        if issue:
            self._issues.append(issue)
            if update_state:
                self.add_state(f"Issue: {issue}")

    @property
    def warnings(self) -> List[Any]:
        """Get warnings"""
        return self._warnings

    @property
    def warnings_str(self) -> Optional[str]:
        """Get warnings as a string"""
        if not self._warnings:
            return None
        return "\n".join(f">>[w:{warning}]" for warning in self._warnings)

    def add_warning(self, warning: Any,update_state:bool=True) -> None:
        """Add warning"""
        if warning:
            self._warnings.append(warning)
            if update_state:
                self.add_state(f"Warning: {warning}")

    @property
    def notices(self) -> List[Any]:
        """Get notices"""
        return self._notices

    @property
    def notices_str(self) -> Optional[str]:
        """Get notices as a string"""
        if not self._notices:
            return None
        return "\n".join(f">>[n:{notice}]" for notice in self._notices)

    def add_notice(self, notice: Any,update_state:bool=True ) -> None:
        """Add notice"""
        if notice:
            self._notices.append(notice)
            if update_state:
                self.add_state(f"Notice: {notice}")

    def get_notes(self, exclude_none: bool = True) -> str:
        """Get all notes"""
        notes = {
            "ISSUES": self.issues_str,
            "WARNINGS": self.warnings_str,
            "NOTICES": self.notices_str
        }
        if exclude_none:
            notes = {k: v for k, v in notes.items() if v is not None}
        
        if not notes:
            return ""
            
        return "\n".join(f">>{k}: {v}" for k, v in notes.items())
    
    @property
    def status(self) -> ProgressStatus:
        return self._status
        
    @status.setter 
    def status(self, s: ProgressStatus):
        self._status = s

    @property
    def is_success(self) -> bool:
        return self.status in ProgressStatus.success_statuses()
    
    @property
    def is_success_or_skipped(self) -> bool:
        return self.status in ProgressStatus.success_statuses() or self.status in ProgressStatus.skipped_statuses()
    
    @property
    def is_closed_or_skipped(self) -> bool:
        return self.status in ProgressStatus.closed_statuses() or self.status in ProgressStatus.skipped_statuses()
    
    @property
    def has_issues(self) -> bool:
        return self.status in ProgressStatus.issue_statuses()
    
    @property
    def is_pending(self) -> bool:
        return self.status in ProgressStatus.pending_statuses()

    def set_pipeline_flow(self, pipeline_flow: 'PipelineFlow'):
        self.pipeline_flow = pipeline_flow

    @property
    def execution_state(self) -> List[str]:
        """Get execution state"""
        return self._execution_state

    @property
    def execution_state_str(self) -> Optional[str]:
        """Get execution state as a formatted string"""
        if not self._execution_state:
            return None
        return "\n".join(f">>[[{entry}]]" for entry in self._execution_state)

    # ------------------
    # Aggregation
    # ------------------
    @property
    def results_aggregated(self) -> int:
        """Get total functions"""
        return self._results_aggregated

    @results_aggregated.setter
    def results_aggregated(self, value: int) -> None:
        """Set total functions"""
        self._results_aggregated = value

    def increment_results_aggregated(self, value: int) -> None:
        """Increment total functions"""
        self._results_aggregated += value

    def incorporate_function_result(self, result: 'FunctionResult') -> None:
        """Incorporate function result issues/warnings/notices"""
        self._issues.extend(result.issues)
        self._warnings.extend(result.warnings)
        self._notices.extend(result.notices)
        self._execution_state.extend(result.execution_state)
        self.increment_results_aggregated(result.results_aggregated)

    # ------------------
    # Dependencies
    # ------------------

    def _normalize_dependencies(self, deps: List[Union[str, Dependency]]) -> List[Dependency]:
        """Convert string dependencies to Dependency objects"""
        normalized = []
        for dep in deps:
            if isinstance(dep, str):
                normalized.append(Dependency(dep))
            elif isinstance(dep, Dependency):
                normalized.append(dep)
            else:
                raise ValueError(f"Invalid dependency type: {type(dep)}")
        return normalized

    def validate_dependencies(self, sequence_ref: Optional[Union[int, str]] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate all dependencies are satisfied.
        Returns (is_satisfied, reason_if_not)
        """
        if not self.dependencies:
            return True, None

        if not self.pipeline_flow:
            # If pipeline_flow isn't set, skip or raise an error
            return True, None
            
        unsatisfied = []
        for dep in self.dependencies:
            if isinstance(dep, str):
                    dep = Dependency(dep)
            if not dep.optional:
                try:
                    dep_step = self.pipeline_flow.get_step(dep.step_name, sequence_ref)
                    if not dep.check_satisfied(dep_step):
                        unsatisfied.append(f"{str(dep)} : {dep_step.status}")
                except KeyError:
                    unsatisfied.append(f"Missing dependency: {dep.step_name}")
                    
        if unsatisfied:
            return False, f"Unsatisfied dependencies: {', '.join(unsatisfied)}"
            
        return True, None

    def validate_and_start(self, set_status: Optional[ProgressStatus]=ProgressStatus.IN_PROGRESS,
                      sequence_ref: Optional[Union[int, str]]=None) -> Tuple[bool, Optional[str]]:
        """Validate and start step execution"""
        # Prevent restarting completed steps
        if self.is_closed_or_skipped:
            return False, f"Step already completed with status {self.status}"
            
        if self.disabled:
            self.status = ProgressStatus.DISABLED
            return False, "Step is disabled"
            
        if self.status in ProgressStatus.skipped_statuses():
            self.status = ProgressStatus.INTENTIONALLY_SKIPPED
            return False, "Step is skipped"

        deps_ok, reason = self.validate_dependencies(sequence_ref)
        if not deps_ok:
            self.status = ProgressStatus.BLOCKED_BY_UNRESOLVED_DEPENDENCY
            self._issues.append(reason)
            return False, reason

        # Start execution tracking
        self._start_time = datetime.now(timezone.utc)
        self.add_state("STARTED")
        self.status = set_status
        return True, None

    

    def nb_tasks(self) -> int:
        """Get number of tasks - must be implemented by subclasses"""
        raise NotImplementedError


    def finalize(self) -> None:
        """
        Calculate final status based on results and issues.
        Only relevant for Tasks - Sequences and Iterators override this.
        """
        if self.is_closed_or_skipped:
            return

        self.add_state("FINALIZING")
        self.calculate_duration()
        
        if self.issues:
            self.status = ProgressStatus.FINISHED_WITH_ISSUES
        elif self.warnings:
            self.status = ProgressStatus.DONE_WITH_WARNINGS
        elif self.notices:
            self.status = ProgressStatus.DONE_WITH_NOTICES
        else:
            self.status = ProgressStatus.DONE

        self.add_state(f"FINALIZED: {self.status.name} in {self.duration_s:.2f}s")

def extract_statuses(steps: Union[List[Step], Dict[str,Step]]) -> List[ProgressStatus]:
    """Extract statuses from a list of steps."""
    if isinstance(steps, dict):
        steps = list(steps.values())
    return [step.status for step in steps]


class PipelineTask(Step):
    """
    Represents a single task in a pipeline.
    """
    def __init__(
        self,
        n: str,
        a: Optional[Action] = None,
        s: Optional[DataResource] = None,
        d: Optional[DataResource] = None,
        scope: Optional[DatasetScope] = None,
        dependencies: Optional[List[Union[str, Dependency]]] = None,
        disabled: bool = False,
        config: Optional[Dict] = None,
    ):
        """
        Initialize a PipelineTask.
        :param n: Name of the task.
        :param s: Source of data for the task.
        :param a: Action to perform.
        :param d: Destination for the task output.
        :param scope: Scope of the dataset being processed.
        :param dependencies: List of task names that this task depends on.
        :param config: Task-specific configuration.
        :param enabled: Whether the task is enabled.
        """
        super().__init__(name=n, disabled=disabled, dependencies=dependencies)
        self.action = a
        self.source = s
        self.destination = d
        self.data_scope = scope
        self.config = config or {}
        self._last_result: Optional[FunctionResult] = None

    def nb_tasks(self) -> int:
        return 1
    

    def __str__(self):
        if self.is_success:
            status_symbol = "✔"
        elif self.status in ProgressStatus.issue_statuses():
            status_symbol = "✖"
        elif self.status in ProgressStatus.pending_statuses():
            status_symbol = "..."
        elif self.status in ProgressStatus.skipped_statuses():
            status_symbol = "//"
        else:
            status_symbol = "?"

        parts = [f">> {self.name}"]
        if self.action:
            parts.append(str(self.action))
        if self.source:
            parts.append(f"from {str(self.source)}")
        if self.destination:
            parts.append(f"to {str(self.destination)}")
        if self.data_scope:
            parts.append(f"scope={str(self.data_scope)}")
        
        parts.append(f"[Status: {status_symbol} {self.status.name}] ")
        return f"{' :: '.join(parts)}"

    def incorporate_function_result(self, result: FunctionResult) -> None:
        """Incorporate function result and update status"""
        super().incorporate_function_result(result)
        self._last_result = result
        
        # Update status based on result if not already finalized
        if not self.is_closed_or_skipped:
            self.status = result.overall_status


class PipelineSequenceTemplate:
    """
    Represents a single iteration of a dynamic iteration group.
    """
    def __init__(self,
                 steps: List[Union['PipelineTask', 'PipelineDynamicIterator']]):
        # self.iteration_ref = iteration_ref
        self.steps: Dict[str, Union['PipelineTask', 'PipelineDynamicIterator']] = {step.name: step for step in steps}

    def clone_steps(self) -> Dict[str, Union['PipelineTask', 'PipelineDynamicIterator']]:
        """Create a deep copy of the steps for a new iteration."""
        
        return {name: copy.deepcopy(step) for name, step in self.steps.items()}
    
    @property
    def nb_tasks(self) -> int:
        return sum(
            step.nb_tasks() if hasattr(step, 'nb_tasks') else 1
            for step in self.steps.values() if step.disabled
        )
    
    def set_pipeline_flow(self, pipeline_flow: 'PipelineFlow'):
        """Associate the iteration's tasks with the pipeline flow."""
        for step in self.steps.values():
            step.set_pipeline_flow(pipeline_flow)

    def __str__(self):
        # iteration_status = f"[Iteration {self.iteration_ref} :: Status: {self.status.value}]"
        steps_str = "\n".join(f"    {str(step)}" for step in self.steps.values())
        # return f"{iteration_status}\n{steps_str}"
        return steps_str
    

class PipelineSequence(Step):
    """Represents a sequence of steps that can be initialized from a template or direct steps"""

    def __init__(self,
                 sequence_ref: Union[int, str],
                 sequence_template: Optional[PipelineSequenceTemplate] = None,
                 steps: Optional[List[Union[PipelineTask, 'PipelineDynamicIterator']]] = None,
                 dependencies: Optional[List[Union[str, Dependency]]] = None):
        """
        Initialize sequence either from template or direct steps.
        
        Args:
            sequence_ref: Unique reference for this sequence
            sequence_template: Optional template to clone steps from
            steps: Optional list of steps to use directly
            dependencies: Optional sequence dependencies
        """
        super().__init__(name=f"sequence_{sequence_ref}", dependencies=dependencies)
        self.sequence_ref = sequence_ref
        self.status_counts = None

        # Initialize steps either from template or direct list
        if sequence_template is not None:
            self.steps = sequence_template.clone_steps()
        elif steps is not None:
            self.steps = {step.name: step for step in steps}
        else:
            self.steps = {}  # Empty initially

    def add_step(self, step: Union[PipelineTask, 'PipelineDynamicIterator']) -> None:
        """Add a step to the sequence"""
        if step.name in self.steps:
            raise ValueError(f"Step {step.name} already exists in sequence {self.sequence_ref}")
        self.steps[step.name] = step
        if self.pipeline_flow:
            step.set_pipeline_flow(self.pipeline_flow)

    def add_steps(self, steps: List[Union[PipelineTask, 'PipelineDynamicIterator']]) -> None:
        """Add multiple steps to the sequence"""
        for step in steps:
            self.add_step(step)

    def update_status_counts_and_overall_status(self, final:bool):
        """
        Update the current status of the sequence based on task statuses.
        If iteration is in PENDING state, evaluate progress without failing for pending tasks.
        Otherwise return existing final status.
        """
            
        if final:
            self.finalize()
        else:
            # Calculate in-progress status
            statuses=extract_statuses(self.steps)
            self.status_counts = calculate_progress_statuses_breakdown(statuses)
            self.status = calculate_overall_status(status_counts=self.status_counts,current_status=self.status,final=final)

    def nb_tasks(self) -> int:
        return sum(
            step.nb_tasks() if hasattr(step, 'nb_tasks') else 1
            for step in self.steps.values() if not step.disabled
        )

    def set_pipeline_flow(self, pipeline_flow: 'PipelineFlow'):
        """Associate the sequence's tasks with the pipeline flow."""
        super().set_pipeline_flow(pipeline_flow)
        for step in self.steps.values():
            step.set_pipeline_flow(pipeline_flow)

    def finalize(self) -> None:
        """Calculate final status based on child step statuses"""
        if self.is_closed_or_skipped:
            return
            
        self.add_state("FINALIZING")
        self.calculate_duration()
        # Calculate overall status
        statuses = extract_statuses(self.steps)
        self.status_counts = calculate_progress_statuses_breakdown(statuses)
        self.status = calculate_overall_status(
            status_counts=self.status_counts,
            current_status=self.status,
            final=True
        )
        
        self.add_state(f"FINALIZED: {self.status.name} in {self.duration_s:.2f}s")

    def __str__(self):
        """
        Generate a string representation of the sequence. Doesn't update status. Ensure status is updated before calling.
        """
        sequence_status = f"[Sequence {self.sequence_ref} :: Status: {self.status.value}]"
        steps_str = "\n".join(f"    {str(step)}" for step in self.steps.values())
        return f"{sequence_status}\n{steps_str}"
    

class PipelineDynamicIterator(Step):
    def __init__(self,
                 name: str,
                 iteration_template: PipelineSequenceTemplate,
                 dependencies: Optional[List[Union[str, Dependency]]] = None,
                 disabled: bool = False,
                 max_iterations: Optional[int] = 100):
        super().__init__(name=name, disabled=disabled, dependencies=dependencies)
        self.iteration_template = iteration_template
        self.max_iterations = max_iterations
        self._iterations: Dict[Union[int, str], PipelineSequence] = {}
        self.status_counts = None

    @property
    def iterations(self) -> Dict[Union[int, str], PipelineSequence]:
        """Get all iterations"""
        return self._iterations

    @property
    def total_iterations(self) -> int:
        """Get total number of iterations"""
        return len(self._iterations)

    def set_iterations(self, iteration_refs: List[Union[int, str]]):
        """Set up iterations for given references"""
        if self.max_iterations < len(iteration_refs):
            raise ValueError(f"Cannot set {len(iteration_refs)} iterations - exceeds max_iterations {self.max_iterations}")
            
        self._iterations = {}
        for ref in iteration_refs:
            self.add_iteration(ref)

    def add_iteration(self, iteration_ref: Union[int, str]):
        """Add a single iteration"""
        if self.total_iterations >= self.max_iterations:
            raise ValueError(f"Cannot add iteration - would exceed max_iterations {self.max_iterations}")
            
        sequence = PipelineSequence(
            sequence_ref=iteration_ref,
            sequence_template=self.iteration_template
        )
        if self.pipeline_flow:
            sequence.set_pipeline_flow(self.pipeline_flow)
        self._iterations[iteration_ref] = sequence

    def remove_iteration(self, iteration_ref: Union[int, str]):
        """Remove an iteration by reference"""
        if iteration_ref in self._iterations:
            del self._iterations[iteration_ref]

    def clear_iterations(self):
        """Remove all iterations"""
        self._iterations.clear()

    def get_iteration(self, iteration_ref: Union[int, str]) -> Optional[PipelineSequence]:
        """Get iteration by reference"""
        if iteration_ref not in self._iterations:
            raise KeyError(f"Iteration {iteration_ref} not found in {self.name}")
        return self._iterations[iteration_ref]

    def set_pipeline_flow(self, pipeline_flow: 'PipelineFlow'):
        """Set pipeline flow for self and all iterations"""
        super().set_pipeline_flow(pipeline_flow)
        for iteration in self._iterations.values():
            iteration.set_pipeline_flow(pipeline_flow)

    def validate_and_start(self, set_status: Optional[ProgressStatus]=ProgressStatus.IN_PROGRESS,
                      sequence_ref: Optional[Union[int, str]]=None) -> Tuple[bool, Optional[str]]:
        """
        Enhanced validation for dynamic iterator including iteration checks.
        """
        # First validate common step requirements
        is_valid, error = super().validate_and_start(set_status, sequence_ref)
        if not is_valid:
            return False, error

        # Validate iterator-specific requirements
        if self.total_iterations == 0:
            self.status = ProgressStatus.INTENTIONALLY_SKIPPED
            self.add_state("No iterations configured")
            return False, "No iterations configured"

        if self.max_iterations < self.total_iterations:
            self.status = ProgressStatus.FAILED
            err_msg = f"Total iterations {self.total_iterations} exceeds max {self.max_iterations}"
            self.issues.append(err_msg)
            self.add_state(err_msg)
            return False, err_msg

        # Add iteration count to execution state
        self.add_state(f"Starting with {self.total_iterations} iterations")
        self.status = set_status
        return True, None

    def update_status_counts_and_overall_status(self, final:bool):
        """
        Update the current status of the sequence based on task statuses.
        If iteration is in PENDING state, evaluate progress without failing for pending tasks.
        Otherwise return existing final status.
        """
        if not self.iterations:
            return
            
        if final:
            self.finalize()
        else:
            # Calculate in-progress status
            statuses=extract_statuses(self.iterations)
            self.status_counts = calculate_progress_statuses_breakdown(statuses)
            self.status = calculate_overall_status(status_counts=self.status_counts,current_status=self.status,final=final)

    def close_step(self):
        """
        Close the group and set the status to disabled.
        """
        self.update_status_counts_and_overall_status(final=True)
    
    def finalize(self) -> None:
        """Calculate final status based on iteration statuses"""
        if self.is_closed_or_skipped:
            return
            
        self.add_state("FINALIZING")
        self.calculate_duration()
        
        if not self.iterations:
            self.status = ProgressStatus.INTENTIONALLY_SKIPPED
            self.add_state("Finalized with no iterations")
            return
            
        # Calculate overall status
        statuses = extract_statuses(self.iterations)
        self.status_counts = calculate_progress_statuses_breakdown(statuses)
        self.status = calculate_overall_status(
            status_counts=self.status_counts,
            current_status=self.status, 
            final=True
        )
        
        self.add_state(f"FINALIZED: {self.status.name} in {self.duration_s:.2f}s")
    
    def get_status_counts_for_step_across_iterations(self, step_name: str) -> Dict[str, int]:
        """
        Get aggregated status counts for a specific task across all iterations.
        """
        status_counts = defaultdict(int)

        for iteration in self.iterations.values():
            if step_name in iteration.steps:
                status:ProgressStatus = iteration.steps[step_name].status
                status_counts[status.value] += 1
                    
        return dict (status_counts)


    def nb_tasks(self) -> int:
        """Get the total number of tasks in the group."""
        return self.iteration_template.nb_tasks * self.total_iterations



    #TODO add step statuses across iterations
    # def __str__(self):
    #     group_status = f"[Status: {self.status.value}; Total_Iterations: {self.total_iterations}]:: Group: {self.name}"
    #     iteration_template_str = str(self.iteration_template)
    #     return f"{group_status}\n{iteration_template_str}"
    

    def __str__(self):
        indent=0
        header = f"{' ' * indent}**  {self.name} [Status: {self.status.name}]"
        if self.iterations:
            if not self.status_counts:
                self.update_status_counts_and_overall_status(final=False)

            iteration_info = (f"Total Iterations: {self.total_iterations}, Total_Statuses: {self.status_counts['total_statuses']}, "
                                + ", ".join(f"{status}: {count}" for status, count in self.status_counts['detailed'].items() if count > 0))
            header += f" [{iteration_info}]"
        else:
            header += " [No iterations yet]"

        # Template tasks with their aggregated statuses
        template_flow = []
        for step_name in self.iteration_template.steps:
            if self.iterations:
                step_status_counts = self.get_status_counts_for_step_across_iterations(step_name=step_name)
                step_info =  (f"[Total Iterations: {self.total_iterations}, "
                                + ", ".join(f"{status}: {count}" for status, count in step_status_counts.items() if count > 0))
                template_flow.append(
                    f"{' ' * (indent + 2)}>> {step_name} {step_info}"
                )
            else:
                template_flow.append(
                    f"{' ' * (indent + 2)}>> {step_name} [No iterations yet]"
                )
        return f"{header}\n{chr(10).join(template_flow)}" if template_flow else header


def _validate_step_name(name: str) -> bool:
    """Validate step name format"""
    if not isinstance(name, str):
        raise ValueError("Step name must be a string")
    if not name.strip():
        raise ValueError("Step name cannot be empty")
    if len(name) > 128:
        raise ValueError("Step name too long (max 128 chars)")
    return True





class PipelineFlow(PipelineSequence):
    """Top-level pipeline sequence"""

    def __init__(self, base_context_name: str, 
                 steps: Optional[List[Step]] = None,
                 disabled: bool = False):
        """
        Initialize pipeline flow.
        
        Args:
            base_context_name: Name/context for this pipeline
            steps: Optional initial steps
            disabled: Whether pipeline is disabled
        """
        super().__init__(
            sequence_ref=base_context_name,
            steps=steps,  # Pass initial steps if provided
            dependencies=None
        )
        self.base_context = base_context_name
        self.disabled = disabled
        self.pipeline_flow = self
        self._total_tasks = sum(step.nb_tasks() for step in (steps or []))
        self._completed_tasks = 0

    def add_step(self, step: Step):
        """Add a step to the pipeline with validation."""
        if step.disabled:
            return

        _validate_step_name(step.name)
        
        if step.name in self.steps:
            raise ValueError(f"Step with name '{step.name}' already exists")

        self.steps[step.name] = step
        step.set_pipeline_flow(self)
        self._total_tasks += step.nb_tasks()

    @property
    def completion_percentage(self) -> float:
        """Get completion percentage based on tasks"""
        if self._total_tasks == 0:
            return 0.0
        return round((self._completed_tasks / self._total_tasks) * 100, 2)

    def update_task_completion(self, completed: int):
        """Update completed task count"""
        self._completed_tasks += completed
        if self._completed_tasks > self._total_tasks:
            self._completed_tasks = self._total_tasks
            
    def finalize(self) -> None:
        """Calculate final pipeline status based on all step statuses"""
        if self.is_closed_or_skipped:
            return
        self.add_state("FINALIZING PIPELINE")
        self.calculate_duration()
        
        # First finalize any unfinalized steps
        for step in self.steps.values():
            if not step.is_closed_or_skipped:
                step.finalize()
        
        # Calculate overall status
        statuses = extract_statuses(self.steps)
        self.status_counts = calculate_progress_statuses_breakdown(statuses)
        self.status = calculate_overall_status(
            status_counts=self.status_counts,
            current_status=self.status,
            final=True
        )
        
        # Add detailed completion info
        completion_info = (
            f"PIPELINE FINALIZED:\n"
            f"Status: {self.status.name}\n"
            f"Duration: {self.duration_s:.2f}s\n"
            f"Completion: {self.completion_percentage}%\n"
            f"Total Tasks: {self._total_tasks}\n"
            f"Completed Tasks: {self._completed_tasks}"
        )
        self.add_state(completion_info)

    def get_pipeline_flow_str(self) -> str:
        """Generate detailed pipeline flow string with metrics and status breakdown"""
        status_info = ""
        if self.status_counts:
            status_info = (
                f"Status Breakdown:\n"
                + "\n".join(f"  {status}: {count}" 
                           for status, count in self.status_counts['detailed'].items()
                           if count > 0)
            )
            
        lines = [
            f"Pipeline: {self.base_context}",
            f"Status: {self.status.name}",
            f"Progress: {self.completion_percentage}%",
            f"Duration: {self.duration_s:.1f}s",
            f"Total Tasks: {self._total_tasks}",
            status_info,
            "Steps:",
            "-------"
        ]

        for step in self.steps.values():
            if not step.disabled:
                lines.append(str(step))

        return "\n".join(lines)

    def validate_steps_dependencies_exist(self) -> bool:
        """Validate all pipeline dependencies"""
        def _validate_step_dependencies(step: Step, path: List[str]) -> None:
            current_path = path + [step.name]

            # Check for circular dependencies
            if len(set(current_path)) != len(current_path):
                cycle = current_path[current_path.index(step.name):]
                raise ValueError(f"Circular dependency detected: {' -> '.join(cycle)}")

            # Validate direct dependencies
            for dep in step.dependencies:
                if isinstance(dep, str):
                    dep = Dependency(dep)
                try:
                    dep_step = self.get_step(dep.step_name)
                    if not dep.optional:
                        _validate_step_dependencies(dep_step, current_path)
                except KeyError as exc:
                    if not dep.optional:
                        raise ValueError(
                            f"Missing required dependency '{dep.step_name}' for step '{step.name}'. "
                            f"Path: {' -> '.join(current_path)}"
                        ) from exc

            # Validate template steps for dynamic iterators
            if isinstance(step, PipelineDynamicIterator):
                for template_step in step.iteration_template.steps.values():
                    _validate_step_dependencies(template_step, current_path)

        # Always validate every step
        for step in self.steps.values():
            _validate_step_dependencies(step, [])

        return True
    
    def validate_and_start(self, set_status: Optional[ProgressStatus]=ProgressStatus.IN_PROGRESS):
        """Validate and start pipeline execution"""
        # First validate pipeline dependencies
        self.validate_steps_dependencies_exist()
        
        # Start execution tracking
        self._start_time = datetime.now(timezone.utc)
        self.add_state("STARTED")
        self.status = set_status
        return True, None
        

    def get_step(self, name: str, sequence_ref: Optional[Union[int, str]] = None) -> Step:
        """Get step by name with improved error handling."""
        if name in self.steps:
            return self.steps[name]

        # Search in dynamic groups
        for step in self.steps.values():
            if isinstance(step, PipelineDynamicIterator):
                # Check specific iteration if reference provided
                if sequence_ref is not None and sequence_ref in step.iterations:
                    iteration = step.iterations[sequence_ref]
                    if name in iteration.steps:
                        return iteration.steps[name]
                # Check template steps
                elif name in step.iteration_template.steps:
                    return step.iteration_template.steps[name]

        raise KeyError(
            f"Step '{name}' not found in pipeline flow "
            f"{'or specified iteration' if sequence_ref else ''}"
        )

    def get_pipeline_description(self) -> str:
        """
        Generate the complete pipeline description with base context and pipeline flow.
        :return: String representing the pipeline description.
        """
        return f"{self.base_context}\nflow:\n{self.get_pipeline_flow_str()}"


