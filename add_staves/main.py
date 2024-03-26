import os
import re
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Annotated, List, Optional, Tuple

import typer
from pypdf import PageObject, PaperSize, PdfReader, PdfWriter
from rich import print

# The CLI app
app = typer.Typer(rich_markup_mode="rich", add_completion=False)

# The version of the tool
# needs to be updated manually
__version__ = "0.2.3"


@dataclass
class PageLayout:
    """
    Convenience class that wraps the page configuration options
    so that they can be easily passed around.
    """

    top_margin: int
    bottom_margin: int
    top_padding: int
    bottom_padding: int
    stave_height: float
    ragged_bottom: bool
    ragged_bottom_last: bool
    minimum_height: float = PaperSize.A4.height
    left_margin: int = 30
    right_margin: int = 30

    def calculate_stave_height(self) -> float:
        return self.stave_height + self.bottom_padding + self.top_padding

    @property
    def printable_width(self) -> float:
        """
        Calculates the width of the printable area.
        """
        return PaperSize.A4.width - self.left_margin - self.right_margin


def version_callback(value: bool):
    if value:
        print(f"add-staves: {__version__}")
        raise typer.Exit()


def output_callback(ctx: typer.Context, input: Optional[Path]) -> Path:
    """
    Callback for the output option in 'run' that creates a
    default output path if none was provided:

    path/to/score.pdf -> path/to/score-analysis.pdf

    Creating the default path can fail in case a file
    with this name already exists. Providing the '--force'-flag
    allows overwriting of this file.
    """
    if input is None:
        score = Path(ctx.params["score"])
        path = score.parent / (score.stem + "-analysis.pdf")
        if path.exists() and not ctx.params["force"]:
            print(
                "[red]A file at the default path [bright_white]'%s'[/] already exists. Please provide an explicit output path with the [green bold]'-o'[/] option or force overwriting with the [green bold]'-f'[/] flag.[/]"
                % path
            )
            raise typer.Exit(1)
        return path
    else:
        return input


def groups_parser(input: Optional[str]) -> Optional[List[int]]:
    """
    Parse a string of comma-separated or space-separated
    numbers into a list of integers.

    This will default to an empty list if an error occurs.
    """
    if input is None:
        return None

    try:
        numbers = [int(num) for num in input.split(",")]
    except:
        numbers = []

    try:
        numbers = [int(num) for num in re.split(r"\s+", input)]
    except:
        pass

    return numbers if all(num > 0 for num in numbers) else []


# def groups_callback(ctx: typer.Context, input: Optional[List[int]]) -> Optional[List[int]]:
def groups_callback(score: PdfReader, groups: Optional[List[int]]) -> Optional[List[int]]:
    """
    🚨 No access to the score argument in the params.

    If no combining flag (input is None) is given, the tool tries to fit as
    many systems as possible on a DIN A4 page.

    If, however the option is used – be it empty or incomplete –
    the tool disregards the DIN A4 size constraint and respects
    as much input as possible:

    1. The user provides an empty string: Everything will end up
       on one page.

    2. The sum of the groupings is less than the total page count:
       The remaining pages will be output on one page.

    3. The sum of the grouping is more than the total page count:
       The overflow will be discarded.
    """
    if groups is None:
        return None

    # number of pages in total
    page_count = len(score.pages)

    # sum of total grouped pages
    grouped_pages_count = sum(groups)

    if sum(groups) == 0:
        return [page_count]
    elif grouped_pages_count < page_count:
        return groups + [page_count - grouped_pages_count]
    elif grouped_pages_count > page_count:
        while sum(groups) > page_count:
            groups.pop()
        else:
            return groups + [page_count - sum(groups)]
    else:
        return groups


def staves_parser(staves_count: int) -> PageObject:
    """
    Fetches the correct empty staves pdf from the resources.

    Valid counts are 0...6
    """
    staves_path = os.path.join(
        os.path.dirname(__file__), "resources", "empty-%d.pdf" % int(staves_count)
    )
    return PdfReader(staves_path).pages[0]


def calculate_min_height(systems: List[PageObject], page_layout: PageLayout) -> float:
    """
    Calculate the minimum height necessary to fit all systems
    plus staves and whitespace on one page.
    """
    return (
        reduce(
            lambda x, y: x + y, list(map(lambda system: system.cropbox.height, systems)), 0
        )
        + page_layout.top_margin
        + page_layout.bottom_margin
        + len(systems)
        * (page_layout.stave_height + page_layout.top_padding + page_layout.bottom_padding)
    )


def layout_systems(
    systems: List[PageObject],
    staves: PageObject,
    writer: PdfWriter,
    page_layout: PageLayout,
    is_last_page: bool
):
    """
    Layout the systems with the empty staves on a new blank
    page in the writer.

    Dynamically adjust the paddings if the total space needed
    is less than a DIN A4 page as long as the flag `ragged_bottom`
    is set.

    Respect the flag `ragged_bottom_last` to not adjust the paddings
    if set.
    """
    # minimum height necessary to layout all elements
    minimum_height = calculate_min_height(systems, page_layout)

    # flag to dynamically layout the elements
    # true if minimus_height is smaller and `ragged_bottom` is not set
    dynamic_layout = True \
    if minimum_height < PaperSize.A4.height and not page_layout.ragged_bottom \
    else False

    # Overwrite dynamic_layout in case it is the last page
    if is_last_page:
        dynamic_layout = True \
        if minimum_height < PaperSize.A4.height and not page_layout.ragged_bottom_last \
        else False

    # property height that represents the current level
    # to which the page is filled
    # it counts down from minimum_height -> zero
    height = (
        minimum_height
        if minimum_height > page_layout.minimum_height
        else page_layout.minimum_height
    )

    # the page to which to "# print" the elements
    current_page = writer.add_blank_page(PaperSize.A4.width, height)

    # insert the top_margin
    height -= page_layout.top_margin

    # space that needs to be dynamically allocated
    # this is only interesting if the flag dynamic_layout is set
    dynamic_spacing = (
        page_layout.minimum_height
        - minimum_height
        - page_layout.bottom_margin
        - page_layout.top_margin
        if dynamic_layout
        else 0
    )

    # calculate the additional_bottom_padding
    additional_bottom_padding = dynamic_spacing / (3 * len(systems))
    if additional_bottom_padding > 30:
        additional_bottom_padding = 30

    # remove the sum of the additional_bottom_paddings from the dynamic_spacing
    dynamic_spacing -= additional_bottom_padding * len(systems)

    # calculate the additional_top_padding
    additional_top_padding = dynamic_spacing / len(systems)

    # iterate over the systems and add them to the current_page
    for system in systems:
        # add the system
        current_page.merge_translated_page(
            system,
            # layout ends up beeing too far to the right
            # (PaperSize.A4.width - system.cropbox.width) / 2,
            0,
            height - system.cropbox.top
        )
        height -= system.cropbox.height

        # add bottom_padding
        # dynamic_layout ? 1/3 up to max 30
        height -= page_layout.bottom_padding + additional_bottom_padding

        # add staves
        current_page.merge_translated_page(
            staves,
            (PaperSize.A4.width - staves.cropbox.width) / 2,
            height - staves.cropbox.height,
        )
        height -= staves.cropbox.height

        # add top_padding
        # dynamic_layout ? increase 2/3 or rest
        height -= page_layout.top_padding + additional_top_padding


@app.command(rich_help_panel=True)
def run(
    # Arguments
    score: Annotated[
        Path,
        typer.Argument(
            metavar="SCORE",
            help="Path to the cropped score.",
            show_default=False,
            exists=True,
            readable=True,
        ),
    ],
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            show_default=False,
            help="Show the current version number.",
        ),
    ] = None,
    # Options
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite the output destination if it exists.",
            is_flag=True,
        ),
    ] = False,
    # Configuration
    groups: Annotated[
        Optional[str],
        typer.Option(
            "--combining",
            "-c",
            metavar="TEXT",
            rich_help_panel="Configuration",
            help="Groups of systems combined on one page as space- or comma-seperated text.",
            parser=groups_parser,
            # callback=groups_callback,
        ),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            metavar="PATH",
            help="Path to the output file. [bright_black]\\[default: <score>-analysis.pdf][/]",
            rich_help_panel="Configuration",
            file_okay=True,
            show_default=False,
            callback=output_callback,
        ),
    ] = None,
    staves: Annotated[
        int,
        typer.Option(
            "--staves",
            "-s",
            min=0,
            max=6,
            clamp=True,
            help="Number of staves to add (0...6).",
            metavar="NUMBER",
            rich_help_panel="Configuration",
            parser=staves_parser,
        ),
    ] = 2,
    # Page Layout
    top_margin: Annotated[
        int,
        typer.Option(
            rich_help_panel="Page Layout",
            help="Configure the margin at the top of the page.",
            min=0,
            clamp=True,
            metavar="NUMBER",
        ),
    ] = 30,
    bottom_margin: Annotated[
        int,
        typer.Option(
            rich_help_panel="Page Layout",
            help="Configure the margin at the bottom of the page.",
            min=0,
            clamp=True,
            metavar="NUMBER",
        ),
    ] = 30,
    top_padding: Annotated[
        int,
        typer.Option(
            rich_help_panel="Page Layout",
            help="Configure the padding above a system.",
            min=0,
            clamp=True,
            metavar="NUMBER",
        ),
    ] = 30,
    bottom_padding: Annotated[
        int,
        typer.Option(
            rich_help_panel="Page Layout",
            help="Configure the padding beneath a system.",
            min=0,
            clamp=True,
            metavar="NUMBER",
        ),
    ] = 10,
    ragged_bottom: Annotated[
        bool,
        typer.Option(
            rich_help_panel="Page Layout",
            help="If this is set, systems will be set at their natural spacing to fit the page.",
            is_flag=True
        )
    ] = False,
    ragged_bottom_last: Annotated[
        bool,
        typer.Option(
            rich_help_panel="Page Layout",
            help="If this is set, systems on the last page will be set at their natural spacing to fit the page.",
            is_flag=True
        )
    ] = True,
):
    """
    Add analytical staves to a score.

    ---------------------------------

    The tool will treat each page of the provided score as one unit
    under which it will add empty staves. Therefore use an external
    tool (e.g. '[link=https://briss.sourceforge.net/]briss[/link]') to separate the score into the desired units.

    By default, the tool tries to fit as many systems (plus their staves)
    as possible on one DIN A4 page. This behaviour can be overridden, by
    providing a comma- or space-separated list of numbers, declaring
    how many pages to group together. This is especially useful, if you
    want to keep the page numbers of the original score:

    Given a 2-page score of which the first page consists of 4 systems
    and the second of 5 system, the command to keep this grouping is:

    [green bold]add-staves my-score.pdf --combining "4 5"[/]

    Take note of the option [green]--combining "4 5"[/]. This tells the
    tool to combine the first 4 and then the next 5 pages on a single page.
    Note, that a page will never be smaller than a DIN A4 page.
    """
    # read the score pdf
    score = PdfReader(score)

    # clean the groups
    groups = groups_callback(score, groups)

    # create the PageLayout class
    page_layout = PageLayout(
        top_margin=top_margin,
        bottom_margin=bottom_margin,
        top_padding=top_padding,
        bottom_padding=bottom_padding,
        ragged_bottom=ragged_bottom,
        ragged_bottom_last=ragged_bottom_last,
        stave_height=staves.cropbox.height
    )

    # the PdfWriter to build the output file
    writer = PdfWriter()

    if groups is None:
        # Fit systems on A4 page
        height = page_layout.top_margin + page_layout.bottom_margin

        current_group_size = 0
        groups = []
        for system in score.pages:
            # Scale the system if it exceeds the width of a DIN A4 page
            if system.cropbox.width > page_layout.printable_width:
                system.scale_by(page_layout.printable_width / system.cropbox.width)

            new_height = system.cropbox.height
            new_height += page_layout.calculate_stave_height()

            if height + new_height <= page_layout.minimum_height:
                current_group_size += 1
                height += new_height
            elif height + new_height > page_layout.minimum_height and current_group_size == 0:
                groups.append(1)
                height = page_layout.top_margin + page_layout.bottom_margin
            else:
                groups.append(current_group_size)
                height = page_layout.top_margin + page_layout.bottom_margin
                current_group_size = 1

    groups = groups_callback(score, groups)

    # keep track of the current system (= a page in the input score)
    current_system_number = 0

    # the count of the groups
    groups_count = len(groups)

    # Follow the groupings
    for index, group in enumerate(groups):
        # get all the systems for this group
        systems = [
            score.pages[index]
            for index in range(current_system_number, current_system_number + group)
        ]

        # increase the page number
        current_system_number += group

        # layout the systems
        layout_systems(
            systems,
            staves,
            writer,
            page_layout,
            True if index == groups_count - 1 else False
         )

    # write to disk
    print(output)
    with open(output, "wb") as fp:
        writer.write(fp)
