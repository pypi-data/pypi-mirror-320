import unittest
from ipulse_shared_base_ftredge import ProgressStatus, StatusCounts, eval_statuses

class TestStatusCounts(unittest.TestCase):
    def setUp(self):
        self.status_counts = StatusCounts()

    def test_empty_status_counts(self):
        """Test initial state of StatusCounts"""
        self.assertEqual(self.status_counts.total_count, 0)
        self.assertEqual(len(self.status_counts.by_status_count), 0)
        self.assertEqual(len(self.status_counts.by_category_count), 0)
        self.assertEqual(self.status_counts.completion_rate, 0.0)
        self.assertEqual(self.status_counts.success_rate, 0.0)

    def test_add_single_status(self):
        """Test adding a single status"""
        self.status_counts.add_status(ProgressStatus.DONE)
        self.assertEqual(self.status_counts.total_count, 1)
        self.assertEqual(self.status_counts.by_status_count[ProgressStatus.DONE], 1)
        self.assertEqual(self.status_counts.get_category_count('success_statuses'), 1)

    def test_add_multiple_statuses(self):
        """Test adding multiple statuses"""
        statuses = [ProgressStatus.DONE, ProgressStatus.IN_PROGRESS, ProgressStatus.FAILED]
        self.status_counts.add_statuses(statuses)
        self.assertEqual(self.status_counts.total_count, 3)
        self.assertEqual(self.status_counts.get_category_count('success_statuses'), 1)
        self.assertEqual(self.status_counts.get_category_count('pending_statuses'), 1)
        self.assertEqual(self.status_counts.get_category_count('failed_statuses'), 1)

    def test_remove_status(self):
        """Test removing a status"""
        self.status_counts.add_status(ProgressStatus.DONE)
        self.status_counts.remove_status(ProgressStatus.DONE)
        self.assertEqual(self.status_counts.total_count, 0)
        self.assertEqual(self.status_counts.by_status_count[ProgressStatus.DONE], 0)
        self.assertEqual(self.status_counts.get_category_count('success_statuses'), 0)

    def test_category_counts(self):
        """Test category counting logic"""
        status_map = {
            ProgressStatus.IN_PROGRESS: 'pending_statuses',
            ProgressStatus.DONE: 'success_statuses',
            ProgressStatus.FAILED: 'failed_statuses',
            ProgressStatus.INTENTIONALLY_SKIPPED: 'skipped_statuses'
        }

        for status, category in status_map.items():
            self.status_counts.add_status(status)
            self.assertEqual(self.status_counts.get_category_count(category), 1)

    def test_has_properties(self):
        """Test boolean status properties"""
        # Test has_failures
        self.status_counts.add_status(ProgressStatus.FAILED)
        self.assertTrue(self.status_counts.has_failures)

        # Test has_issues
        self.status_counts.add_status(ProgressStatus.FINISHED_WITH_ISSUES)
        self.assertTrue(self.status_counts.has_issues)

        # Test has_warnings
        self.status_counts.add_status(ProgressStatus.DONE_WITH_WARNINGS)
        self.assertTrue(self.status_counts.has_warnings)

        # Test has_notices
        self.status_counts.add_status(ProgressStatus.DONE_WITH_NOTICES)
        self.assertTrue(self.status_counts.has_notices)

    def test_completion_and_success_rates(self):
        """Test completion and success rate calculations"""
        # Add mix of statuses
        self.status_counts.add_statuses([
            ProgressStatus.DONE,  # Success
            ProgressStatus.IN_PROGRESS,  # Pending
            ProgressStatus.FAILED,  # Closed
            ProgressStatus.INTENTIONALLY_SKIPPED  # Skipped
        ])

        # Expected rates
        expected_completion = (3 / 4) * 100  # DONE , FAILED  and INTENTIONALLY_SKIPPED are closed/skipped
        expected_success = (1 / 4) * 100  # Only DONE is success

        self.assertEqual(self.status_counts.completion_rate, expected_completion)
        self.assertEqual(self.status_counts.success_rate, expected_success)

    def test_to_status_set(self):
        """Test conversion to status set"""
        original_statuses = [
            ProgressStatus.DONE,
            ProgressStatus.DONE,  # Duplicate will be combined in set
            ProgressStatus.IN_PROGRESS
        ]
        for status in original_statuses:
            self.status_counts.add_status(status)

        status_set = self.status_counts.to_status_set()
        self.assertEqual(len(status_set), 2)  # Should be 2 unique statuses
        self.assertTrue(ProgressStatus.DONE in status_set)
        self.assertTrue(ProgressStatus.IN_PROGRESS in status_set)

class TestEvalStatus(unittest.TestCase):
    def test_empty_input(self):
        """Test evaluation of empty input"""
        self.assertEqual(eval_statuses([]), ProgressStatus.NOT_STARTED)
        self.assertEqual(eval_statuses(set()), ProgressStatus.NOT_STARTED)
        self.assertEqual(eval_statuses(StatusCounts()), ProgressStatus.NOT_STARTED)

    def test_all_skipped(self):
        """Test when all statuses are skipped"""
        skipped_statuses = [
            ProgressStatus.INTENTIONALLY_SKIPPED,
            ProgressStatus.CANCELLED,
            ProgressStatus.DISABLED
        ]
        self.assertEqual(eval_statuses(skipped_statuses), ProgressStatus.INTENTIONALLY_SKIPPED)



    def test_issues_allowed_with_final_true(self):

        self.assertEqual(
            eval_statuses([ProgressStatus.FINISHED_WITH_ISSUES, ProgressStatus.INTENTIONALLY_SKIPPED], final=True, issues_allowed=True),
            ProgressStatus.FINISHED_WITH_ISSUES
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.DONE, ProgressStatus.INTENTIONALLY_SKIPPED], final=True, issues_allowed=True),
            ProgressStatus.DONE
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FINISHED_WITH_ISSUES, ProgressStatus.DONE], final=True, issues_allowed=True),
            ProgressStatus.FINISHED_WITH_ISSUES
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FINISHED_WITH_ISSUES, ProgressStatus.DONE], final=True, issues_allowed=False),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FAILED, ProgressStatus.DONE], final=True, issues_allowed=True),
            ProgressStatus.FINISHED_WITH_ISSUES
        )
        self.assertEqual(
            eval_statuses([ProgressStatus.FAILED, ProgressStatus.DONE], final=True, issues_allowed=False),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FAILED, ProgressStatus.BLOCKED_BY_UNRESOLVED_DEPENDENCY], final=True, issues_allowed=True),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FAILED, ProgressStatus.BLOCKED_BY_UNRESOLVED_DEPENDENCY], final=True, issues_allowed=False),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FINISHED_WITH_ISSUES, ProgressStatus.BLOCKED_BY_UNRESOLVED_DEPENDENCY], final=True, issues_allowed=True),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FINISHED_WITH_ISSUES, ProgressStatus.BLOCKED_BY_UNRESOLVED_DEPENDENCY], final=True, issues_allowed=False),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FAILED, ProgressStatus.IN_PROGRESS], final=True, issues_allowed=True),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FAILED, ProgressStatus.IN_PROGRESS], final=True, issues_allowed=False),
            ProgressStatus.FAILED
        )

        # Mixed Success with Warnings = DONE_WITH_WARNINGS
        self.assertEqual(
            eval_statuses([ProgressStatus.DONE, ProgressStatus.DONE_WITH_WARNINGS], final=True, issues_allowed=True),
            ProgressStatus.DONE_WITH_WARNINGS
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.DONE, ProgressStatus.DONE_WITH_WARNINGS], final=True, issues_allowed=False),
            ProgressStatus.DONE_WITH_WARNINGS
        )


        self.assertEqual(
            eval_statuses([ProgressStatus.DONE, ProgressStatus.IN_PROGRESS_WITH_ISSUES], final=True, issues_allowed=True),
            ProgressStatus.FAILED # FINAL is evaluated first and all not finished finals are considered as FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.DONE, ProgressStatus.IN_PROGRESS_WITH_ISSUES], final=True, issues_allowed=False),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.DONE, ProgressStatus.IN_PROGRESS_WITH_WARNINGS], final=True, issues_allowed=True),
            ProgressStatus.UNFINISHED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.DONE, ProgressStatus.IN_PROGRESS_WITH_WARNINGS], final=True, issues_allowed=False),
            ProgressStatus.UNFINISHED
        )
############################################################################################################

    def test_issues_allowed_with_final_false(self):
        """Test final status calculation scenarios"""

        self.assertEqual(
            eval_statuses([ProgressStatus.FINISHED_WITH_ISSUES, ProgressStatus.INTENTIONALLY_SKIPPED], final=False, issues_allowed=True),
            ProgressStatus.FINISHED_WITH_ISSUES
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.DONE, ProgressStatus.INTENTIONALLY_SKIPPED], final=False, issues_allowed=True),
            ProgressStatus.DONE
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FINISHED_WITH_ISSUES, ProgressStatus.DONE], final=False, issues_allowed=True),
            ProgressStatus.FINISHED_WITH_ISSUES
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FINISHED_WITH_ISSUES, ProgressStatus.DONE], final=False, issues_allowed=False),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FAILED, ProgressStatus.DONE], final=False, issues_allowed=True),
            ProgressStatus.FINISHED_WITH_ISSUES
        )
        self.assertEqual(
            eval_statuses([ProgressStatus.FAILED, ProgressStatus.DONE], final=False, issues_allowed=False),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FAILED, ProgressStatus.BLOCKED_BY_UNRESOLVED_DEPENDENCY], final=False, issues_allowed=True),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FAILED, ProgressStatus.BLOCKED_BY_UNRESOLVED_DEPENDENCY], final=False, issues_allowed=False),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FINISHED_WITH_ISSUES, ProgressStatus.BLOCKED_BY_UNRESOLVED_DEPENDENCY], final=False, issues_allowed=True),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FINISHED_WITH_ISSUES, ProgressStatus.BLOCKED_BY_UNRESOLVED_DEPENDENCY], final=False, issues_allowed=False),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FAILED, ProgressStatus.IN_PROGRESS], final=False, issues_allowed=True),
            ProgressStatus.IN_PROGRESS_WITH_ISSUES
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.FAILED, ProgressStatus.IN_PROGRESS], final=False, issues_allowed=False),
            ProgressStatus.FAILED
        )

        # Mixed Success with Warnings = DONE_WITH_WARNINGS
        self.assertEqual(
            eval_statuses([ProgressStatus.DONE, ProgressStatus.DONE_WITH_WARNINGS], final=False, issues_allowed=True),
            ProgressStatus.DONE_WITH_WARNINGS
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.DONE, ProgressStatus.DONE_WITH_WARNINGS], final=False, issues_allowed=False),
            ProgressStatus.DONE_WITH_WARNINGS
        )


        self.assertEqual(
            eval_statuses([ProgressStatus.DONE, ProgressStatus.IN_PROGRESS_WITH_ISSUES], final=False, issues_allowed=True),
            ProgressStatus.IN_PROGRESS_WITH_ISSUES # FINAL is evaluated first and all not finished finals are considered as FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.DONE, ProgressStatus.IN_PROGRESS_WITH_ISSUES], final=False, issues_allowed=False),
            ProgressStatus.FAILED
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.DONE, ProgressStatus.IN_PROGRESS_WITH_WARNINGS], final=False, issues_allowed=True),
            ProgressStatus.IN_PROGRESS_WITH_WARNINGS
        )

        self.assertEqual(
            eval_statuses([ProgressStatus.DONE, ProgressStatus.IN_PROGRESS_WITH_WARNINGS], final=False, issues_allowed=True),
            ProgressStatus.IN_PROGRESS_WITH_WARNINGS
        )



    def test_non_final_status_calculation(self):
        """Test non-final status calculation scenarios"""
        # Test in-progress with issues
        self.assertEqual(
            eval_statuses([ProgressStatus.IN_PROGRESS, ProgressStatus.FINISHED_WITH_ISSUES], issues_allowed=True),
            ProgressStatus.IN_PROGRESS_WITH_ISSUES
        )

        # Test in-progress with warnings
        self.assertEqual(
            eval_statuses([ProgressStatus.IN_PROGRESS, ProgressStatus.DONE_WITH_WARNINGS]),
            ProgressStatus.IN_PROGRESS_WITH_WARNINGS
        )

        # Test all not started
        self.assertEqual(
            eval_statuses([ProgressStatus.NOT_STARTED]),
            ProgressStatus.NOT_STARTED
        )

    def test_status_counts_input(self):
        """Test evaluation with StatusCounts input"""
        counts = StatusCounts()
        counts.add_status(ProgressStatus.IN_PROGRESS)
        counts.add_status(ProgressStatus.DONE_WITH_WARNINGS)
        
        self.assertEqual(
            eval_statuses(counts),
            ProgressStatus.IN_PROGRESS_WITH_WARNINGS
        )

    def test_issues_allowed_parameter(self):
        """Test issues_allowed parameter behavior"""
        statuses = [ProgressStatus.IN_PROGRESS, ProgressStatus.FINISHED_WITH_ISSUES]
        
        # With issues allowed
        self.assertEqual(
            eval_statuses(statuses, issues_allowed=True),
            ProgressStatus.IN_PROGRESS_WITH_ISSUES
        )
        
        # Without issues allowed
        self.assertEqual(
            eval_statuses(statuses, issues_allowed=False),
            ProgressStatus.FAILED
        )

    def test_edge_cases(self):
        """Test edge cases and complex combinations"""
        # Mix of everything
        complex_statuses = [
            ProgressStatus.DONE,
            ProgressStatus.IN_PROGRESS,
            ProgressStatus.FAILED,
            ProgressStatus.INTENTIONALLY_SKIPPED,
            ProgressStatus.DONE_WITH_WARNINGS
        ]
        
        # Non-final should show in-progress with issues
        self.assertEqual(
            eval_statuses(complex_statuses, final=False),
            ProgressStatus.IN_PROGRESS_WITH_ISSUES
        )
        
        # Final should show failed
        self.assertEqual(
            eval_statuses(complex_statuses, final=True),
            ProgressStatus.FAILED
        )

if __name__ == '__main__':
    unittest.main()
