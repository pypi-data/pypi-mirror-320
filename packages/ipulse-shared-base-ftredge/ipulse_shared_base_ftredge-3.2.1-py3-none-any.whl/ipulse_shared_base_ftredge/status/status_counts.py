from collections import defaultdict
from typing import Dict, Any, List, Set, Union
from ipulse_shared_base_ftredge import ProgressStatus

class StatusCounts:
    """Class for tracking and analyzing status counts with smart aggregation methods"""
    
    def __init__(self):
        self._total_count = 0
        self._by_status_count = defaultdict(int)
        self._by_category_count = defaultdict(int)

    @property
    def total_count(self) -> int:
        """Get total number of statuses counted"""
        return self._total_count

    @property
    def by_status_count(self) -> Dict[str, int]:
        """Get counts for individual statuses"""
        return dict(self._by_status_count)
        

    @property
    def by_category_count(self) -> Dict[str, int]:
        """Get counts for status categories"""
        return dict(self._by_category_count)

        
    def add_status(self, status: ProgressStatus) -> None:
        """Add a single status occurrence"""
        self._by_status_count[status] += 1
        self._total_count += 1
        self._update_category_counts(status)
    
    def add_statuses(self, statuses: List[ProgressStatus]) -> None:
        """Add multiple status occurrences at once"""
        for status in statuses:
            self.add_status(status)
            
    def remove_status(self, status: ProgressStatus) -> None:
        """Remove a single status occurrence"""
        if self._by_status_count[status] > 0:
            self._by_status_count[status] -= 1
            self._total_count -= 1
            self._update_category_counts(status, removing=True)
            
    def _update_category_counts(self, status: ProgressStatus, removing: bool = False) -> None:
        """Update category counts when adding/removing a status"""
        change = -1 if removing else 1
        
        # Update category counts based on status membership
        if status in ProgressStatus.pending_statuses():
            self._by_category_count['pending_statuses'] += change
        if status in ProgressStatus.success_statuses():
            self._by_category_count['success_statuses'] += change
        if status in ProgressStatus.failed_statuses():
            self._by_category_count['failed_statuses'] += change
        if status in ProgressStatus.skipped_statuses():
            self._by_category_count['skipped_statuses'] += change
        if status in ProgressStatus.issue_statuses():
            self._by_category_count['issue_statuses'] += change
        if status in ProgressStatus.closed_statuses():
            self._by_category_count['closed_statuses'] += change
        

    def get_count_breakdown(self, string_format: bool = True) -> Dict[str, Any]:
        """Get complete status count breakdown"""

        # Return only detailed counts if requested
        
        result = {
            'total_count': self._total_count,
            'by_status_count': {},
            'by_category_count': dict(self._by_category_count)  
        }
        
        # Convert status keys to strings if requested
        if string_format:
            result['by_status_count'] = {
                status.name: count
                for status, count in self._by_status_count.items()
            }
        else:
            result['by_status_count'] = self._by_status_count
            
        return result

    def has_any_status(self, statuses: Union[ProgressStatus, List[ProgressStatus], Set[ProgressStatus]]) -> bool:
        """Check if any of the given statuses exist"""
        if isinstance(statuses, ProgressStatus):
            statuses = [statuses]
        return any(self._by_status_count[status] > 0 for status in statuses)

    def count_statuses(self, statuses: Union[ProgressStatus, List[ProgressStatus], Set[ProgressStatus]]) -> int:
        """Count occurrences of specific statuses"""
        if isinstance(statuses, ProgressStatus):
            statuses = [statuses]
        return sum(self._by_status_count[status] for status in statuses)
        

    def get_category_count(self, category_name: str) -> int:
        """Get count for a specific category"""
        return self._by_category_count.get(category_name, 0)

    @property
    def has_failures(self) -> bool:
        """Check if there are any issue statuses"""
        return self.get_category_count('failed_statuses') > 0
    
    @property
    def has_issues(self) -> bool:
        """Check if there are any issue statuses"""
        return self.get_category_count('issue_statuses') > 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warning statuses (DONE_WITH_WARNINGS)"""
        return self._by_status_count[ProgressStatus.DONE_WITH_WARNINGS] > 0 or self.has_any_status(ProgressStatus.IN_PROGRESS_WITH_WARNINGS)

    @property
    def has_notices(self) -> bool:
        """Check if there are any notice statuses (DONE_WITH_NOTICES)"""
        return self._by_status_count[ProgressStatus.DONE_WITH_NOTICES] > 0 or self.has_any_status(ProgressStatus.IN_PROGRESS_WITH_NOTICES)

    @property
    def all_closed(self) -> bool:
        """Check if all statuses are in closed or skipped categories"""
        return self.total_count == self.get_category_count('closed_statuses')
    
    @property
    def all_closed_or_skipped(self) -> bool:
        """Check if all statuses are in closed or skipped categories"""
        return self.total_count == self.get_category_count('closed_or_skipped_statuses')

    @property
    def all_success(self) -> bool:
        """Check if all statuses are successful"""
        return self.total_count == self.get_category_count('success_statuses')
    
    @property
    def completion_rate(self) -> float:
        """Get completion rate as percentage"""
        if self.total_count == 0:
            return 0.0
        completed = self.get_category_count('closed_statuses') + self.get_category_count('skipped_statuses')
        return (completed / self.total_count) * 100

    @property
    def success_rate(self) -> float:
        """Get success rate as percentage"""
        if self.total_count == 0:
            return 0.0
        return (self.get_category_count('success_statuses') / self.total_count) * 100
    
    def to_status_set(self) -> Set[ProgressStatus]:
        """Convert status counts to a set of ProgressStatus instances"""
        status_set = set()
        for status, count in self._by_status_count.items():
            for _ in range(count):
                status_set.add(status)
        return status_set

    def get_summary(self) -> str:
        """Get human-readable summary of status counts"""
        if self.total_count == 0:
            return "No statuses recorded"
            
        parts = [
            f"Total count: {self.total_count}",
            f"Completion: {self.completion_rate:.1f}%",
            f"Success rate: {self.success_rate:.1f}%"
        ]
        
        # Add counts by category
        for category, count in self._by_category_count.items():
            if count > 0:
                parts.append(f"{category}: {count}")
                
        # Add specific status counts
        detailed = [f"{status.name}: {count}" 
                   for status, count in self._by_status_count.items() 
                   if count > 0]
        if detailed:
            parts.append("Detailed counts:")
            parts.extend(f"  {item}" for item in detailed)
            
        return "\n".join(parts)

    def __str__(self) -> str:
        return self.get_summary()




def eval_statuses(
    status_input: Union[Set[ProgressStatus], List[ProgressStatus], StatusCounts],
    final: bool = False,
    issues_allowed: bool = True
) -> ProgressStatus:
    """
    Determine overall status from either a set of statuses or StatusCounts object.
    
    Args:
        status_input: Either a set/list of ProgressStatus or StatusCounts object
        final: Whether this is final status calculation
        issues_allowed: Whether issues are allowed in non-final status
        
    Returns:
        ProgressStatus representing overall status
    """
    # Convert input to set of statuses if needed
    if isinstance(status_input, StatusCounts):
        statuses = status_input.to_status_set()
    else:
        statuses = set(status_input)
    
    total_count = len(statuses)
    if total_count == 0:
        return ProgressStatus.NOT_STARTED

    # Handle fully skipped case
    skipped = {s for s in statuses if s in ProgressStatus.skipped_statuses()}
    if len(skipped) == total_count:
        return ProgressStatus.INTENTIONALLY_SKIPPED

    # Count various status types
    pending_statuses = {s for s in statuses if s in ProgressStatus.pending_statuses()}
    failed = {s for s in statuses if s == ProgressStatus.FAILED}
    failed_statuses = {s for s in statuses if s in ProgressStatus.failed_statuses()}
    blocked = {s for s in statuses if s == ProgressStatus.BLOCKED_BY_UNRESOLVED_DEPENDENCY}
    issues = {s for s in statuses if s in ProgressStatus.issue_statuses()}
    warnings_statuses = {s for s in statuses if s in [ProgressStatus.IN_PROGRESS_WITH_WARNINGS, ProgressStatus.DONE_WITH_WARNINGS]}
    notices_statuses = {s for s in statuses if s in [ProgressStatus.IN_PROGRESS_WITH_NOTICES, ProgressStatus.DONE_WITH_NOTICES]}
    success_statuses = {s for s in statuses if s in ProgressStatus.success_statuses()}
    unfinished = {s for s in statuses if s == ProgressStatus.UNFINISHED}
    # Handle final status calculation
    if final:
        if pending_statuses:
            # If there are failures with pending items, it's a failure
            if issues:
                return ProgressStatus.FAILED
            return ProgressStatus.UNFINISHED
            
        # All items are complete at this point 
        # Check Issues
        if failed_statuses:
            if not issues_allowed:
                return ProgressStatus.FAILED
            
            if failed:
                if (len(failed) + len(blocked)+ len(skipped)+len(unfinished)) == total_count:
                    return ProgressStatus.FAILED
                if unfinished:
                    return ProgressStatus.UNFINISHED
            
                return ProgressStatus.FINISHED_WITH_ISSUES
            
        # Fallback to highest priority
        return max(statuses, key=lambda s: s.value)

    # Non-final status calculation
    # All items are complete at this point

    if pending_statuses:
        if (len(issues) + len(skipped)) == total_count:
            return ProgressStatus.FAILED
        if issues:
            if not issues_allowed:
                return ProgressStatus.FAILED
            return ProgressStatus.IN_PROGRESS_WITH_ISSUES

        if warnings_statuses:
            return ProgressStatus.IN_PROGRESS_WITH_WARNINGS
        if notices_statuses:
            return ProgressStatus.IN_PROGRESS_WITH_NOTICES
        if len(pending_statuses) == total_count and ProgressStatus.NOT_STARTED in pending_statuses:
            return ProgressStatus.NOT_STARTED
        return ProgressStatus.IN_PROGRESS
    
    if failed_statuses:
        if not issues_allowed:
            return ProgressStatus.FAILED
        if unfinished:
            return ProgressStatus.UNFINISHED
        return ProgressStatus.FINISHED_WITH_ISSUES

    # Fallback to highest priority status
    return max(statuses, key=lambda s: s.value)


# def eval_combined_progress_status(statuses: List[ProgressStatus]) -> ProgressStatus:
#     """Determine the overall status based on child statuses"""
    
#     # Handle specific combinatory cases
#     if ProgressStatus.NOT_STARTED in statuses:
#         if any(status in statuses for status in [
#             ProgressStatus.DONE_WITH_WARNINGS,
#             ProgressStatus.DONE_WITH_NOTICES,
#             ProgressStatus.DONE
#         ]):
#             return ProgressStatus.IN_PROGRESS
        
#     if ProgressStatus.FINISHED_WITH_ISSUES in statuses and ProgressStatus.pending_statuses() in statuses:
#         return ProgressStatus.FAILED
    
#     if ProgressStatus.UNFINISHED in statuses and ProgressStatus.FINISHED_WITH_ISSUES in statuses:
#         return ProgressStatus.FAILED

#     # Determine the highest priority status based on enum value
#     highest_priority_status = max(statuses, key=lambda status: status.value)


#     return highest_priority_status

