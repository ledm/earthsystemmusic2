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


	#climate_music_video(settings, plotter)
    bpm = settings.globals['bpm']
    notes_per_beat = settings.globals['notes_per_beat']
    plot_every = settings.globals.get('plot_every', 1)

    frame_rate = str(bpm/60.*notes_per_beat/plot_every)

    output_mp4 = settings.globals['output_path'] + settings.globals['name']+ '_no_sound.mp4'
    #make_mp4 = "ffmpeg -nostdin -y -framerate "+frame_rate+" -s 1920x1280 -i "+plotter.video_folder+"/frame_%06d.png -i "+output_mp3+" -pix_fmt yuv420p -c:v libx264  -preset ultrafast  "+output_mp4
    make_mp4 = "ffmpeg -nostdin -y -framerate "+frame_rate+" -s 1920x1280 -i "+plotter.video_folder+"/frame_%06d.png -pix_fmt yuv420p -c:v libx264  -preset ultrafast "+output_mp4
    print(make_mp4)

    ######
    # Output paths:
    # output_mid = output_fold+name+'.mid'
    # output_mp3 = output_fold+name + '.mp3'
    # output_wav = output_fold+name + '.wav'
    # output_wmv = output_fold + name+ '.wmv'
    # image_fold = ymlu.get_image_folder(name)





if __name__ == "__main__":
    earthsystemmusic()
