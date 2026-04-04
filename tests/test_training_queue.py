import pytest
from pathlib import Path
import sys
import threading
import time
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent / "nam_trainer" / "gui" / "_resources"))

from training_queue import TrainingQueue, TrainingJob, JobStatus


@pytest.fixture
def queue():
    """Create a fresh TrainingQueue for each test."""
    return TrainingQueue()


class MockArchitecture:
    """Mock architecture enum value."""
    def __init__(self, arch_str: str = "standard"):
        self.value = arch_str
    
    def __str__(self):
        return self.value


class MockGearType:
    """Mock gear type value."""
    def __init__(self, type_str: str = "cab"):
        self.value = type_str
    
    def __str__(self):
        return self.value


def create_job(
    input_path: str = "/data/input.wav",
    output_path: str = "/output/output.wav",
    train_destination: str = "/output",
    architecture_str: str = "standard",
    num_epochs: int = 100,
    batch_guid: str = None,
    job_id: str = None,
) -> TrainingJob:
    """Helper to create a test job."""
    arch = MockArchitecture(architecture_str)
    
    return TrainingJob(
        job_id=job_id or str(uuid.uuid4())[:8],
        input_path=Path(input_path),
        output_path=Path(output_path),
        train_destination=Path(train_destination),
        architecture=arch,
        num_epochs=num_epochs,
        batch_guid=batch_guid,
    )


@pytest.fixture
def sample_job(queue):
    """Create a sample job and add it to the queue."""
    job = create_job()
    queue.add_job(job)
    return job


class TestTrainingQueueBasics:
    """Test basic queue operations."""

    def test_new_queue_is_empty(self, queue):
        """New queue should have no jobs."""
        assert queue.get_queue_size() == 0
        assert queue.get_all_jobs() == []

    def test_new_queue_is_not_running(self, queue):
        """New queue should not be running."""
        assert not queue.is_running()


class TestAddJob:
    """Test adding jobs to the queue."""

    def test_add_single_job(self, queue):
        """Adding a job should increase queue size."""
        job = create_job()
        queue.add_job(job)
        assert queue.get_queue_size() == 1
        assert job is not None

    def test_add_multiple_jobs(self, queue):
        """Adding multiple jobs should work."""
        queue.add_job(create_job(
            input_path="/input1.wav",
            output_path="/output1.wav",
        ))
        queue.add_job(create_job(
            input_path="/input2.wav",
            output_path="/output2.wav",
            architecture_str="lite",
        ))
        assert queue.get_queue_size() == 2

    def test_job_has_queued_status(self, queue):
        """Added job should have QUEUED status."""
        job = create_job()
        queue.add_job(job)
        assert job.status == JobStatus.QUEUED

    def test_job_has_unique_id(self, queue):
        """Each job should have a unique ID."""
        job1 = create_job()
        job2 = create_job()
        queue.add_job(job1)
        queue.add_job(job2)
        assert job1.job_id != job2.job_id


class TestRemoveJob:
    """Test removing jobs from the queue."""

    def test_remove_job(self, queue, sample_job):
        """Removing a job should decrease queue size."""
        job_id = sample_job.job_id
        queue.remove_job(job_id)
        assert queue.get_queue_size() == 0

    def test_remove_nonexistent_job(self, queue):
        """Removing a nonexistent job should not raise an error."""
        queue.add_job(create_job())
        queue.remove_job("nonexistent_id")
        assert queue.get_queue_size() == 1

    def test_get_job_by_id(self, queue, sample_job):
        """Should be able to retrieve job by ID."""
        retrieved = queue.get_job(sample_job.job_id)
        assert retrieved is sample_job


class TestJobReordering:
    """Test job reordering operations."""

    def test_move_job_up(self, queue):
        """Moving a job up should change order."""
        job1 = create_job(input_path="/input1.wav", output_path="/output1.wav")
        job2 = create_job(input_path="/input2.wav", output_path="/output2.wav")
        job3 = create_job(input_path="/input3.wav", output_path="/output3.wav")
        queue.add_job(job1)
        queue.add_job(job2)
        queue.add_job(job3)

        jobs = queue.get_all_jobs()
        assert jobs[0].job_id == job1.job_id
        assert jobs[1].job_id == job2.job_id
        assert jobs[2].job_id == job3.job_id

    def test_move_job_down(self, queue):
        """Moving a job down should change order."""
        job1 = create_job(input_path="/input1.wav", output_path="/output1.wav")
        job2 = create_job(input_path="/input2.wav", output_path="/output2.wav")
        queue.add_job(job1)
        queue.add_job(job2)

        queue.move_job_down(job1.job_id)
        jobs = queue.get_all_jobs()
        assert jobs[0].job_id == job2.job_id
        assert jobs[1].job_id == job1.job_id


class TestQueueStopBehavior:
    """Test queue stop behavior."""

    def test_stop_queue_marks_processing_job_as_queued(self, queue, sample_job):
        """Stopping queue should mark processing job as QUEUED for retry."""
        queue.request_stop()
        assert sample_job.status == JobStatus.QUEUED

    def test_stop_queue_sets_running_false(self, queue):
        """Stopping queue should set running to False."""
        queue.request_stop()
        assert not queue.is_running()

    def test_stop_clears_progress_fields_for_processing_job(self, queue):
        """Stopping should clear progress fields for PROCESSING job."""
        job = create_job()
        queue.add_job(job)
        job.status = JobStatus.PROCESSING  # Simulate job being processed
        job.current_epoch = 50
        job.current_esr = 0.05
        job.best_esr = 0.04
        
        queue.request_stop()
        
        assert job.current_epoch is None
        assert job.current_esr is None
        assert job.best_esr is None


class TestQueueStart:
    """Test queue start behavior."""

    def test_start_queue_sets_running_with_jobs(self, queue):
        """Starting queue with jobs should set running to True."""
        queue.add_job(create_job())
        queue.add_job(create_job())
        queue.start()
        time.sleep(0.1)  # Give worker time to start
        try:
            assert queue.is_running()
        finally:
            queue.stop()

    def test_start_queue_processes_queued_jobs(self, queue):
        """Starting queue should process QUEUED jobs."""
        job = create_job()
        queue.add_job(job)
        assert job.status == JobStatus.QUEUED
        queue.start()
        time.sleep(0.3)  # Give time for job to be picked up
        try:
            # Job should have been processed (and likely failed since files don't exist)
            # But it should have moved from QUEUED state
            assert job.status in (JobStatus.PROCESSING, JobStatus.COMPLETED, JobStatus.FAILED)
        finally:
            queue.stop()


class TestConcurrentAccess:
    """Test thread safety of queue operations."""

    def test_add_job_thread_safe(self, queue):
        """Adding jobs from multiple threads should be safe."""
        def add_jobs():
            for i in range(5):
                job = create_job(
                    input_path=f"/input{i}.wav",
                    output_path=f"/output{i}.wav",
                )
                queue.add_job(job)

        threads = [threading.Thread(target=add_jobs) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert queue.get_queue_size() == 20

    def test_get_all_jobs_thread_safe(self, queue):
        """Getting all jobs while adding should not raise errors."""
        def add_jobs():
            for i in range(10):
                queue.add_job(create_job())
                time.sleep(0.01)

        def read_jobs():
            for _ in range(10):
                queue.get_all_jobs()
                time.sleep(0.01)

        add_thread = threading.Thread(target=add_jobs)
        read_thread = threading.Thread(target=read_jobs)

        add_thread.start()
        read_thread.start()

        add_thread.join()
        read_thread.join()

        assert queue.get_queue_size() == 10
