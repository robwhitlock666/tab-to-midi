import mido
from mido import MidiFile, MidiTrack, Message
import typer
from pathlib import Path

# Define drum mapping to MIDI notes
DRUM_MAPPING = {
    'C': 49,  # Crash Cymbal
    'H': 42,  # Closed Hi-Hat
    'S': 38,  # Snare Drum
    'T': 45,  # Tom
    'B': 36   # Bass Drum
}

app = typer.Typer()


def parse_split_tabs_to_midi(split_tabs: str, bpm=120, include_ghost_notes=True) -> MidiFile:
    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)

    # Add tempo meta message
    microseconds_per_beat = int(60000000 / bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=microseconds_per_beat))

    # Calculate time per 16th note
    ticks_per_beat = midi.ticks_per_beat
    time_per_16th_note = ticks_per_beat // 4

    # Parse the split tabs
    lines = split_tabs.strip().split('\n')
    grouped_measures = []
    current_group = []

    for line in lines:
        if line.strip() == "":
            if current_group:
                grouped_measures.append(current_group)
                current_group = []
        else:
            current_group.append(line)

    if current_group:
        grouped_measures.append(current_group)

    # Build rows for each drum from grouped measures
    rows = {drum: [] for drum in DRUM_MAPPING.keys()}

    for group in grouped_measures:
        for line in group:
            if line[0] in DRUM_MAPPING:
                rows[line[0]].extend(line[2:].split('|')[:-1])

    # Determine the number of measures
    measure_count = len(rows[next(iter(rows.keys()))])

    # Parse each measure and beat
    for measure_idx in range(measure_count):
        for beat_idx in range(16):  # 16 beats per measure
            simultaneous_notes = []
            for instrument, measures in rows.items():
                if instrument not in DRUM_MAPPING:
                    continue
                note = DRUM_MAPPING[instrument]
                char = measures[measure_idx][beat_idx]
                if char == 'g' and include_ghost_notes:  # Ghost note
                    simultaneous_notes.append((note, 30))  # Soft velocity for ghost notes
                elif char in {'x', 'o'}:  # Regular hit
                    simultaneous_notes.append((note, 100))  # Normal velocity

            # Add all simultaneous notes
            for note, velocity in simultaneous_notes:
                track.append(Message('note_on', note=note, velocity=velocity, time=0))

            # Add the correct delay after processing all notes
            track.append(Message('note_off', note=0, velocity=0, time=time_per_16th_note))

    return midi


@app.command()
def parse(input_tab: str, output_midi: str):
    """
    Parse a split tab file into a MIDI file.
    """
    split_tabs = Path(input_tab).read_text()
    midi = parse_split_tabs_to_midi(split_tabs, bpm=120, include_ghost_notes=True)
    midi.save(output_midi)
    print(f"MIDI file saved to {output_midi}")


if __name__ == "__main__":
    app()
