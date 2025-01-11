import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from ipulse_shared_base_ftredge import ProgressStatus
from ipulse_shared_data_eng_ftredge.pipelines.pipelineflow import (
    calculate_overall_status,
    Dependency,
    DependencyType,
    Step,
    PipelineTask,
     PipelineTask, PipelineSequence, PipelineDynamicIterator, PipelineFlow,
    PipelineSequenceTemplate,
)

from ipulse_shared_base_ftredge import (
    Action, DataResource, DatasetScope, ProgressStatus
)

class TestOverallStatusCalculation(unittest.TestCase):
    """Test calculate_overall_status function"""

    def test_current_final_status_is_preserved(self):
        """Test that final current status is preserved"""
        counts = {
            'total_statuses': 3,
            'detailed': {'DONE': 2, 'IN_PROGRESS': 1},
            'by_category': {'pending_statuses': 1}
        }
        current = ProgressStatus.DONE
        result = calculate_overall_status(counts, current, final=False)
        self.assertEqual(result, ProgressStatus.DONE)

    def test_all_pending_with_issues_returns_failed_in_final(self):
        """Test pending + issues = FAILED in final mode"""
        counts = {
            'total_statuses': 2,
            'detailed': {'IN_PROGRESS': 1, 'FINISHED_WITH_ISSUES': 1},
            'by_category': {
                'pending_statuses': 1,
                'issue_statuses': 1
            }
        }
        result = calculate_overall_status(counts, None, final=True)
        self.assertEqual(result, ProgressStatus.FAILED)

    def test_all_not_started_returns_not_started(self):
        """Test all NOT_STARTED returns NOT_STARTED status"""
        counts = {
            'total_statuses': 2,
            'detailed': {'NOT_STARTED': 2},
            'by_category': {
                'pending_statuses': 2,
                'not_started_or_skipped_statuses': 2
            }
        }
        result = calculate_overall_status(counts, None, final=False)
        self.assertEqual(result, ProgressStatus.NOT_STARTED)

    def test_mixed_status_no_issues_returns_in_progress(self):
        """Test mixed statuses without issues returns IN_PROGRESS"""
        counts = {
            'total_statuses': 3,
            'detailed': {'DONE': 1, 'IN_PROGRESS': 1, 'NOT_STARTED': 1},
            'by_category': {
                'pending_statuses': 2,
                'not_started_or_skipped_statuses': 1
            }
        }
        result = calculate_overall_status(counts, None, final=False)
        self.assertEqual(result, ProgressStatus.IN_PROGRESS)

class TestDependency(unittest.TestCase):
    """Test Dependency class"""

    def setUp(self):
        self.mock_step = Mock()
        self.mock_step.status = ProgressStatus.DONE

    def test_default_dependency_creation(self):
        """Test default dependency creation"""
        dep = Dependency("step1")
        self.assertEqual(dep.step_name, "step1")
        self.assertEqual(dep.requirement, DependencyType.TO_SUCCESS_OR_SKIPPED)
        self.assertFalse(dep.optional)
        self.assertIsNone(dep.timeout_s)

    def test_custom_dependency_creation(self):
        """Test custom dependency creation"""
        dep = Dependency(
            "step1",
            requirement=DependencyType.TO_SUCCESS,
            optional=True,
            timeout_s=60
        )
        self.assertTrue(dep.optional)
        self.assertEqual(dep.timeout_s, 60)

    def test_timeout_checking(self):
        """Test timeout functionality"""
        dep = Dependency("step1", timeout_s=1)
        dep.start_timeout()
        self.assertFalse(dep.is_timeout())
        
        # Mock time passage
        dep._start_time = datetime.now() - timedelta(seconds=2)
        self.assertTrue(dep.is_timeout())

    def test_dependency_satisfaction_success(self):
        """Test dependency satisfaction with success status"""
        dep = Dependency("step1", requirement=DependencyType.TO_SUCCESS)
        self.mock_step.status = ProgressStatus.DONE
        self.assertTrue(dep.check_satisfied(self.mock_step))

    def test_dependency_satisfaction_failure(self):
        """Test dependency satisfaction with invalid status"""
        dep = Dependency("step1", requirement=DependencyType.TO_SUCCESS)
        self.mock_step.status = ProgressStatus.FAILED
        self.assertFalse(dep.check_satisfied(self.mock_step))

    def test_at_least_started_requirement(self):
        """Test TO_AT_LEAST_STARTED requirement"""
        dep = Dependency("step1", requirement=DependencyType.TO_AT_LEAST_STARTED)
        
        # Should pass
        self.mock_step.status = ProgressStatus.IN_PROGRESS
        self.assertTrue(dep.check_satisfied(self.mock_step))
        
        # Should fail
        self.mock_step.status = ProgressStatus.NOT_STARTED
        self.assertFalse(dep.check_satisfied(self.mock_step))

class TestStep(unittest.TestCase):
    """Test Step class"""

    def setUp(self):
        self.step = Step("test_step")
        self.mock_pipeline = Mock()
        # Fix: Set up get_step method on the mock pipeline
        self.mock_pipeline.get_step = Mock()
        self.step.pipeline_flow = self.mock_pipeline

    def test_step_creation(self):
        """Test basic step creation"""
        step = Step("test", disabled=True)
        self.assertEqual(step.name, "test")
        self.assertTrue(step.disabled)
        self.assertEqual(step.status, ProgressStatus.DISABLED)
        self.assertEqual(len(step.dependencies), 0)

    def test_step_with_dependencies(self):
        """Test step creation with dependencies"""
        deps = ["dep1", Dependency("dep2", optional=True)]
        step = Step("test", dependencies=deps)
        self.assertEqual(len(step.dependencies), 2)
        self.assertFalse(step.dependencies[0].optional)
        self.assertTrue(step.dependencies[1].optional)

    def test_validate_start_disabled(self):
        """Test validate_start with disabled step"""
        step = Step("test", disabled=True)
        # Fix: Set pipeline flow before validating
        step.pipeline_flow = self.mock_pipeline
        is_valid, reason = step.validate_and_start()
        self.assertFalse(is_valid)
        self.assertEqual(step.status, ProgressStatus.DISABLED)

    def test_validate_start_with_dependencies(self):
        """Test validate_start with dependencies"""
        mock_dep_step = Mock()
        mock_dep_step.status = ProgressStatus.DONE
        self.mock_pipeline.get_step.return_value = mock_dep_step

        step = Step("test", dependencies=["dep1"])
        # Fix: Set pipeline flow before validating
        step.pipeline_flow = self.mock_pipeline
        is_valid, _ = step.validate_and_start()
        self.assertTrue(is_valid)
        self.assertEqual(step.status, ProgressStatus.IN_PROGRESS)

    def test_validate_start_with_failed_dependency(self):
        """Test validate_start with failed dependency"""
        mock_dep_step = Mock()
        mock_dep_step.status = ProgressStatus.FAILED
        self.mock_pipeline.get_step.return_value = mock_dep_step

        step = Step("test", dependencies=[Dependency("dep1", DependencyType.TO_SUCCESS)])
        # Fix: Set pipeline flow before validating
        step.pipeline_flow = self.mock_pipeline
        is_valid, reason = step.validate_and_start()
        self.assertFalse(is_valid)
        self.assertEqual(step.status, ProgressStatus.BLOCKED_BY_UNRESOLVED_DEPENDENCY)

    # Add test for missing dependency
    def test_validate_start_with_missing_dependency(self):
        """Test validate_start with missing dependency"""
        self.mock_pipeline.get_step.side_effect = KeyError("Dependency not found")

        step = Step("test", dependencies=["missing_dep"])
        step.pipeline_flow = self.mock_pipeline
        is_valid, reason = step.validate_and_start()
        self.assertFalse(is_valid)
        self.assertEqual(step.status, ProgressStatus.BLOCKED_BY_UNRESOLVED_DEPENDENCY)
        self.assertIn("Missing dependency", reason)

    # Add test for already completed step
    def test_validate_start_already_completed(self):
        """Test validate_start with already completed step"""
        step = Step("test")
        step.pipeline_flow = self.mock_pipeline
        step.status = ProgressStatus.DONE
        is_valid, reason = step.validate_and_start()
        self.assertFalse(is_valid)
        self.assertIn("already completed", reason)

    # Add test for optional dependency
    def test_validate_start_with_optional_dependency(self):
        """Test validate_start with optional dependency"""
        mock_dep_step = Mock()
        mock_dep_step.status = ProgressStatus.FAILED
        self.mock_pipeline.get_step.return_value = mock_dep_step

        step = Step("test", dependencies=[
            Dependency("dep1", optional=True)
        ])
        step.pipeline_flow = self.mock_pipeline
        is_valid, _ = step.validate_and_start()
        self.assertTrue(is_valid)
        self.assertEqual(step.status, ProgressStatus.IN_PROGRESS)

    def test_status_transitions(self):
        """Test status transitions"""
        self.step.status = ProgressStatus.IN_PROGRESS
        self.assertEqual(self.step.status, ProgressStatus.IN_PROGRESS)
        
        self.step.add_warning("Warning")
        self.step.finalize()
        self.assertEqual(self.step.status, ProgressStatus.DONE_WITH_WARNINGS)

    def test_execution_tracking(self):
        """Test execution state tracking"""
        self.step.add_state("Started")
        self.step.add_warning("Warning 1")
        self.step.add_issue("Issue 1")
        self.step.add_notice("Notice 1")
        
        self.assertEqual(len(self.step.execution_state), 4)
        self.assertEqual(len(self.step.warnings), 1)
        self.assertEqual(len(self.step.issues), 1)
        self.assertEqual(len(self.step.notices), 1)

    def test_duration_tracking(self):
        """Test duration tracking"""
        self.step.validate_and_start()
        self.assertGreater(self.step.duration_s, 0)
        
        self.step.finalize()
        final_duration = self.step.duration_s
        self.assertGreater(final_duration, 0)

    def test_function_result_incorporation(self):
        """Test incorporating function results"""
        mock_result = Mock()
        mock_result.issues = ["Issue"]
        mock_result.warnings = ["Warning"]
        mock_result.notices = ["Notice"]
        mock_result.execution_state = ["State"]
        mock_result.results_aggregated = 1

        self.step.incorporate_function_result(mock_result)
        self.assertEqual(len(self.step.issues), 1)
        self.assertEqual(len(self.step.warnings), 1)
        self.assertEqual(len(self.step.notices), 1)
        self.assertEqual(self.step.results_aggregated, 2)  # Initial 1 + incorporated 1

####################################################################################################
#################################### TestPipelineTask ################################### 

class TestPipelineTask(unittest.TestCase):
    """Test PipelineTask class"""

    def setUp(self):
        self.task = PipelineTask(
            n="test_task",
            a=Action.EXECUTE,
            s=DataResource.DB,
            d=DataResource.FILE,
            scope=DatasetScope.FULL
        )
        self.mock_pipeline = Mock()
        self.mock_pipeline.get_step = Mock()
        self.task.pipeline_flow = self.mock_pipeline

    def test_task_creation(self):
        """Test task creation with all parameters"""
        self.assertEqual(self.task.name, "test_task")
        self.assertEqual(self.task.action, Action.EXECUTE)
        self.assertEqual(self.task.source, DataResource.DB)
        self.assertEqual(self.task.destination, DataResource.FILE)
        self.assertEqual(self.task.data_scope, DatasetScope.FULL)
        self.assertFalse(self.task.disabled)

    def test_task_execution_flow(self):
        """Test full task execution flow"""
        # Start task
        is_valid, _ = self.task.validate_and_start()
        self.assertTrue(is_valid)
        self.assertEqual(self.task.status, ProgressStatus.IN_PROGRESS)
        self.assertIsNotNone(self.task._start_time)

        # Add some execution data
        self.task.add_warning("Test warning")
        self.task.add_notice("Test notice")

        # Finalize task
        self.task.finalize()
        self.assertEqual(self.task.status, ProgressStatus.DONE_WITH_WARNINGS)
        self.assertGreater(self.task.duration_s, 0)

    def test_task_string_representation(self):
        """Test task string representation"""
        task_str = str(self.task)
        self.assertIn("test_task", task_str)
        self.assertIn(Action.EXECUTE.name, task_str)
        self.assertIn(DataResource.DB.name, task_str)
        self.assertIn(DataResource.FILE.name, task_str)

####################################################################################################
#################################### TestPipelineSequence ################################### 

class TestPipelineSequence(unittest.TestCase):
    """Test PipelineSequence class"""

    def setUp(self):
        self.task1 = PipelineTask("task1")
        self.task2 = PipelineTask("task2", dependencies=["task1"])
        self.template = PipelineSequenceTemplate([self.task1, self.task2])
        self.sequence = PipelineSequence("seq1", sequence_template=self.template)
        self.mock_pipeline = Mock()
        self.sequence.pipeline_flow = self.mock_pipeline

    def test_sequence_creation_from_template(self):
        """Test sequence creation from template"""
        self.assertEqual(len(self.sequence.steps), 2)
        self.assertIn("task1", self.sequence.steps)
        self.assertIn("task2", self.sequence.steps)

    def test_sequence_creation_from_steps(self):
        """Test sequence creation from direct steps"""
        sequence = PipelineSequence("seq2", steps=[self.task1, self.task2])
        self.assertEqual(len(sequence.steps), 2)
        self.assertIn("task1", sequence.steps)
        self.assertIn("task2", sequence.steps)

    def test_sequence_status_calculation(self):
        """Test sequence status calculation"""
        self.sequence.steps["task1"].status = ProgressStatus.DONE
        self.sequence.steps["task2"].status = ProgressStatus.IN_PROGRESS
        print("self.sequence.status",self.sequence.status)
        
        self.sequence.update_status_counts_and_overall_status(final=False)
        print("status_counts",self.sequence.status_counts)
        self.assertEqual(self.sequence.status, ProgressStatus.IN_PROGRESS)

        self.sequence.steps["task2"].status = ProgressStatus.DONE
        self.sequence.update_status_counts_and_overall_status(final=True)
        self.assertEqual(self.sequence.status, ProgressStatus.DONE)

####################################################################################################
#################################### TestPipelineDynamicIterator ################################### 

class TestPipelineDynamicIterator(unittest.TestCase):
    """Test PipelineDynamicIterator class"""

    def setUp(self):
        self.task1 = PipelineTask("task1")
        self.task2 = PipelineTask("task2", dependencies=["task1"])
        self.template = PipelineSequenceTemplate([self.task1, self.task2])
        self.iterator = PipelineDynamicIterator("test_iter", self.template)
        self.mock_pipeline = Mock()
        self.iterator.pipeline_flow = self.mock_pipeline

    def test_iterator_creation(self):
        """Test iterator creation"""
        self.assertEqual(self.iterator.name, "test_iter")
        self.assertEqual(self.iterator.total_iterations, 0)
        self.assertEqual(self.iterator.max_iterations, 100)

    def test_iteration_management(self):
        """Test adding and removing iterations"""
        # Add iterations
        self.iterator.set_iterations(["iter1", "iter2"])
        self.assertEqual(self.iterator.total_iterations, 2)
        
        # Add single iteration
        self.iterator.add_iteration("iter3")
        self.assertEqual(self.iterator.total_iterations, 3)
        
        # Remove iteration
        self.iterator.remove_iteration("iter2")
        self.assertEqual(self.iterator.total_iterations, 2)
        
        # Clear iterations
        self.iterator.clear_iterations()
        self.assertEqual(self.iterator.total_iterations, 0)

    def test_max_iterations_limit(self):
        """Test max iterations enforcement"""
        self.iterator.max_iterations = 2
        
        # Try to add more than max
        with self.assertRaises(ValueError):
            self.iterator.set_iterations(["iter1", "iter2", "iter3"])


####################################################################################################
#################################### TestPipelineFlow ################################### 

class TestPipelineFlow(unittest.TestCase):
    """Test PipelineFlow class"""

    def setUp(self):
        self.task1 = PipelineTask("task1")
        self.task2 = PipelineTask("task2", dependencies=["task1"])
        # Make the pipeline enabled instead of disabled
        self.flow = PipelineFlow("test_pipeline", steps=[self.task1, self.task2], disabled=False)
        self.flow.validate_and_start()

    def test_pipeline_creation(self):
        """Test pipeline creation"""
        self.assertEqual(self.flow.base_context, "test_pipeline")
        self.assertEqual(len(self.flow.steps), 2)
        self.assertEqual(self.flow._total_tasks, 2)

    def test_pipeline_task_completion(self):
        """Test task completion tracking"""
        self.assertEqual(self.flow.completion_percentage, 0)
        
        self.flow.update_task_completion(1)
        self.assertEqual(self.flow.completion_percentage, 50)
        
        self.flow.update_task_completion(1)
        self.assertEqual(self.flow.completion_percentage, 100)

    def test_dependency_validation(self):
        """Test dependency validation"""
        # Set up valid dependency chain
        self.task1.status = ProgressStatus.DONE
        self.task2.validate_and_start()
        self.assertEqual(self.task2.status, ProgressStatus.IN_PROGRESS)

        # Add task3 to the pipeline to ensure the circular dependency is recognized
        task3 = PipelineTask("task3", dependencies=["task2"])
        self.flow.add_step(task3)
        self.task1.dependencies = ["task3"]  # Create circular dependency
        
        with self.assertRaises(ValueError) as context:
            self.flow.validate_steps_dependencies_exist()
        self.assertIn("Circular dependency detected", str(context.exception))

    def test_pipeline_finalization(self):
        """Test pipeline finalization"""
        # Complete tasks
        self.task1.status = ProgressStatus.DONE
        self.task2.status = ProgressStatus.DONE_WITH_WARNINGS
        
        # Finalize pipeline
        self.flow.finalize()
        
        self.assertEqual(self.flow.status, ProgressStatus.DONE_WITH_WARNINGS)
        self.assertGreater(self.flow.duration_s, 0)

if __name__ == '__main__':
    unittest.main()
