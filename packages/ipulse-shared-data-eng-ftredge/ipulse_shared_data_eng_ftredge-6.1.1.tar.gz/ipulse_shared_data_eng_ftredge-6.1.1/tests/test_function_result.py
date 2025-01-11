import unittest
import time
import json
from ipulse_shared_base_ftredge import ProgressStatus, evaluate_combined_progress_status
from ipulse_shared_data_eng_ftredge import FunctionResult

class TestFunctionResult(unittest.TestCase):
    def setUp(self):
        self.result = FunctionResult(name="Test function")

    def test_initialization(self):
        """Test default initialization"""
        self.assertEqual(self.result.name, "Test function")
        self.assertEqual(self.result.overall_status, ProgressStatus.IN_PROGRESS)
        self.assertEqual(self.result.results_aggregated, 1)
        self.assertIsNone(self.result.data)
        self.assertEqual(len(self.result.execution_state), 0)
        self.assertIsNotNone(self.result.start_time)
        self.assertEqual(self.result.duration_s, 0.0)

    def test_data_management(self):
        """Test data property and methods"""
        # Test simple data assignment
        test_data = {"key": "value"}
        self.result.data = test_data
        self.assertEqual(self.result.data, test_data)

        # Test add_data method
        self.result.data = {}  # Start with empty dict
        self.result.add_data(values=["item1", "item2"], name="list_data")
        self.assertEqual(self.result.data["list_data"], ["item1", "item2"])

        # Test add_data with invalid initial data type
        self.result.data = "string"
        with self.assertRaises(ValueError):
            self.result.add_data(values=[1,2,3], name="numbers")

    def test_status_management(self):
        """Test status handling and transitions"""
        # Test direct status assignment
        self.result.overall_status = ProgressStatus.DONE
        self.assertEqual(self.result.overall_status, ProgressStatus.DONE)

        # Test string status assignment
        self.result.overall_status = "FAILED"
        self.assertEqual(self.result.overall_status, ProgressStatus.FAILED)

        self.result.overall_status = "FAIL"
        self.assertEqual(self.result.overall_status, ProgressStatus.UNKNOWN)

        # Test final() method with different scenarios
        # 1. Final with issues
        self.result = FunctionResult()
        self.result.add_issue("Test issue")
        self.result.final()
        self.assertEqual(self.result.overall_status, ProgressStatus.FINISHED_WITH_ISSUES)

        # 2. Final with warnings
        self.result = FunctionResult()
        self.result.add_warning("Test warning")
        self.result.final()
        self.assertEqual(self.result.overall_status, ProgressStatus.DONE_WITH_WARNINGS)

        # 3. Final with notices
        self.result = FunctionResult()
        self.result.add_notice("Test notice")
        self.result.final()
        self.assertEqual(self.result.overall_status, ProgressStatus.DONE_WITH_NOTICES)

        # 4. Clean completion
        self.result = FunctionResult()
        self.result.final()
        self.assertEqual(self.result.overall_status, ProgressStatus.DONE)

        self.result = FunctionResult()
        self.result.add_issue("Test issue")
        self.result.final(ProgressStatus.DONE)
        self.assertEqual(self.result.overall_status, ProgressStatus.DONE)

    def test_execution_state_tracking(self):
        """Test execution state management"""
        self.result.add_state("Started function")
        self.result.add_state("Processing")
        self.result.add_state("Completed")

        # Check state entries
        self.assertEqual(len(self.result.execution_state), 3)
        
        # Verify timestamp format in state entries
        for state in self.result.execution_state:
            self.assertRegex(state, r"\[t:.*\]--.*")

        # Check string representation
        state_str = self.result.execution_state_str
        self.assertIn("Started function", state_str)
        self.assertIn("Processing", state_str)
        self.assertIn("Completed", state_str)

    def test_issues_warnings_notices(self):
        """Test adding and retrieving issues, warnings, and notices"""
        # Test issues
        self.result.add_issue("Critical error")
        self.result.add_issue("Data corruption")
        self.assertEqual(len(self.result.issues), 2)
        self.assertIn("Critical error", self.result.issues_str)

        # Test warnings
        self.result.add_warning("Performance degradation")
        self.assertEqual(len(self.result.warnings), 1)
        self.assertIn("Performance degradation", self.result.warnings_str)

        # Test notices
        self.result.add_notice("Process completed")
        self.assertEqual(len(self.result.notices), 1)
        self.assertIn("Process completed", self.result.notices_str)

        # Test combined notes
        notes = self.result.get_notes()
        self.assertIn("ISSUES", notes)
        self.assertIn("WARNINGS", notes)
        self.assertIn("NOTICES", notes)

    def test_metadata_management(self):
        """Test metadata handling"""
        # Test direct assignment
        test_metadata = {"source": "test", "version": "1.0"}
        self.result.metadata = test_metadata
        self.assertEqual(self.result.metadata, test_metadata)

        # Test add_metadata method
        self.result.add_metadata(new_field="value", another_field=123)
        self.assertEqual(self.result.metadata["new_field"], "value")
        self.assertEqual(self.result.metadata["another_field"], 123)


    def test_duration_calculation(self):
        """Test duration calculation functionality"""
        result = FunctionResult()
        time.sleep(0.1)
        
        # Test duration before calculation
        self.assertEqual(result.duration_s, 0.0)
        
        # Test duration after manual calculation
        result.calculate_duration()
        self.assertGreater(result.duration_s, 0.0)
        
        # Test duration after final
        result = FunctionResult()
        time.sleep(0.1)
        result.final()
        self.assertGreater(result.duration_s, 0.0)
        
        # Test duration accurate to milliseconds
        duration_ms = result.duration_s * 1000
        self.assertGreater(duration_ms, 100)  # Should be at least 100ms


    def test_results_aggregated_counting(self):
        """Test results aggregated counting functionality"""
        self.assertEqual(self.result.results_aggregated, 1)
        
        # Test increment
        self.result.increment_results_aggregated(2)
        self.assertEqual(self.result.results_aggregated, 3)

        # Test direct setting
        self.result.results_aggregated = 5
        self.assertEqual(self.result.results_aggregated, 5)

    def test_normal_result_integration(self):
        """Test integrating child function results"""
        # Create child result
        child_result = FunctionResult()
        child_result.add_warning("Child warning")
        child_result.add_issue("Child issue")
        child_result.add_notice("Child notice")
        child_result.add_metadata(child_specific_meta="value")
        child_result.data = {"child_data": "value"}
        child_result.final(status=ProgressStatus.DONE_WITH_WARNINGS)

        # Test integration with default settings (skip_data=True, skip_metadata=True)
        self.result.integrate_result(child_result=child_result,combine_status=True)
        self.assertEqual(len(self.result.warnings), 1)
        self.assertEqual(len(self.result.issues), 1)
        self.assertEqual(len(self.result.notices), 1)
        self.assertIsNone(self.result.data)  # Data should be skipped
        self.assertEqual(len(self.result.metadata), 0)  # Metadata should be skipped

        # Test integration with data and metadata
        self.result = FunctionResult()  # Fresh instance
        self.result.integrate_result(child_result, skip_data=False, skip_metadata=False)
        self.assertEqual(self.result.data, {"child_data": "value"})
        self.assertEqual(self.result.metadata["child_specific_meta"], "value")

    def test_not_combined_status_integration(self):
            # Test status combination in Combine not Forced and child didn't have issues
            child_result = FunctionResult()
            child_result.final(status=ProgressStatus.FAILED)
            self.result.integrate_result(child_result, combine_status=False)
            self.assertEqual(self.result.overall_status, ProgressStatus.IN_PROGRESS)
            self.result.final()
            self.assertEqual(self.result.overall_status, ProgressStatus.DONE)

    def test_not_combined_status_integration_with_issues(self):
            # Test status combination in Combine not Forced and child had issues
            child_result = FunctionResult()
            child_result.add_issue("Child issue 3")
            child_result.final(status=ProgressStatus.FAILED)
            self.result.integrate_result(child_result, combine_status=False)
            self.assertEqual(self.result.overall_status, ProgressStatus.IN_PROGRESS)
            self.result.final()
            self.assertEqual(self.result.overall_status, ProgressStatus.FINISHED_WITH_ISSUES)


    def test_status_aggregation(self):
        """Test status aggregation logic"""
        # Test priority ordering
        status_pairs = [
            (ProgressStatus.DONE, ProgressStatus.FAILED),  # FAILED should win
            (ProgressStatus.DONE_WITH_NOTICES, ProgressStatus.DONE_WITH_WARNINGS),  # WARNINGS should win
            (ProgressStatus.IN_PROGRESS, ProgressStatus.DONE),  # IN_PROGRESS should win
            (ProgressStatus.CANCELLED, ProgressStatus.FAILED),  # FAILED should win
        ]

        for status1, status2 in status_pairs:
            result = evaluate_combined_progress_status([status1, status2])
            self.assertEqual(result, max(status1, status2, key=lambda x: x.value))

    def test_serialization(self):
        """Test dictionary and string serialization"""
        # Prepare a result with various data
        self.result.add_state("Started")
        self.result.add_warning("Test warning")
        self.result.add_metadata(test_key="test_value")
        self.result.data = {"test": "data"}

        # Test to_dict()
        result_dict = self.result.to_dict(exclude_none=False)
        self.assertIn("data", result_dict)
        self.assertIn("status", result_dict)
        self.assertIn("overall_status", result_dict["status"])
        self.assertIn("execution_state", result_dict["status"])

        # Test str representation
        result_str = str(self.result)
        self.assertIn("overall_status", result_str)
        self.assertIn("name", result_str)

        # Test info property
        info = self.result.get_status_info(exclude_none=False)
        self.assertIsInstance(info, str)
        self.assertIn("test_key", info)

    def test_exclude_none_behavior(self):
        """Test exclude_none behavior in various methods"""
        result = FunctionResult()
        
        # Test with empty states
        self.assertIsNone(result.execution_state_str)
        self.assertIsNone(result.issues_str)
        self.assertIsNone(result.warnings_str)
        self.assertIsNone(result.notices_str)
        
        # Test get_notes() with empty states
        self.assertEqual(result.get_notes(), "")
        
        # Add some data
        result.add_issue("Test issue")
        result.add_warning(None)  # Should not be included
        
        # Test get_notes() with exclude_none=True (default)
        notes = result.get_notes()
        self.assertIn("ISSUES", notes)
        self.assertNotIn("WARNINGS", notes)
        
        # Test get_status_info with exclude_none=True
        info_dict = json.loads(result.get_status_info())
        self.assertIn("issues", info_dict)
        self.assertNotIn("warnings", info_dict)
        
        # Test with exclude_none=False
        info_dict = json.loads(result.get_status_info(exclude_none=False))
        self.assertIn("warnings", info_dict)
        self.assertIsNone(info_dict["warnings"])

    def test_metadata_management_extended(self):
        """Test extended metadata management functionality"""
        result = FunctionResult()
        
        # Test add_metadata_from_dict
        metadata_dict = {
            "key1": "value1",
            "key2": None,  # Should be included
            "key3": {"nested": "value"}
        }
        result.add_metadata_from_dict(metadata_dict)
        self.assertEqual(result.metadata["key1"], "value1")
        self.assertIsNone(result.metadata["key2"])
        self.assertEqual(result.metadata["key3"]["nested"], "value")
        
        # Test metadata merging
        result.add_metadata(key4="value4")
        self.assertEqual(len(result.metadata), 4)
        
        # Test metadata in to_dict
        dict_result = result.to_dict(exclude_none=True)
        self.assertIn("key1", json.loads(dict_result["status"]["metadata"]))

    def test_name_management(self):
        """Test name property management"""
        result = FunctionResult()
        
        # Test default name is UUID
        self.assertIsNotNone(result.name)
        self.assertTrue(len(result.name) > 0)
        
        # Test name setting
        test_name = "test_function_001"
        result.name = test_name
        self.assertEqual(result.name, test_name)
        
        # Test name appears in status info
        self.assertIn(test_name, result.get_status_info())

    def test_status_transitions(self):
        """Test complex status transitions and final states"""
        result = FunctionResult()
        
        # Test transition with issues and forced status
        result.add_issue("Critical error")
        result.final(status=ProgressStatus.DONE, force_if_closed=True)
        self.assertEqual(result.overall_status, ProgressStatus.DONE)
        
        # Test can't change status when closed without force
        result.final(status=ProgressStatus.FAILED, force_if_closed=False)
        self.assertEqual(result.overall_status, ProgressStatus.DONE)
        self.assertTrue(any("already closed" in w for w in result.notices))

        
        
        # Test invalid status handling
        with self.assertRaises(ValueError):
            result = FunctionResult()
            result.final(status="INVALID_STATUS")
            
        # Test status resolution order
        result = FunctionResult()
        result.add_issue("issue")
        result.add_warning("warning")
        result.add_notice("notice")
        result.final()  # Should resolve to FINISHED_WITH_ISSUES due to priority
        self.assertEqual(result.overall_status, ProgressStatus.FINISHED_WITH_ISSUES)

    def test_complex_integration_scenarios(self):
        """Test complex integration scenarios between function results"""
        parent = FunctionResult()
        child1 = FunctionResult()
        child2 = FunctionResult()
        
        # Setup different states
        child1.add_warning("Warning in child1")
        child1.final(status=ProgressStatus.DONE_WITH_WARNINGS)
        
        child2.add_issue("Error in child2")
        child2.data = {"child2_data": "value"}
        child2.final(status=ProgressStatus.FAILED)
        
        # Test integration with status combination
        parent.integrate_result(child1)
        self.assertEqual(parent.overall_status, ProgressStatus.IN_PROGRESS)
        
        parent.integrate_result(child2)
        self.assertEqual(parent.overall_status, ProgressStatus.FAILED)
        
        # Verify aggregation counts
        self.assertEqual(parent.results_aggregated, 3)  # parent + 2 children
        
        # Test data handling in integration
        self.assertIsNone(parent.data)  # Should be None due to skip_data=True
        
        # Test full integration
        parent = FunctionResult()
        parent.data = {"parent_data": "value"}
        parent.integrate_result(child2, skip_data=False, skip_metadata=False)
        self.assertIn("child2_data", parent.data)
        self.assertEqual(parent.results_aggregated, 2)



if __name__ == '__main__':
    unittest.main()