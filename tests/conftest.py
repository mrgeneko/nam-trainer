import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Create mock modules before importing training_queue
mock_core = MagicMock()
mock_core.Architecture = MagicMock()
mock_core.Architecture.STANDARD = MagicMock()
mock_core.Architecture.STANDARD.value = "standard"

# Add mock paths to sys.modules
sys.modules['nam'] = MagicMock()
sys.modules['nam.train'] = MagicMock()
sys.modules['nam.train.core'] = mock_core
sys.modules['nam.models'] = MagicMock()
sys.modules['nam.models.metadata'] = MagicMock()
sys.modules['nam.models.metadata.GearType'] = MagicMock()
sys.modules['nam.models.metadata.ToneType'] = MagicMock()
