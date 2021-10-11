
standard_ranges = {
    # Strings
    'Violin': [55, 103],
    'Viola': [48, 91],
    'Double Bass': [28, 67],
    'Cello': [36, 76],
    'Bass Guitar': [28, 67],
    'Acoustic Guitar': [40, 88],

    #Brass
    'Tuba': [28, 58],
    'Bass Trombone': [34, 67],
    'French Horn': [34, 77],
    'Trombone': [40, 72],
    'Trumpet': [55, 82],

    #Woodwinds
    'Piccolo': [74, 102],
    #'Flute': [60, 96],
    'Oboe': [58, 91],
    'Alto Flute': [55, 91],
    'Cor Anglais (English Horn)': [52, 81],
    #'Clarinet': [50, 94],
    'Bass Clarinet': [38, 77],
    'Bassoon': [34, 75],
    'Contrabassoon': [22, 53],
    'Soprano Recorder': [72, 98],
    'Alto Recorder': [65, 91],
    'Tenor Recorder': [60, 86],
    'Bass Recorder': [53, 79],
    'Baritone Sax': [36, 69],
    'Tenor Sax': [44, 76],
    'Alto Sax': [49, 81],
    'Soprano Sax': [56, 88],

    #Tuned Percussion
    'Glockenspiel': [79, 108],
    'Xylophone': [65, 108],
    'Vibraphone': [53, 89],
    'Marimba': [45, 96],
    'Bass Marimba': [33, 81],
    'Celeste': [60, 108],
    'Tubular Bells': [60, 77],
    'Timpani': [40, 55],
    'Harpsichord': [29, 89],
    'Harp': [24, 103],

    # VSCO:
    'Flute':  [55, 88],
    'Clarinet': [50,  84],
}




Kontakt_ranges = {

}
Kontakt_channels = {
    'Chords'
}



SINE_ranges = {
    'Full Orchestra': [],
}
SINE_channels = {
    'Chords Maj Sustain': 0,
    'Chords Min Sustain': 1,
    'Chords Sus4 Sustain': 2,
    'Chords Maj Staccato': 3,
    'Chords Min Staccato': 4,
    'Chords Sus4 Staccato': 5,
    'Sustains Low Unison': 6,
    'Staccato Low Unison': 7,
}

# Versillian Chamber orcestra.
# does weird stuff with changing articulation. (yellow keys as a trigger)
Sketch_ranges = {
    'Cello section': [36, 79],
    'Double Bass': [24, 60],
    'Double Bass 2': [36, 58],
    'Viola section': [48, 88],

    'Violin':[67, 112],
    'Violin 1':[67, 102],
    'Violin 2':[76, 100],
    'Violin 3':[67, 90],
    'Violin section': [67, 101],
}
Sketch_channels = {
    'Chords': '',
}

VSCO_channels = {
    # Note that these are the values that the VST uses.
    # Python MISI uses 0-15 instead of 1-16.
    'Flue':     1,
    'Clarinet': 2,
    'Bassoon':  3,
    'Horn':     4,
    'Trumpet':  5,
    'Tenor Bone': 6,
    'Bass Bone': 7,
    'Timpani':  8,
    'Xylophone': 8,
    'Chimes':   9,
    'Glockenspiel': 9,
    'Orchestral percussion': 10,
    'Harp':     11,
    'Violin':   12,
    'Violin section': 13,
    'Piano':    14,
}

# Different vst's have different ranges and instruments.
VSCO_ranges = {
    'Flute':  [55, 88],
    'Clarinet': [50,  84],
    'Bassoon': [36, ],
    'Horn': 4,
    'Trumpet': 5,
    'Tenor Bone': 6,
    'Bass Bone': 7,
    'Timpani': 8,
    'Xylophone': 8,
    'Chimes': 9,
    'Glockenspiel': 9,
    'Orchestral percussion': 10,
    'Harp': 11,
    'Violin': 12,
    'Violin section': 13,
    'Piano': 14,
}


instrument_range = {'VSCO': VSCO_ranges, 'sketch':Sketch_ranges,}
instrument_channels = {'VSCO': {instrument: channel -1 for instrument, channel in VSCO_channels.items()}}



#		Drum MIDI:
#		Bass  	KeyNum	Sound	 	Treble  	KeyNum	Sound
#		A_	33	Metronome Click
#		B_b	34	Metronome Bell
#		B_	35	Acoustic Bass Drum
#		C	36	Bass Drum 1	 	C	60	Hi Bongo
#		C#	37	Side Stick	 	C#	61	Low Bongo#
#		D	38	Acoustic Snare	 	D	62	Mute Hi Conga
#		Eb	39	Hand Clap	 	D#	63	Open Hi C#onga
#		E	40	Electric Snare	 	E	64	Low Conga
#		F	41	Low Floor Tom	 	F	65	High Timbale
#		F#	42	Closed Hi-Hat	 	F#	66	Low Timbale
#		G	43	High Floor Tom	 	G	67	High Agogo
#		G#	44	Pedal Hi-Hat	 	G#	68	Low Agogo
#		A	45	Low Tom	 	A	69	Cabasa
#		Bb	46	Open Hi-Hat	 	Bb	70	Maracas
#		Bn	47	Low-Mid Tom	 	Bn	71	Short Whistle
#		c	48	Hi-Mid Tom	 	c	72	Long Whistle
#		c#	49	Crash Cymbal 1	 	c#	73	Short Guiro
#		d	50	High Tom	 	d	74	Long Guiro
#		eb	51	Ride Cymbal 1	 	d#	75	Claves
#		e	52	Chinese Cymbal	 	e	76	Hi Wood Block
#		f	53	Ride Bell	 	f	77	Low Wood Block
#		f#	54	Tambourine	 	f#	78	Mute Cuica
#		g	55	Splash Cymbal	 	g	79	Open Cuica
#		g#	56	Cowbell	 	g#	80	Mute Triangle
#		a	57	Crash Cymbal 2	 	a	81	Open Triangle
#		bb	58	Vibraslap	 		82
#		bn	59	Ride Cymbal 2	 		83


def create_chord_list():
    """
    Force data into a set of specific scales.
    """
    reference_keys = {
        'C': 0, 'C#': 1, 'Db': 1,
        'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'E#': 5, 'Fb': 4,
        'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10,
        'B': 11, 'B#': 0, 'Cb': 11
    }

    Chords = {
          # Single note:
          '_tonic': [0, ],
          # Chords (no underscore)
          '5': [0, 7 ],
          'maj' : [0, 4, 7, ],
          'maj/1b':[1, 4, 7, 12, 16, 19,],
          'min' : [0, 3, 7, ],
          'dim' : [0, 3, 6],
          'maj6': [0, 4, 7, 9, 11],
          'min6': [0, 3, 7, 9, 11],
          'maj7': [0, 4, 7, 11],
          'min7': [0, 3, 7, 10],
          'maj9': [0, 2, 4, 7, 11],
          'min9': [0, 2, 3, 7, 10],
          'maj11': [0, 2, 4, 5, 7, 11],
          'min11': [0, 2, 3, 5, 7, 10],
          'min7(b5)' : [0, 3, 6, 10],
          '7': [0, 4, 7, 10],
          '7(#9)':  [0, 4, 7, 10, 15, 19, 23],
          '9' : [0,  4, 7, 14, 19, 23],
          'min9' : [0,  3, 7, 14, 19, 23],
          # Scales (underscores)
          '_major': [0, 2, 4, 5, 7, 9, 11, ],
          '_major_pentatonic': [0, 2, 4, 7, 9, ],
          '_major_pentatonic7': [0, 2, 4, 7, 9, 11 ],
          '_7': [0, 2, 4, 5, 7, 9, 10, ],
          '_minor': [0, 2, 3, 5, 7, 8, 11, 12],
          '_minor_7': [0, 2, 3, 5, 7, 8, 10, 12],
          '_minor_natural': [0, 2, 3, 5, 7, 8, 10, 12],
          '_minor_harmonic': [0, 2, 3, 5, 7, 8, 11, 12],
          '_minor_harmonic': [0, 2, 3, 5, 7, 9, 11, 12],
          '_minor_pentatonic': [0, 3, 5, 6, 7, 10, ],
          '_minor_pentatonic9': [0, 2, 3, 5, 7, 10, ],
          '_minor_pentatonic_blues9': [0, 2, 3, 5, 6, 7, 10, 11 ],
      }

	# Add slash chords
	# for chord, values in Chords.items():
 	# 	for num in np.arange(0,12,1):
 	# 		new_chord = chord+'/'+str(num)
 	# 		Chords[new_chord] = values[:]
 	# 		Chords[new_chord].append(num)
 	# 		# print(new_chord, values, num, '->', Chords[new_chord])

	# Add all generic chords combinatorially:
    notes_in_chord = {}
    for key, reference in reference_keys.items():
        for chord, values in Chords.items():

            #if chord == 'min':
            #    print('making dict:', key,reference, chord, values)
            #octave_width = 12
            #if max(values)>12: octave_width = 24
            #if max(values)>24: octave_width = 36
            #values = [(v + reference)%octave_width for v in values]
            notes_in_chord[''.join([key, chord])] = [(v + reference)%12 for v in values]
            #if chord == 'min':
            #    print('making dict:', key,reference, chord, values, notes_in_chord[''.join([key, chord])])
	#Specific chords:
	#notes_in_chord['C#ocmaj7'] = [0, 1, 4, 7, 11,]

	# Add all notes to the list of acceptable notes.
    all_notes = {}
    all_notes['Chromatic'] = list(range(-1,129))
    for scale, scale_notes in notes_in_chord.items():
        notes = []
        octave_width = 12

        #if max(scale_notes) > 12:
        #    octave_width = 24

        for pitch in all_notes['Chromatic']:
            if pitch % octave_width in scale_notes:
                notes.append(pitch)
            all_notes[scale] = notes

    return all_notes
chord_dict = create_chord_list()


def pitch_to_named_note(pitch):
    """
    Convert pitch to a named note (ie is 60 is C5)
    """
    reference_keys = {
        'C': 0, 'C#': 1,
        'D': 2, 'Eb': 3,
        'E': 4,
        'F': 5, 'F#': 6,
        'G': 7, 'Ab': 8,
        'A': 9, 'Bb': 10,
        'B': 11,
    }
    pitch_keys = {v:n for n, v in reference_keys.items()}
    note = pitch_keys[pitch%12]
    octave = str(int(pitch/12))
    return note+octave
