
import os
import sys
import yaml
import numpy as np
from shelve import open as shopen
import csv

from midiranges import instrument_range, instrument_channels, create_chord_list
from music_utils import midinote, save_midi


chord_dict = create_chord_list()

def get_image_folder(name):
    fold = get_output_folder(name)
    image_fold = fold+'images'
    try:
        os.makedirs(image_fold)
    except:
        pass
    return image_fold

def folder(name):
    try:
        os.makedirs(name)
    except:
        pass
    return name

def get_output_folder(name):
    image_fold = 'output/'+name+'/'
    try:
        os.makedirs(image_fold)
    except:
        pass
    return image_fold


#####
# Loading utils:
def load_netcdf(track_dict, path):
    """
    Load the data from an netcdf file.
    """
    print("load_netcdf: not implemented yet")
    assert 0

def load_csv(track_dict, path):
    """
    Load the data from a csv file.
    """
    #print("load_csv: not implemented yet")
    #assert 0
    data = {}
    csv_file = open(path)
    for row in csv_file.readlines():
        if row[0] == '#': continue
        if row == '\n': continue
        if row.lower().find('year') > -1: continue
        row = row.split(',')
        #print(row)
        data[float(row[0])] = float(row[1])
    return data


def load_shelve(track_dict, path):
    """
    Load the data from a shelve file.
    """
    print('Loading shelve from path:', path)
    sh = shopen(path , 'r')
    print(sh.keys())
    shelve_data = sh['modeldata'][track_dict.data_key]
    sh.close()
    return shelve_data

def apply_kwargs(track_dict, track_data, ):
    """
    Apply key word arguments to manipulate the data.
    ie, apply a fix, or retime the spin up, etc.
    """
    return track_data


def load_yml(yml_fn):
    """
    Load the yml file
    ---------
    yml_fn:str
        Yaml file path

    Returns:
        yaml file loaded as dictionairy.
    """
    with open(yml_fn) as f:
        my_dict = yaml.safe_load(f)
    return my_dict


# Music utils:
def value_to_pitch(value, data_range, music_range, debug=True):
    """
    Using the range, the values and the musical output range,
    we can guess the output pitch.

    Note that it returns pitch as a float, not a int.
    """

    data_extent = data_range[1] - data_range[0]
    music_extent = music_range[1] - music_range[0]

    fraction = (value - data_range[0]) / data_extent

    pitch = (fraction * music_extent) + music_range[0]
    if np.isnan(pitch):
        print("value_to_pitch:", value, pitch, data_range, music_range)
        assert 0
    #print(pitch)
    #assert 0
    if debug:
        print("value_to_pitch:", value, '->',pitch, data_range, music_range)
    return pitch


def time_to_placement(time, time_range, notes_per_beat):
    """
    Using the time range, the time value and the notes per beat, we calculate
    where the time should be in the piece.

    Note that it returns time as a float, not a int.
    """
    #time_range[0] is out_time= 0
    duration = 1. / notes_per_beat
    #print(time, (time - time_range[0])/notes_per_beat)
    return (time - time_range[0])/notes_per_beat, duration


def calculate_moving_average(data, track_dict, debug = False):
    ######
    #
    moving_average = track_dict['moving_average']
    if moving_average in ['', [], None]:
        print('No moving_average needed.')
        return data
    if isinstance(moving_average, str):
        window_width, window_units = moving_average.split(' ')
        window_width = float(window_width)

    window_units = window_units.lower()
    if window_units not in ['days','months','years']:
        raise ValueError("calculate_moving_average: window_units not recognised"+str(window_units))

    print("calculate_moving_average:", data)
    for t in sorted(data.keys()):
        if debug:
            print("calculate_moving_average:", t, ':',data[t])

    arr_times = [t for t in sorted(data.keys())]
    arr_data = np.ma.array([data[t] for t in arr_times])
    arr_times = np.ma.array(arr_times)
    if debug:
        print('arr_times:', arr_times)
        print('arr_data:', arr_data)
        print('calculate_moving_average:', window_width, window_units )

    #####
    # Assuming time
    output = {}
    if isinstance(window_width, float):
        if window_units in ['years',]:
            window = window_width/2.
        elif window_units in ['months',]:
            window = window_width/(2.*12.)
        elif window_units in ['days',]:
            window = window_width/(2.*365.25)

        for i, t in enumerate(arr_times):
            tmin = t - window
            tmax = t + window
            arr = np.ma.masked_where((arr_times < tmin) + (arr_times > tmax) + arr_data.mask, arr_data)
            output[t] = arr.mean()

    elif type(window_width) in [list, tuple, dict]:
        for i, t in enumerate(arr_times):
            if i > len(window_width)-1: continue
            window = float(window_width[i])/2.
            if debug:
                print((i, t, window, len(arr_times), len(window_width)))

            tmin = t-window
            tmax = t+window
            arr = np.ma.masked_where((arr_times < tmin) + (arr_times > tmax) + arr_data.mask, arr_data)

            output[t] = arr.mean()
    else:
        print('calculate_moving_average: window not understood:',window_width, window_units)
        assert 0
    print('output:', output)

    return output


class settings:
    def __init__(self, yml_fn):
        """
        Create a settings dictionairy for the yml file.
        """
        self.fn = yml_fn
        #self. yml is the yml dict.
        self.yml = load_yml(yml_fn)
        self.globals = self.yml['global']
        self.debug = self.globals.get('debug', True)

        self.tracks = self.yml['tracks']
        for track, track_dict in self.tracks.items():

            # Load track data
            paths = track_dict['data_paths']
            self.tracks[track]['data'] = self.load_track(track, paths)

            # Create pitches dict.
            self.create_pitches(track)

            # Create time dict:
            self.create_locations(track)

            # Create volume dict:
            self.create_volumes(track)

            # Create scale in time:
            self.determine_scales(track)

            # Enforce the scale:
            self.modulate_to_scale(track)

            # Set the Channels
            self.modulate_channel(track)

            # Remove successive duplicates:
            self.remove_doubles(track)

            # Extend the final note:
            self.long_last_note(track)

        # Convert to Midi notes:
        self.convert_to_midi()

    def load_track(self, track, paths):
        """
        Load a track from the track dict.
        """
        track_dict =  self.tracks[track]
        print('Trying to load:', track, paths)

        if isinstance(paths, str):
            paths = [paths, ]

        data = {}
        for path in paths:
            print('Loading', path)
            if track_dict['data_type'] == 'shelve':
                track_data = load_shelve(track_dict, path)
            elif track_dict['data_type'] in ['nc', 'netcdf']:
                track_data = load_netcdf(track_dict, path)
                assert 0
            elif track_dict['data_type'] in ['csv']:
                track_data = load_csv(track_dict, path)

            track_data = apply_kwargs(track_dict, track_data, )
            data.update(track_data)

        # Apply any kind of smoothing to the data:
        data = calculate_moving_average(data, track_dict)

        # Set data and time ranges.
        times = np.ma.array([t for t in sorted(data.keys())])
        data = np.ma.array([data[t] for t in times])

        time_range =  track_dict.get('time_range', None)
        if not time_range:
            time_range = [times.min(), times.max()]
            track_dict['time_range'] = time_range

        # Remove masked values.
        times = np.ma.masked_where(data.mask + (times < time_range[0] ) + (times > time_range[1]), times )
        data  = np.ma.masked_where(data.mask + times.mask,  data )

        times = times.compressed()
        data = data.compressed()
        data = {t:d for t,d in zip(times,data)}

        return data

    def create_pitches(self, track): #times, data, time_range, data_range, music_range, notes_per_beat = 4):
        """
        Create a set of musical notes.

        Note that these pitches are still floats.
       """
        # Check musical range for this track:
        # Default is timidity+ piano
        vst = self.tracks[track].get('vst', None)
        instrument = self.tracks[track].get('instrument', None)
        music_range = self.tracks[track].get('music_range', None)

        # either need a vst instrument combo, or a music range.
        if vst == instrument == music_range == None:
            print("Need to provide either a vst or a range")
            assert 0

        if vst and instrument:
            print ('Loading: ',vst, instrument, instrument_range[vst][instrument])
            #assert 0
            self.tracks[track]['music_range'] = instrument_range[vst][instrument]

        # Check whether a data range was provided.
        if not self.tracks[track].get('data_range', None):
            datrange = list(self.tracks[track]['data'].values())
            data_range = [min(datrange), max(datrange)]
            self.tracks[track]['data_range'] = data_range

        pitches = {}
        for time, dat in self.tracks[track]['data'].items():
            pitch = value_to_pitch(dat,
                                   self.tracks[track]['data_range'],
                                   self.tracks[track]['music_range'])
            pitches[time] = pitch
        self.tracks[track]['pitches_float'] = pitches

    def create_locations(self, track):
        """
        Create the dictionairy to link the dataset time and the location in time in the musical piece.

        Notes per beat is actually "years per musical beat".

        It works like this:
        Time zero is allocated to be the first note of any in the piece.
        The duration is set tp the minimum
        """
        #time_range[0] is out_time= 0
        time_range = self.tracks[track]['time_range']
        notes_per_beat = self.tracks[track]['notes_per_beat']

        duration = 1. / notes_per_beat

        locations = {}
        durations = {}
        for time, dat in self.tracks[track]['data'].items():
            durations[time] = duration
            locations[time] = (time - time_range[0])/notes_per_beat

        self.tracks[track]['locations'] = locations
        self.tracks[track]['durations'] = durations

    def create_volumes(self, track):
        """
        Create a dict for volumes from data.
        """
        # Load track volume data.
        vel_paths = self.tracks[track].get('volume_paths', None)
        vol_range = self.tracks[track].get('volume_range', 120)

        if not vel_paths:
            # No data is provided for volume, set a flat volume curve.
            self.tracks[track]['volumes'] = {
                t:max(vol_range) for t in self.tracks[track]['data']['times']
            }
            return

        volumes_data = self.load_track(track, vel_paths )
        volumes_data_range = list(volumes_data.values())
        volumes_data_range = [min(volumes_data_range), max(volumes_data_range)]
        volumes = {}
        for time, dat in volumes_data.items():
            volume = value_to_pitch(dat,
                                    volumes_data_range,
                                    vol_range)
            if self.debug:
                print("volume:", time, volume)
            volumes[time] = volume
        self.tracks[track]['volumes'] = volumes

    def determine_scales(self, track):
        """
        Using the times, determinues which scale is linked with each note.

        Uses the scale list to guess which scale is associated with each time.
        """
        beats_per_chord = self.tracks[track]['beats_per_chord']
        scale_list = self.tracks[track]['scales']
        if isinstance(scale_list, str):
            scale_list = [scale_list, ]

        scales = {}
        for time, loc in self.tracks[track]['locations'].items():
            scale_num = (int(loc/float(beats_per_chord)))%len(scale_list)
            #print(note[0], beats_per_chord, len(scales))
            scales[time] = scale_list[scale_num]
        self.tracks[track]['scales'] = scales

    def modulate_to_scale(self, track):
        """
        Using the chord and pitch (float) already calculated.

        Produces a list of pitches, but in the correct order.
        """
        pitches = {}
        for time, floatpitch in self.tracks[track]['pitches_float'].items():
            scale = self.tracks[track]['scales'][time]
            pitch = min(chord_dict[scale], key=lambda x:abs(x - floatpitch))
            pitches[time] = pitch
            if self.debug:
                print(time, floatpitch, scale, '->', pitch )
        self.tracks[track]['pitches'] = pitches

    def modulate_channel(self, track):
        """
        Changing the channel for this track.

        Produces a list of channels, but in the correct order.
        If a VST and instrument is provided, then
        """
        # Different instruments have different channels
        vst = self.tracks[track].get('vst', None)
        instrument = self.tracks[track].get('instrument', None)
        main_channel =  self.tracks[track].get('channel', None)

        if vst == 'VSCO':
            # Simple VST with one channel per instrument.
            main_channel = instrument_channels[instrument]

        channels = {}
        # In this case, there is only one channel.
        if isinstance(main_channel, int):
            for time, floatpitch in self.tracks[track]['pitches_float'].items():
                channels[time] = main_channel

        self.tracks[track]['channels'] = channels

    def remove_doubles(self, track, debug= False):
        """
        Remove successive duplicates in the pitch, loc, volume, duration
        dicts.

        Unlike the old vesrion, we do this in place now, instead of creating a new list.
        """
        times =  sorted(self.tracks[track]['locations'].keys())
        notes_removed = 0
        t_m1 = -1
        for i, time in enumerate(times):
            print("remove_doubles", i, time)
            if i == 0:
                t_m1 = time
                continue

            duration = self.tracks[track]['durations'][time]
            pitch = self.tracks[track]['pitches'][time]
            last_pitch = self.tracks[track]['pitches'][t_m1]
            last_duration =  self.tracks[track]['durations'][t_m1]

            # Option to play a notev whenever the chord changes, even if
            # there's no change in note pitch.
            if self.tracks.get('play_new_chords', False):
                last_scale = self.tracks[track]['scales'][t_m1]
                new_scale = self.tracks[track]['scales'][time]
                if last_scale != new_scale:
                    t_m1 = time
                    continue

            if pitch == last_pitch:
                new_duration = last_duration + duration
                self.tracks[track]['durations'][t_m1] = new_duration
                if debug:
                    print("Found double:", [t_m1, last_pitch, last_duration], [time, pitch,duration], 'length:',new_duration)
                for dict_key in ['pitches', 'durations', 'locations', 'scales','volumes']:
                    del self.tracks[track][dict_key][time]
                notes_removed+=1
            else:
                t_m1 = time
        if self.debug:
            print("Removed:", notes_removed, 'notes out of', len(times))

    def long_last_note(self, track):
        """
        Extend the final note of the track.
        """
        max_time =  sorted(self.tracks[track]['locations'].keys())[-1]
        self.tracks[track]['durations'][max_time] = 8.

    def convert_to_midi(self,):
        """
        Convert to the 6 parameter midi data.

        MyMIDI.addNote(track, channel, pitch, time, duration, volume)
        """
        miditracks = {}
        for track_number, track in enumerate(self.tracks):
            miditracks[track] = []
            channel = self.tracks[track]['channel']
            for time, pitch in self.tracks[track]['pitches'].items():
                note = midinote(
                    track=track_number, # Means nothing, is overwritten later.
                    channel=self.tracks[track]['channels'][time],
                    pitch=int(pitch),
                    time=self.tracks[track]['locations'][time],
                    duration=self.tracks[track]['durations'][time],
                    volume=int(self.tracks[track]['volumes'][time]),
                    )
                miditracks[track].append(note)

        title = self.globals['title']

        tempo = self.globals['bpm']
        path = folder(self.globals['output_path'])+'/'+self.globals['name']+'.mid'
        save_midi(title, tempo, miditracks, path)


#####
# Tests:
def test_global(yml):
    """
    Test global dict
    """
    print('Testing global dict:')
    globals = yml['global']
    global_keys =  ['name', 'output_path', 'bpm', 'plot_every' ]
    for key in global_keys:
        print('test', key, globals[key])
    print('Test Global dict: Success')


def test_tracks(yml):
    """
    Test specific tracks
    """
    print('Testing tracks dict:')
        # bpm: 146.
        # notes_per_beat: 4.
        # beats_per_chord: 2.
        # plot_every: 1
        # name: 'test'
        # output_path: 'output/test'
    tracks = yml['tracks']
    for track, track_dict in tracks.items():
        for key, value in track_dict.items():
            print(track, key, value)
    print('Test tracks: Success')


def ymltest():
    print('Running yml_utils tests')
    try:
        test_yml_fn = sys.argv[1]
    except:
        #test_yml_fn = 'yml/test.yml'
        pass

    yml = load_yml(test_yml_fn)
    print('Testing', test_yml_fn)
    test_global(yml)
    test_tracks(yml)
    #for track, track_dict in yml['tracks'].items():
    #    data = load_track(track, track_dict)
    #print('Test yml: Success')

    print('Test settings class:')
    setting = settings(test_yml_fn)
    print(setting)
    print('Test setting: Success')


if __name__ == "__main__":
    ymltest()
