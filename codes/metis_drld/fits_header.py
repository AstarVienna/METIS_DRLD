"""Fits Headers."""

import dataclasses


@dataclasses.dataclass
class FitsHeader:
    parameter: str
    hidden: str
    range: str
    label: str

    @staticmethod
    def from_wiki_line(line):
        _, parameter, hidden, therange, label, _ = [cell.strip() for cell in line.split("|")]
        return FitsHeader(
            parameter=parameter,
            hidden=hidden,
            range=therange,
            label=label,
        )
