"""A timed-out private import must retain diagnostics without publishing a build."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.pck_mod import build


class FailedImportDiagnostics(unittest.TestCase):
    def test_partial_output_survives_timeout_and_temporary_stage_cleanup(self):
        for output in [b'Import stalled at poster.png\n', 'Import stalled at poster.png\n']:
            with self.subTest(output_type=type(output).__name__), tempfile.TemporaryDirectory() as tmp:
                log = Path(tmp) / 'import.log'
                failure = subprocess.TimeoutExpired(['godot'], 1, output=output)
                with patch.object(build.subprocess, 'run', side_effect=failure):
                    with self.assertRaises(build.BuildError) as raised:
                        build.run_godot('godot', tmp, ['--editor', '--import'], log)
                self.assertIn('Import stalled at poster.png', log.read_text())
                public_error = str(raised.exception)
            self.assertIn('Import stalled at poster.png', public_error)
            self.assertFalse(log.exists())


if __name__ == '__main__':
    unittest.main()
