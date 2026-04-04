import json
import os
import tempfile
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "nam_trainer" / "gui" / "_resources"))

from config import _DEFAULTS, load, save, get, set


@pytest.fixture
def temp_config_dir(monkeypatch):
    """Create a temporary config directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        monkeypatch.setattr("config._CONFIG_DIR", tmppath)
        monkeypatch.setattr("config._CONFIG_FILE", tmppath / "settings.json")
        yield tmppath


class TestConfigDefaults:
    """Test default configuration values."""

    def test_defaults_exist(self):
        """Verify all expected default keys exist."""
        expected_keys = [
            "default_architectures",
            "output_template",
            "dry_path",
            "wet_path",
            "default_destination",
            "model_name",
            "modeled_by",
            "gear_type",
            "gear_make",
            "gear_model",
            "tone_type",
            "input_level_dbu",
            "output_level_dbu",
        ]
        for key in expected_keys:
            assert key in _DEFAULTS, f"Missing default key: {key}"

    def test_default_architectures_is_list(self):
        """Default architectures should be a list."""
        assert isinstance(_DEFAULTS["default_architectures"], list)

    def test_default_output_template(self):
        """Default output template should be a non-empty string."""
        assert isinstance(_DEFAULTS["output_template"], str)
        assert len(_DEFAULTS["output_template"]) > 0


class TestConfigLoad:
    """Test configuration loading."""

    def test_load_returns_defaults_when_no_file(self, temp_config_dir):
        """Load should return defaults when config file doesn't exist."""
        config = load()
        for key, value in _DEFAULTS.items():
            assert config[key] == value

    def test_load_returns_saved_values(self, temp_config_dir):
        """Load should return previously saved values."""
        test_settings = {
            "dry_path": "/path/to/dry.wav",
            "wet_path": "/path/to/wet.wav",
            "model_name": "Test Model",
        }
        save(test_settings)
        
        config = load()
        assert config["dry_path"] == "/path/to/dry.wav"
        assert config["wet_path"] == "/path/to/wet.wav"
        assert config["model_name"] == "Test Model"

    def test_load_merges_with_defaults(self, temp_config_dir):
        """Load should merge saved values with defaults."""
        partial_settings = {"dry_path": "/custom/path"}
        save(partial_settings)
        
        config = load()
        assert config["dry_path"] == "/custom/path"
        assert config["model_name"] == _DEFAULTS["model_name"]


class TestConfigSave:
    """Test configuration saving."""

    def test_save_creates_file(self, temp_config_dir):
        """Save should create the config file."""
        save({"model_name": "Test"})
        assert (temp_config_dir / "settings.json").exists()

    def test_save_writes_valid_json(self, temp_config_dir):
        """Save should write valid JSON."""
        test_settings = {"dry_path": "/test/path"}
        save(test_settings)
        
        with open(temp_config_dir / "settings.json") as f:
            data = json.load(f)
        assert data["dry_path"] == "/test/path"


class TestConfigGetSet:
    """Test individual get/set operations."""

    def test_get_returns_default_when_missing(self, temp_config_dir):
        """Get should return default value for missing keys."""
        value = get("nonexistent_key", "default_value")
        assert value == "default_value"

    def test_set_updates_config(self, temp_config_dir):
        """Set should update a single config value."""
        set("model_name", "New Name")
        config = load()
        assert config["model_name"] == "New Name"

    def test_set_preserves_other_values(self, temp_config_dir):
        """Set should preserve other config values."""
        save({"model_name": "Original", "dry_path": "/original"})
        set("model_name", "Updated")
        
        config = load()
        assert config["model_name"] == "Updated"
        assert config["dry_path"] == "/original"
