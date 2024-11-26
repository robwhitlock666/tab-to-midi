from dataclasses import dataclass, field
import re
import typer

app = typer.Typer()

@dataclass
class Measure:
    """
    Represents a single measure containing arrays for each drum.
    """
    C: str = "-" * 16
    H: str = "-" * 16
    S: str = "-" * 16
    T: str = "-" * 16
    B: str = "-" * 16

    def as_lines(self) -> list[str]:
        """
        Returns the measure as formatted lines for output.
        """
        return [
            f"C|{self.C}|",
            f"H|{self.H}|",
            f"S|{self.S}|",
            f"T|{self.T}|",
            f"B|{self.B}|"
        ]

def parse_tabs(lines: list[str]) -> tuple[list[Measure], list[str]]:
    """
    Parse the tab lines and annotations, converting them into Measures.
    """
    measures = []
    annotations = []

    current_measures = {"C": [], "H": [], "S": [], "T": [], "B": []}
    for line in lines:
        if "Play x" in line:
            annotations.append(line.strip())
        elif re.match(r"^[CHSTB]\|", line):
            part = line[0]  # C, H, S, T, or B
            hits = line[2:].split('|')[:-1]
            current_measures[part].extend(hits)
        elif line.strip() == "":
            # End of a measure group; build complete measures
            while len(current_measures["C"]) > 0:
                measures.append(
                    Measure(
                        C=current_measures["C"].pop(0),
                        H=current_measures["H"].pop(0) if current_measures["H"] else "-" * 16,
                        S=current_measures["S"].pop(0) if current_measures["S"] else "-" * 16,
                        T=current_measures["T"].pop(0) if current_measures["T"] else "-" * 16,
                        B=current_measures["B"].pop(0) if current_measures["B"] else "-" * 16,
                    )
                )

    return measures, annotations

def expand_measures(measures: list[Measure], annotations: list[str]) -> list[Measure]:
    """
    Expand measures based on annotations like 'Play xN'.
    """
    expanded_measures = []
    for idx, measure in enumerate(measures):
        repetitions = 1  # Default is 1 if no annotation applies
        if annotations:
            annotation = annotations[min(idx, len(annotations) - 1)]
            match = re.search(r"Play x(\d+)", annotation)
            if match:
                repetitions = int(match.group(1))
        expanded_measures.extend([measure] * repetitions)
    return expanded_measures

@app.command()
def process_tabs(input_file: str, output_file: str):
    """
    Process a tab file, ensuring all measures are properly formatted
    and all drums are included even if missing in the input.
    """
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Parse input into measures and annotations
    measures, annotations = parse_tabs(lines)

    # Expand measures based on annotations
    expanded_measures = expand_measures(measures, annotations)

    # Write the expanded measures to the output file
    with open(output_file, 'w') as file:
        for measure in expanded_measures:
            file.writelines("\n".join(measure.as_lines()) + "\n\n")

if __name__ == "__main__":
    app()
