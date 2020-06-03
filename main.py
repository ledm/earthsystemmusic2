#!/bin/python3

import sys
from climate_music_maker import climate_music_maker
from climate_music_plotter import climate_music_plotter

def earthsystemmusic():

    print('Runningearthsystemmusic')
    try:
        test_yml_fn = sys.argv[1]
    except:
        #test_yml_fn = 'yml/test.yml'
        print(sys.argv[1])
        print('Please provide a climate music maker yml file')
        return

    settings = climate_music_maker(test_yml_fn)
    print('Climate_music_maker: Success')
    plotter = climate_music_plotter(settings)

	#
	#climate_music_video(settings, plotter)




    ######
    # Output paths:
    # output_mid = output_fold+name+'.mid'
    # output_mp3 = output_fold+name + '.mp3'
    # output_wav = output_fold+name + '.wav'
    # output_wmv = output_fold + name+ '.wmv'
    # output_mp4 = output_fold + name+ '.mp4'
    # image_fold = ymlu.get_image_folder(name)





if __name__ == "__main__":
    earthsystemmusic()
