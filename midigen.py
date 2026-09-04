import json
from mido import Message, MidiFile, MidiTrack, MetaMessage

# Load the JSON data
with open('OrangeChairs', 'r') as f:
    data = json.load(f)

bpm = data['project_metadata']['bpm']

def parse_single_pitch(pitch_str):
    """Parses a single note string like 'D1', 'A#1', 'Bb1' into a MIDI note number."""
    name_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    
    note_name = pitch_str[0].upper()
    accidental = 0
    octave_str_idx = 1
    
    if len(pitch_str) > 1 and pitch_str[1] in ('b', '#'):
        if pitch_str[1] == 'b':
            accidental = -1
        elif pitch_str[1] == '#':
            accidental = 1
        octave_str_idx = 2
        
    octave = int(pitch_str[octave_str_idx:])
    base_note = 12 * (octave + 1)
    return base_note + name_map.get(note_name, 0) + accidental

def parse_pitch(pitch_field):
    """Handles both single notes and hyphen-separated chord strings as specified in technical notes."""
    if '-' in pitch_field:
        return [parse_single_pitch(p.strip()) for p in pitch_field.split('-')]
    else:
        return [parse_single_pitch(pitch_field.strip())]

def duration_to_ticks(duration_str, tpb):
    """Converts a duration string like '4b' or '0.5b' into ticks."""
    val = float(duration_str.lower().replace('b', ''))
    return int(val * tpb)

def create_midi():
    tpb = 480  # Standard MIDI resolution
    
    for track_data in data['tracks']:
        mid = MidiFile(ticks_per_beat=tpb)
        track = MidiTrack()
        mid.tracks.append(track)
        
        # Set tempo metadata (microseconds per quarter note)
        microseconds_per_beat = int(60000000 / bpm)
        track.append(MetaMessage('set_tempo', tempo=microseconds_per_beat, time=0))
        
        events = []
        
        for note in track_data['notes']:
            start_ticks = int(note['time'] * tpb)
            dur_ticks = duration_to_ticks(note['duration'], tpb)
            midi_pitches = parse_pitch(note['pitch'])
            velocity = note['velocity']
            
            for midi_pitch in midi_pitches:
                events.append((start_ticks, 'note_on', midi_pitch, velocity))
                events.append((start_ticks + dur_ticks, 'note_off', midi_pitch, 0))
            
        # Sort events by absolute tick time; note_offs processed before note_ons at identical ticks
        events.sort(key=lambda x: (x[0], 0 if x[1] == 'note_off' else 1))
        
        last_tick = 0
        for abs_tick, msg_type, pitch, vel in events:
            delta = abs_tick - last_tick
            track.append(Message(msg_type, note=pitch, velocity=vel, time=delta))
            last_tick = abs_tick
            
        # Sanitize track name for filesystem safety
        safe_name = "".join(c for c in track_data['track_name'] if c.isalnum() or c in (' ', '_', '-')).strip()
        filename = f"{safe_name}.mid"
        mid.save(filename)
        print(f"Successfully generated: {filename}")

if __name__ == "__main__":
    create_midi()