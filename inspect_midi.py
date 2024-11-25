import typer
from mido import MidiFile

app = typer.Typer()

@app.command()
def analyze_midi(file: str):
    """
    Analyze a MIDI file and display its details.

    Args:
        file (str): Path to the MIDI file to analyze.
    """
    try:
        midi = MidiFile(file)
        
        # Display general MIDI file information
        typer.echo(f"Number of tracks: {len(midi.tracks)}")
        typer.echo(f"Ticks per beat: {midi.ticks_per_beat}")
        typer.echo(f"Length in seconds: {midi.length}")
        typer.echo(f"Type: {midi.type}")

        # Analyze each track
        for i, track in enumerate(midi.tracks):
            typer.echo(f"\nTrack {i}: {track.name}")
            for msg in track:
                typer.echo(msg)
    except FileNotFoundError:
        typer.echo(f"Error: File '{file}' not found.", err=True)
    except Exception as e:
        typer.echo(f"An error occurred: {e}", err=True)

if __name__ == "__main__":
    app()
