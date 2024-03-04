
from midiutil.MidiFile import MIDIFile
import os
import platform


def folder(name):
    """ This snippet takes a string, makes the folder and the string.
        It also accepts lists of strings.
    """
    if isinstance(name, list):
        name='/'.join(name)
    if name[-1] != '/':
        name = ''.join([name, '/'])
    if not os.path.exists(name):
        os.makedirs(name)
        #print('makedirs ', name)
    return name


def symlink(source, link_name):
    if platform.system().lower().find('cygwin') > -1:
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        if csl(link_name, source, flags) == 0:
            raise ctypes.WinError()
    else:
        os_symlink = getattr(os, "symlink", None)
        if callable(os_symlink):
            os_symlink(source, link_name)



class midinote:
    def __init__(self, track=0, channel=0, pitch=0, time=0, duration=0, volume=0):
        self.track = track
        self.channel = channel
        self.pitch = pitch
        self.time = time
        self.duration = duration
        self.volume = volume

def save_midi(title, tempo, tracks, path):
        """
        Saving the miodi file.
        The tracks are a dict of midinotes.
            tracks = {trackname: {midinotes, tempo}}
        """

        # Create the MIDIFile Object with 1 track
        MyMIDI = MIDIFile(len(list(tracks.keys())))

        # Add track name and tempo.
        for track_number, track_name in enumerate(sorted(tracks.keys())):
            print("Saving track:", track_number, track_name)
            MyMIDI.addTrackName(track_number, 0, track_name)
            MyMIDI.addTempo(track_number , 0, tempo)

            # Add the notes.
            print( track_number, track_name, tracks[track_name][0].track)
            for note in tracks[track_name]:
                print('Adding note:', 
		            track_number, 
					note.channel,
                    note.pitch,
                    note.time,
                    note.duration,
                    note.volume)
				
                MyMIDI.addNote(
                    track_number, #note.track,
                    note.channel,
                    note.pitch,
                    note.time,
                    note.duration,
                    note.volume)

        # And write it to disk.
        print('Saving midi file:', path)
        binfile = open(path, 'wb')
        MyMIDI.writeFile(binfile)
        binfile.close()

def test_midi():
    # create a test midi
    title = 'Test MIDI'
    tempo= 154
    tracks = {}
    for track in range(17):
        notes = []
        for value in range(0,127):
            note = midinote(
             track=track,
             channel=track,
             pitch=value,
             time=value/2.,
             duration=0.5,
             volume=120
            )
            notes.append(note)
        tracks['track '+ str(track)] = notes
    path = "output/test_midi.mid"

    save_midi(title, tempo, tracks, path)



def value_to_pitch(value, data_range, music_range, debug=False):
	"""
	Using the range, the values and the musical output range,
	we can guess the output pitch.

	Note that it returns pitch as a float, not a int.
	"""
	if debug: print((value, data_range, music_range))
	data_extent = data_range[1] - data_range[0]
	music_extent = music_range[1] - music_range[0]

	fraction = (value - data_range[0]) / data_extent

	pitch = (fraction * music_extent) + music_range[0]
	if np.isnan(pitch):
		print(("value_to_pitch:", value, pitch, data_range, music_range))
		assert 0
	return pitch


def time_to_placement(time, time_range, notes_per_beat):
	"""
	Using the time range, the time value and the notes per beat,
	we calculate.

	Assume annual time resolution.

	Note that it returns pitch as a float, not a int.
	"""
	#time_range[0] is out_time= 0
	duration = 1. / notes_per_beat
	#print(time, (time - time_range[0])/notes_per_beat)
	return (time - time_range[0])/notes_per_beat, duration


def pitch_to_value(pitch, data_range, music_range):
	"""
	Using the pitch, the data range and the musical output range,
	we can guess the uuantized data value.
	"""
	data_extent = data_range[1] - data_range[0]
	music_extent = music_range[1] - music_range[0]

	fraction = float(pitch - music_range[0]) / music_extent

	value = (fraction * data_extent) + data_range[0]
	return value


def remove_doubles(midinotes, notes_per_beat = 4, beats_per_chord=4, dont_remove_new_chord = True):
	"""
	Removes notes with repeated pitch
	"""
	midinotes_out = []

	notes_removed = 1
	t0 = midinotes[0][0]
	for i, note in enumerate(midinotes):
		print(("remove_doubles", i, note))
		if np.ma.is_masked(note):
			midinotes_out.append(note)
			continue
		if i == 0:
			midinotes_out.append(note)
			continue

		if dont_remove_new_chord:
			if note[0] % beats_per_chord == 0:
				midinotes_out.append(note)
				continue
			#print i, note, note[0],  notes_per_beat, beats_per_chord
			#if i > 64 : assert 0

		last_note = midinotes_out[i-notes_removed]
		if np.ma.is_masked(last_note):
			midinotes_out.append(note)
			continue

		#print i, note, last_note
		pitch = note[1]
		duration = note[3]

		last_pitch = last_note[1]
		last_duration = last_note[3]

		if pitch == last_pitch:
			new_duration = last_duration + duration
			new_note = last_note
			new_note[3] = new_duration
			midinotes_out[i-notes_removed] = new_note

			notes_removed+=1
		else:
			midinotes_out.append(note)

	return midinotes_out


def change_velocity(midinotes, velocities, vel_range = [75, 127]):
	"""
	Set velocity according to some data.
	"""
	midinotes_out = []

	if velocities.min() == velocities.max():
		print(("velocities failed", velocities))
		print((velocities.min(), velocities.max()))
		assert 0
	velocities = np.ma.masked_invalid(velocities)

	out_vels = []
	for i, note, in enumerate(midinotes):
		if np.ma.is_masked(note):
			midinotes_out.append(note)
			continue
		if note[1] and np.ma.is_masked(velocities[i]):
			print(("change_velocity: note exists, velocity does not:", note[1], np.ma.is_masked(velocities[i])))
			assert 0
		velocity = value_to_pitch(velocities[i],
					[velocities.min(),velocities.max()],
					vel_range,
					)
		diff = 1
		while np.ma.is_masked(velocity):
			velocity = velocities[i - diff]
			diff += 1
			if i -diff < 0:
				assert 0

		if velocity > 127: velocity = 127
		if velocity < 1: velocity = 1

		note[2] = velocity
		out_vels.append(velocity)
		midinotes_out.append(note)

	return midinotes_out




# def create_midinotes(times, data, time_range, data_range, music_range, notes_per_beat = 4):
# 	"""
# 	Create a set of musical notes.
#
# 	Note that these pitches are still floats.
# 	"""
# 	midinotes = []
# 	data = np.ma.masked_invalid(data)
# 	if len(times) != len(data):
# 		print("create_midinotes: times and data have wrong durations:", len(times), len(data))
# 		assert False
#
# 	t_min = 1E20
# 	for i, da in enumerate(data):
# 		if np.ma.is_masked(da):
# 			midinotes.append(da)
# 			continue
# 		pitch = value_to_pitch(da, data_range, music_range)
# 		time, duration = time_to_placement(times[i], time_range, notes_per_beat)
# 		if time < t_min: t_min = time.copy()
# 		note = [
# 			time, 		# time
# 			pitch, 		#60 is middle C (C5)
# 			127, 		#velocity_range(t*1000), # velocity
# 			duration]
#     midinotes.append(note)
#
#     for i, note in enumerate(midinotes):
#         midinotes[i][0] -= t_min
#         print(i, midinotes[i][0], '->', midinotes[i][0])
#         #assert 0
#     return midinotes

def strip_mask(midinotes):
	"""
	Remove masked values from array.
	"""
	midinotes_out = []
	for i, note, in enumerate(midinotes):
		if np.ma.is_masked(note):
			continue
		for no in note:
			if np.ma.is_masked(no):
				continue
		midinotes_out.append(note)
	return midinotes_out


def long_last_note(midinotes):
	"""
	Make the final note longer.
	"""
	midinotes = sorted(midinotes)
	if len(midinotes) == 0:
		return midinotes

	i = -1
	found = False
	while not found:
		if np.ma.is_masked(midinotes[i]):
			i = i -1
			continue
		midinotes[i][3] += 8.
		found = True
		print(("long_last_note:", found, i, midinotes[i]))
	return midinotes



def remove_duplicates(midinotes_list):
	"""
	Goes through the midi notes and removes the duplicates in different tracks.

	midi notes:
	0: time of note
	1: pitch
	2: velocity (loudness)
	3: duration of note.

	"""
	midinotes_dict = {}
	for track in midinotes_list:
		for note in track:
			tup = (note[0], note[1])
			try:
				midinotes_dict[tup].append(note)
			except:
				midinotes_dict[tup] = [note, ]

	midinotes = []
	for tup, notes in sorted(midinotes_dict.items()):
		if len(notes) == 1:
			midinotes.append(notes[0])
		else:
			print(("Found duplicates:", notes))
			vel = max([note[2] for note in notes])
			dur = max([note[3] for note in notes])
			note = [tup[0], tup[1], vel, dur]
			midinotes.append(note)
	#assert 0
	return [midinotes, ]


def convert_notes_to_data(midinotes, data_range, music_range):
	"""
	Calculates quantized data from notes.
	"""
	data = []
	for note in midinotes:
		if np.ma.is_masked(note):
			data.append(note)
			continue
		pitch = note[1]
		value = pitch_to_value(pitch, data_range, music_range)
		data.append(value)
	data = np.ma.array(data)
	return data


def quantize_time(times,  data):
	"""
	Extends each time and data point to the full extent.
	"""
	new_times = []
	new_data = []
	for i, t in enumerate(times):

		if i == len(times) -1:
			# Last time step
			next_time = t + (t - times[i-1])
		else:
			next_time = times[i+1]
		new_times.append(t)
		new_times.append(next_time)

		new_data.append(data[i])
		new_data.append(data[i])
	return new_times, new_data



def calculate_moving_average(times,data, window_len=5.,window_units='years', field = ''):
	######
	#
	window_units = window_units.lower()
#	if window_units not in ['days','months','years']:
#        raise ValueError("calculate_moving_average: window_units not recognised"+str(window_units))

	data = np.ma.array(data)
	times= np.ma.array(times)

	#####
	# Assuming time
	if type(window_len) in [float, int]:
		if window_units in ['years',]:	window = float(window_len)/2.
		if window_units in ['months',]:	window = float(window_len)/(2.*12.)
		if window_units in ['days',]:	window = float(window_len)/(2.*365.25)
		output = []#np.ma.zeros(data.shape)
		for i,t in enumerate(times):
			tmin = t-window
			tmax = t+window
			arr = np.ma.masked_where((times < tmin) + (times > tmax) + data.mask, data)
			output.append(arr.mean())
		return np.ma.array(output)

	if type(window_len) in [list, tuple, dict]:
		output = []
		for i,t in enumerate(times):
			if i > len(window_len)-1: continue
			window = float(window_len[i])/2.
			print((i, t, window, len(times), len(window_len)))

			tmin = t-window
			tmax = t+window
			arr = np.ma.masked_where((times < tmin) + (times > tmax) + data.mask, data)
			output.append(arr.mean())
		return np.ma.array(output)


if __name__ == "__main__":
    test_midi()
