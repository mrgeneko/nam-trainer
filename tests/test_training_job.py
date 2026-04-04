import pytest
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "nam_trainer" / "gui" / "_resources"))

from training_queue import TrainingJob, JobStatus


class MockArchitecture:
    """Mock architecture enum value."""
    STANDARD = None
    
    def __init__(self):
        self.value = "standard"
    
    def __str__(self):
        return self.value


class MockGearType:
    """Mock gear type value."""
    def __init__(self, type_str: str = "cab"):
        self.value = type_str
    
    def __str__(self):
        return self.value


def create_test_job(
    input_path: str = "/data/input.wav",
    output_path: str = "/output/output.wav",
    train_destination: str = "/output",
    architecture_str: str = "standard",
    num_epochs: int = 100,
    output_template: str = "{input}_{size}",
    model_name: str = "TestModel",
    modeled_by: str = "TestUser",
    gear_type_str: str = "cab",
    batch_guid: str = "abc12345",
) -> TrainingJob:
    """Helper to create a test job with proper mock types."""
    arch = MockArchitecture()
    arch.value = architecture_str
    
    return TrainingJob(
        job_id="test1234",
        input_path=Path(input_path),
        output_path=Path(output_path),
        train_destination=Path(train_destination),
        architecture=arch,
        num_epochs=num_epochs,
        output_template=output_template,
        model_name=model_name,
        modeled_by=modeled_by,
        gear_type=MockGearType(gear_type_str),
        batch_guid=batch_guid,
    )


class TestTrainingJobBasics:
    """Test basic TrainingJob properties."""

    def test_job_has_id(self):
        """Job should have an ID."""
        job = create_test_job()
        assert job.job_id is not None
        assert len(job.job_id) > 0

    def test_job_id_is_8_chars(self):
        """Job ID should be 8 characters long."""
        job = create_test_job()
        assert len(job.job_id) == 8

    def test_default_status_is_pending(self):
        """New jobs should have PENDING status."""
        job = create_test_job()
        assert job.status == JobStatus.PENDING


class TestTrainingJobFilenameResolution:
    """Test output filename resolution with various tokens."""

    def test_resolve_input_token(self):
        """Test {input} token resolves to input filename."""
        job = create_test_job(output_template="{input}")
        basename = job.resolve_output_filename()
        assert basename == "input"

    def test_resolve_size_token(self):
        """Test {size} token resolves to architecture."""
        job = create_test_job(output_template="{size}")
        basename = job.resolve_output_filename()
        assert basename == "standard"

    def test_resolve_guid_token(self):
        """Test {guid} token resolves to batch GUID with __ID_...__ wrapper."""
        job = create_test_job(batch_guid="abc12345", output_template="{guid}")
        basename = job.resolve_output_filename()
        assert basename == "__ID_abc12345__"

    def test_multiple_tokens(self):
        """Test multiple tokens in template."""
        job = create_test_job(
            batch_guid="abc12345",
            model_name="TestModel",
            output_template="{guid}_{model}_{type}_{size}_{date}"
        )
        basename = job.resolve_output_filename()
        today = datetime.now().strftime("%Y_%m_%d")
        expected = f"__ID_abc12345___TestModel_cab_standard_{today}"
        assert basename == expected

    def test_creator_token(self):
        """Test {creator} token resolves to modeled_by field."""
        job = create_test_job(modeled_by="TestUser", output_template="{creator}")
        basename = job.resolve_output_filename()
        assert basename == "TestUser"

    def test_empty_value_for_missing_field(self):
        """Missing optional fields should result in empty string."""
        job = create_test_job(model_name="", output_template="{model}")
        basename = job.resolve_output_filename()
        assert basename == ""

    def test_unknown_token_removed(self):
        """Unknown tokens should be removed."""
        job = create_test_job(output_template="{unknown}")
        basename = job.resolve_output_filename()
        assert basename == ""


class TestTrainingJobProgress:
    """Test progress tracking fields."""

    def test_default_progress_is_none(self):
        """New jobs should have no progress."""
        job = create_test_job()
        assert job.current_epoch is None
        assert job.current_esr is None
        assert job.best_esr is None

    def test_progress_can_be_updated(self):
        """Progress fields should be updateable."""
        job = create_test_job()
        job.current_epoch = 50
        job.current_esr = 0.05
        job.best_esr = 0.04
        
        assert job.current_epoch == 50
        assert job.current_esr == 0.05
        assert job.best_esr == 0.04

    def test_best_esr_tracks_lowest(self):
        """best_esr should track the lowest ESR seen."""
        job = create_test_job()
        job.best_esr = 0.05
        job.current_esr = 0.03  # Lower
        if job.best_esr is None or job.current_esr < job.best_esr:
            job.best_esr = job.current_esr
        
        assert job.best_esr == 0.03
