
import os
import yaml
from shelve import open as shopen
import csv





def get_image_folder(name):
    fold = get_output_folder(name)
    image_fold = fold+'images'
    try:
        os.makedirs(image_fold)
    except:
        pass
    return image_fold


def get_output_folder(name):
    image_fold = 'output/'+name+'/'
    try:
        os.makedirs(image_fold)
    except:
        pass
    return image_fold


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
    return track_dict





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

def calculate_moving_average(data, track_dict):
    ######
    #
    moving_average = track_dict['moving_average']
    if moving_average in ['', [], None]:
        return data
    if isinstance(moving_average, str):
        window_width, window_units = moving_average.split(' ')
    window_units = window_units.lower()
    if window_units not in ['days','months','years']:
        raise ValueError("calculate_moving_average: window_units not recognised"+str(window_units))

    times = np.array([t for t in sorted(data.keys())])
    data = np.array([data[t] for t in times])

    data = np.ma.array(data)
    times= np.ma.array(times)

    #####
    # Assuming time
    output = {}
    if type(window_len) in [float, int]:
        if window_units in ['years',]:	window = float(window_len)/2.
        if window_units in ['months',]:	window = float(window_len)/(2.*12.)
        if window_units in ['days',]:	window = float(window_len)/(2.*365.25)
        for i,t in enumerate(times):
            tmin = t-window
            tmax = t+window
            arr = np.ma.masked_where((times < tmin) + (times > tmax) + data.mask, data)
            output[t] = arr.mean()

    if type(window_len) in [list, tuple, dict]:
        for i,t in enumerate(times):
            if i > len(window_len)-1: continue
            window = float(window_len[i])/2.
            print((i, t, window, len(times), len(window_len)))

            tmin = t-window
            tmax = t+window
            arr = np.ma.masked_where((times < tmin) + (times > tmax) + data.mask, data)

            output[t] = arr.mean()

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
        self.tracks = self.yml['tracks']
        for track, track_dict in self.tracks.items():
            # Load track data
            paths = track_dict['data_paths']
            self.tracks[track]['data'] = self.load_track(track, paths)

            # Load track velocity data.
            vel_paths = track_dict['velocity_paths']
            self.tracks[track]['velocity_data'] = self.load_track(track,vel_paths )

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

        data = calculate_moving_average(data, track_dict)
        print(data)
        return data

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
    test_yml_fn = 'yml/test.yml'
    yml = load_yml(test_yml_fn)
    print('Testing', test_yml_fn)
    test_global(yml)
    test_tracks(yml)
    #for track, track_dict in yml['tracks'].items():
    #    data = load_track(track, track_dict)
    #print('Test yml: Success')

    print('Test settings class:')
    setting = settings(test_yml_fn)
    #print(setting)
    print('Test setting: Success')


if __name__ == "__main__":
    ymltest()
