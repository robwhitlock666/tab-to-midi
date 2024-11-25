import mido
from mido import MidiFile, MidiTrack, Message

# Define drum mapping to MIDI notes
DRUM_MAPPING = {
    'C': 49,  # Crash Cymbal
    'H': 42,  # Closed Hi-Hat
    'S': 38,  # Snare Drum
    'T': 45,  # Tom (Mid-Tom as default, can be customized)
    'B': 36   # Bass Drum
}

# Function to parse ASCII tabs and generate MIDI track
def parse_tabs_to_midi(ascii_tabs, bpm=120, include_ghost_notes=True):
    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)

    # Add tempo meta message
    microseconds_per_beat = int(60000000 / bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=microseconds_per_beat))

    # Calculate time per 16th note
    ticks_per_beat = midi.ticks_per_beat
    time_per_16th_note = ticks_per_beat // 4

    # Split input into lines and measures
    lines = ascii_tabs.strip().split('\n')
    rows = {line[0]: line.split('|')[1:-1] for line in lines}

    # Get the number of measures
    measure_count = len(rows[next(iter(rows))])

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
            if simultaneous_notes:
                track.append(Message('note_off', note=0, velocity=0, time=time_per_16th_note))
            else:
                # Add a rest (no notes played)
                track.append(Message('note_on', note=0, velocity=0, time=time_per_16th_note))

    return midi

# Example usage
ascii_tabs = """
C|----------------|o-----------o---|------------o---|----------------|
H|x-x-x-x-x-x-x-x-|x-x-x-x-x-x-x-x-|x-x-x-x-x-x-x-x-|x-x-x-x-x-x-x-x-|
S|oo-o-o-o-o-oooog|----o-------o---|----o-------o---|----o-------oo--|
T|----------------|----------------|----------------|--------------oo|
B|----------------|oo-o-o-o-o------|oo-o-o-o-o------|oo-o-o-o-o------|
"""

# Parse and save the MIDI file
midi = parse_tabs_to_midi(ascii_tabs, bpm=120, include_ghost_notes=True)
output_file = 'drum_tabs_correct_timing.mid'
midi.save(output_file)  # Save the MIDI file with corrected timing
print(f"MIDI file saved to {output_file}")
