from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union, List
from datetime import datetime, timezone
import json
import uuid
from ipulse_shared_base_ftredge import (ProgressStatus, to_enum, evaluate_combined_progress_status)

@dataclass
class FunctionResult:
    """Base class for function results with status tracking"""
    name: str = field(default_factory=lambda: str(uuid.uuid4()))
    _data: Any = None
    _overall_status: ProgressStatus = ProgressStatus.IN_PROGRESS
    _execution_state: List[str] = field(default_factory=list)
    _issues: List[Any] = field(default_factory=list)
    _warnings: List[Any] = field(default_factory=list)
    _notices: List[Any] = field(default_factory=list)
    _metadata: Dict[str, Any] = field(default_factory=dict)
    _start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _duration_s: float = 0.0
    _results_aggregated: int = 1  # Default to 1 for the current function

    @property
    def data(self) -> Any:
        """Get data"""
        return self._data
    
    @data.setter
    def data(self, value: Any) -> None:
        """Set data"""
        self._data = value

    def add_data(self, values: Any, name: str) -> None:
        """Add data to a dict with a name"""
        if not self.data:
            self.data = {}
        elif not isinstance(self.data, dict):
            raise ValueError("Data must be a dictionary to add more values")
        self.data[name] = values

    @property
    def overall_status(self) -> ProgressStatus:
        """Get overall status"""
        return self._overall_status
    
    @overall_status.setter
    def overall_status(self, value: Union[ProgressStatus, str]) -> None:
        """Set overall status"""
        self._overall_status = to_enum(value=value, enum_class=ProgressStatus, required=True, default=ProgressStatus.UNKNOWN)

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
    
    # ------------------
    # Metadata
    # ------------------
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get metadata"""
        return self._metadata
    
    @metadata.setter
    def metadata(self, value: Dict[str, Any]) -> None:
        """Set metadata"""
        self._metadata = value

    def add_metadata(self, **kwargs) -> None:
        """Add metadata key-value pairs"""

        self.metadata.update(kwargs)

    def add_metadata_from_dict(self, metadata: Dict[str, Any]) -> None:
        """Add metadata from a dictionary"""
        self.metadata.update(metadata)

    # ------------------
    # Timing
    # ------------------
    @property
    def start_time(self) -> datetime:
        """Get start time"""
        return self._start_time

    @property
    def duration_s(self) -> float:
        """Get duration in seconds"""
        return self._duration_s
    
    @duration_s.setter
    def duration_s(self, value: float) -> None:
        """Set duration in seconds"""
        self._duration_s = value

    def calculate_duration(self) -> None:
        """Set final duration in seconds"""
        self._duration_s = (datetime.now(timezone.utc) - self.start_time).total_seconds()

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

    def integrate_result(self, child_result: "FunctionResult", combine_status=True, skip_data: bool = True, skip_metadata: bool = True) -> None:
        """Integrate a child operation result into this result"""
        # Add child's operation ID to execution state
        self.add_state(f"Integrating Child OpR {child_result.name}")

        # Aggregate issues, warnings, notices
        self._issues.extend(child_result.issues)
        self._warnings.extend(child_result.warnings)
        self._notices.extend(child_result.notices)

        # Merge execution states
        self._execution_state.extend(child_result.execution_state)

        # Merge metadata
        if not skip_metadata:
            self._metadata.update(child_result.metadata)

        # Sum total functions
        self.increment_results_aggregated(child_result.results_aggregated)

        # Optionally merge data
        if not skip_data and child_result.data:
            if self._data is None:
                self._data = child_result.data
            elif isinstance(self._data, dict) and isinstance(child_result.data, dict):
                self._data.update(child_result.data)

        # Determine overall status using priority
        if combine_status:
            self.overall_status = evaluate_combined_progress_status(
                [self.overall_status, child_result.overall_status]
            )
    

    # ------------------
    # Closing / Finalizing
    # ------------------

    @property
    def is_success(self) -> bool:
        """Check if operation is successful"""
        return self.overall_status in ProgressStatus.success_statuses() or self.overall_status in ProgressStatus.skipped_statuses() 

    @property
    def is_closed(self) -> bool:
        """Check if operation is closed"""
        return self.overall_status in ProgressStatus.closed_or_skipped_statuses()

    

    def final(self, status: Optional[ProgressStatus] = None, force_if_closed: bool = True, raise_issue_on_unknown: bool = True) -> None:
        """Mark operation as complete"""

        if self.is_closed and status:
            if force_if_closed:
                if self.overall_status in ProgressStatus.issue_statuses():
                    self.warnings.append(f"Operation is already closed at value {self.overall_status}, forcing status to {status}")
                else:
                    self.notices.append(f"Operation is already closed at value {self.overall_status}, forcing status to {status}")
                self.overall_status = to_enum(value=status, enum_class=ProgressStatus, required=True, default=ProgressStatus.UNKNOWN)
            else:
                self.notices.append(f"Operation is already closed, not changing status to {status} because force_if_closed is False")
        elif status:
            self.overall_status = to_enum(value=status, enum_class=ProgressStatus, required=True, default=ProgressStatus.UNKNOWN)
            if self.overall_status == ProgressStatus.UNKNOWN:
                if raise_issue_on_unknown:
                    raise ValueError("Invalid final Progress Status provided")
                else:
                    self.warnings.append(f"Invalid final Progress Status provided: {status}")
        elif self.issues:
            self.overall_status = ProgressStatus.FINISHED_WITH_ISSUES
        elif self.warnings:
            self.overall_status = ProgressStatus.DONE_WITH_WARNINGS
        elif self.notices:
            self.overall_status = ProgressStatus.DONE_WITH_NOTICES
        else:
            self.overall_status = ProgressStatus.DONE
        if self.overall_status == ProgressStatus.UNKNOWN and raise_issue_on_unknown:
            raise ValueError("Invalid final Progress Status provided")
        self.calculate_duration()
        self.add_state("CLOSED STATUS")

    def get_status_info(self, exclude_none: bool = True) -> str:
        """Get all information as a JSON string"""
        info_dict = {
            "overall_status": self.overall_status.name,
            "name": self.name,
            "execution_state": self.execution_state_str,
            "issues": self.issues_str,
            "warnings": self.warnings_str,
            "notices": self.notices_str,
            "metadata": self.metadata,
            "results_aggregated": self.results_aggregated,
            "start_time": self.start_time.isoformat(),
            "duration_s": self.duration_s
        }
        
        if exclude_none:
            info_dict = {k: v for k, v in info_dict.items() if v is not None}
            
        return json.dumps(info_dict, default=str, indent=2)

    def __str__(self) -> str:
        """String representation of the object"""
        return self.get_status_info()

    def to_dict(self, infos_as_str: bool = True, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format"""
        status_dict = {
            "overall_status": self.overall_status.name,
            "name": self.name,
            "execution_state": self.execution_state_str if infos_as_str else self.execution_state,
            "issues": self.issues_str if infos_as_str else self.issues,
            "warnings": self.warnings_str if infos_as_str else self.warnings,
            "notices": self.notices_str if infos_as_str else self.notices,
            "metadata": json.dumps(self.metadata, default=str, indent=2) if infos_as_str else self.metadata,
            "results_aggregated": self.results_aggregated,
            "start_time": self.start_time.isoformat(),
            "duration_s": self.duration_s
        }
        
        if exclude_none:
            status_dict = {k: v for k, v in status_dict.items() if v is not None}

        result = {
            "data": self.data,
            "status": status_dict
        }
        
        if exclude_none and result["data"] is None:
            result.pop("data")
            
        return result
