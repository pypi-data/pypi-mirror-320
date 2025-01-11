import pytest
import nanobindgen
from pathlib import Path
import difflib


def test_bindings():
    with (
        open("tests/input.h", "r") as f_in,
        open("tests/output/output.h", "w") as f_out,
        open("tests/expected_output.h", "r") as f_out_expected,
        open("tests/output/diff.diff", "w") as f_diff,
    ):
        source_code = f_in.read()
        binding = nanobindgen.build_header("input", source_code)

        f_out.write(binding)

        expected_binding = f_out_expected.read()

        diff = difflib.unified_diff(
            expected_binding.splitlines(),
            binding.splitlines(),
            fromfile="tests/expected_output.h",
            tofile="tests/output.h",
            lineterm="",
        )

        f_diff.write("\n".join(diff))

    assert binding == expected_binding
