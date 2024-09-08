from pathlib import Path
import pytest
from typer.testing import CliRunner

from add_staves.main import app
from tests.helpers import diff

runner = CliRunner()

def test_scale_down(request):
    """
    Tests that the individual systems are correctly scaled down
    to fit into the width of a DIN A4 page.
    """
    input = Path(request.config.rootdir / "tests/input/test_scale_down.pdf")
    output = Path(request.config.rootdir / "tests/output/test_scale_down.pdf")
    expectation = Path(request.config.rootdir / "tests/expectation/test_scale_down.pdf")

    result = runner.invoke(app, ["--output=" + str(output), str(input)])
    assert result.exit_code == 0

    # Diff the output with the expectation
    diff(output, expectation)


def test_zwerg_stream(request):
    """
    Tests the output of the systems as a stream (not split into multiple pages).
    """
    input = Path(request.config.rootdir / "tests/input/test_zwerg.pdf")
    output = Path(request.config.rootdir / "tests/output/test_zwerg_stream.pdf")
    expectation = Path(request.config.rootdir / "tests/expectation/test_zwerg_stream.pdf")

    result = runner.invoke(app, ["--output=" + str(output), "-c='0'", str(input)])
    assert result.exit_code == 0

    # Diff the output with the expectation
    diff(output, expectation)


def test_zwerg_a4(request):
    """
    Tests the output of the systems when they are split into multiple DIN A4 pages.
    """
    input = Path(request.config.rootdir / "tests/input/test_zwerg.pdf")
    output = Path(request.config.rootdir / "tests/output/test_zwerg_a4.pdf")
    expectation = Path(request.config.rootdir / "tests/expectation/test_zwerg_a4.pdf")

    result = runner.invoke(app, ["--output=" + str(output), str(input)])
    assert result.exit_code == 0

    # Diff the output with the expectation
    diff(output, expectation)


def test_zwerg_a4_ragged_bottom(request):
    """
    Tests the output of the system when they are split into multiple DIN A4 pages
    and the option ragged-bottom is set.
    """
    input = Path(request.config.rootdir / "tests/input/test_zwerg.pdf")
    output = Path(request.config.rootdir / "tests/output/test_zwerg_a4_ragged_bottom.pdf")
    expectation = Path(request.config.rootdir / "tests/expectation/test_zwerg_a4_ragged_bottom.pdf")

    result = runner.invoke(app, ["--output=" + str(output), "--ragged-bottom", str(input)])
    assert result.exit_code == 0

    # Diff the output with the expectation
    diff(output, expectation)

    
def test_wagner_träume(request):
    """
    Test
    """
    input = Path(request.config.rootdir / "tests/input/test_wagner_träume.pdf")
    output = Path(request.config.rootdir / "tests/output/test_wagner_träume.pdf")
    expectation = Path(request.config.rootdir / "tests/expectation/test_wagner_träume.pdf")

    result = runner.invoke(app, ["--output=" + str(output), str(input)])
    assert result.exit_code == 0

    diff(output, expectation)
