import pytest

from diff_pdf_visually import pdf_similar
from pathlib import Path

def diff(output: Path, expectation: Path):
    # Make sure that the expectation exists, else
    # copy the output and fail the test
    if not expectation.exists():
        with open(output, 'rb') as source_file:
            with open(expectation, 'wb') as destination_file:
                destination_file.write(source_file.read())
            pytest.fail("Treating the output as the generation. Run the test again.")

    if not pdf_similar(output, expectation):
        pytest.fail("The generated document is different than the expectation.")
