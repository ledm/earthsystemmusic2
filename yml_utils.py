
import os
import yaml
from shelve import open as shopen



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
    print("load_csv: not implemented yet")
    assert 0


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

def apply_kwargss(track_dict, track_data, ):
    """
    Apply key word arguments to manipulate the data.
    ie, apply a fix, or retime the spin up, etc.
    """
    return track_dict


def load_track(track, track_dict):
    """
    Load a track from the track dict
    """
    print('Trying to load:', track_dict['data_paths'])

    if isinstance(track_dict['data_paths'], str):
        track_dict['data_paths'] = [track_dict['data_paths'], ]

    # data dict: it's always in format data['time'] = data value.
    data = {}
    for path in track_dict['data_paths']:
        print('Loading', path)
        if track_dict['data_type'] == 'shelve':
            track_data = load_shelve(track_dict, path)
        elif track_dict['data_type'] in ['nc', 'netcdf']:
            track_data = load_netcdf(track_dict, path)
            assert 0
        elif track_dict['data_type'] in ['csv']:
            track_data = load_csv(track_dict, path)
            assert 0

        track_data = apply_kwargs(track_dict, track_data, )
        data.update(track_data)
    print(data)
    return data



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


def test_global(yml):
    """
    Test global dict
    """
    print('Testing global dict:')
    globals = yml['global']
    global_keys =  ['title', 'output_path', 'bpm', 'plot_every' ]
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
        # title: 'test'
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
    for track, track_dict in yml['tracks'].items():
        data = load_track(track, track_dict)
    print('Test yml: Success')

if __name__ == "__main__":
    ymltest()
