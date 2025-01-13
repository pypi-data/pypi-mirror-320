from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
import json
from ..enums import ProgressStatus
from ..utils import to_enum
from . import eval_statuses

class StatusTrackingMixin:
    """Mixin class providing common status tracking functionality"""
    
    def __init__(self):
        self._issues: List[Any] = []
        self._warnings: List[Any] = []
        self._notices: List[Any] = []
        self._execution_state: List[str] = []
        self._metadata: Dict[str, Any] = {}
        self._statuses_aggregated: int = 1
        self._progress_status: ProgressStatus = ProgressStatus.NOT_STARTED

    @property
    def progress_status(self) -> ProgressStatus:
        """Get progress status"""
        return self._progress_status
    
    @progress_status.setter
    def progress_status(self, value: Union[ProgressStatus, str]) -> None:
        """Set progress status"""
        self._progress_status = to_enum(value=value, enum_class=ProgressStatus, required=True, default=ProgressStatus.UNKNOWN)

    @property
    def is_success(self) -> bool:
        """Check if operation is successful"""
        return self.progress_status in ProgressStatus.success_statuses()

    @property 
    def is_closed(self) -> bool:
        """Check if operation is closed"""
        return self.progress_status in ProgressStatus.closed_or_skipped_statuses()

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

    def add_warning(self, warning: Any, update_state:bool=True) -> None:
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

    def add_notice(self, notice: Any, update_state:bool=True) -> None:
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

    @property
    def statuses_aggregated(self) -> int:
        """Get total statuses tracked"""
        return self._statuses_aggregated

    @statuses_aggregated.setter
    def statuses_aggregated(self, value: int) -> None:
        """Set total statuses tracked"""
        self._statuses_aggregated = value

    def increment_statuses_aggregated(self, value: int) -> None:
        """Increment total statuses tracked"""
        self._statuses_aggregated += value

    def integrate_status_tracker(self, next: 'StatusTrackingMixin',
                               combine_status: bool = True,
                               issues_allowed: bool = False,
                               skip_metadata: bool = True,
                               name: Optional[str] = None) -> None:
        """
        Integrate another status tracker's state into this one
        
        Args:
            other: Another StatusTrackingMixin instance to integrate from
            combine_status: Whether to combine progress statuses
            skip_metadata: Whether to skip metadata integration
            name: Optional name of the tracker being integrated for state logging
        """
        # Add integration state
        integration_name = name if name else "other tracker"
        self.add_state(f"Integrating {integration_name}.")

        # Aggregate issues, warnings, notices
        self._issues.extend(next.issues)
        self._warnings.extend(next.warnings)
        self._notices.extend(next.notices)

        # Merge execution states
        self._execution_state.extend(next.execution_state)
        
        # Sum total functions
        self.increment_statuses_aggregated(next.statuses_aggregated)

        # Handle metadata if not skipped
        if not skip_metadata:
            self._metadata.update(next.metadata)

        # Update progress status if requested
        if combine_status:
            self.progress_status = eval_statuses(
                [self.progress_status, next.progress_status],
                final=False,  # During integration we treat as non-final
                issues_allowed=issues_allowed  # Default to allowing issues during integration
            )

        # Add completion state
        self.add_state(f"Completed integrating {integration_name}")

    def get_status_report(self, exclude_none: bool = True) -> str:
        """Get all information as a JSON string"""
        info_dict = {
            "progress_status": self.progress_status.name,
            "execution_state": self.execution_state_str,
            "issues": self.issues_str,
            "warnings": self.warnings_str,
            "notices": self.notices_str,
            "metadata": self.metadata,
            "statuses_aggregated": self.statuses_aggregated
        }
        
        if exclude_none:
            info_dict = {k: v for k, v in info_dict.items() if v is not None}
            
        return json.dumps(info_dict, default=str, indent=2)

    def __str__(self) -> str:
        """String representation of the object"""
        return self.get_status_report()

    def to_dict(self, infos_as_str: bool = True, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format"""
        status_dict = {
            "progress_status": self.progress_status.name,
            "execution_state": self.execution_state_str if infos_as_str else self.execution_state,
            "issues": self.issues_str if infos_as_str else self.issues,
            "warnings": self.warnings_str if infos_as_str else self.warnings,
            "notices": self.notices_str if infos_as_str else self.notices,
            "metadata": json.dumps(self.metadata, default=str, indent=2) if infos_as_str else self.metadata,
            "statuses_aggregated": self.statuses_aggregated
        }
        
        if exclude_none:
            status_dict = {k: v for k, v in status_dict.items() if v is not None}

        return status_dict
