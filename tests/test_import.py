"""Check the installed package import contract in a fresh Python process."""

import subprocess
import sys
import textwrap


def test_import_has_no_runtime_side_effects(tmp_path):
    probe = textwrap.dedent(
        """
        import importlib.util
        import os
        import sys

        spec = importlib.util.find_spec("crucible")
        assert spec is not None and spec.origin is not None
        allowed_reads = {spec.origin, importlib.util.cache_from_source(spec.origin)}
        write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND

        def audit(event, args):
            if event == "open":
                path, mode, flags = args
                assert path in allowed_reads, ("unexpected file read", path)
                assert not flags & write_flags, ("file write", path)
            if event == "import":
                assert args[0] == "crucible", ("runtime dependency import", args[0])
            assert not event.startswith(("socket.", "subprocess.")), event
            assert event not in {
                "os.mkdir", "os.remove", "os.rename", "os.rmdir", "os.system",
            }, event

        sys.addaudithook(audit)
        import crucible
        assert crucible.__file__ == spec.origin
        """
    )
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", probe],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""
    assert list(tmp_path.iterdir()) == []
