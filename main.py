
import argv

import yml_utils as ymlu

def earthsystemmusic():

    print(argv[1])
    yml_fn = argv[1]

    yml = ymlu.load_yml(yml_fn)
    name = yml['name']

    ######
    # Output paths:
    output_fold = ymlu.get_output_folder()
    output_mid = output_fold+name+'.mid'
    output_mp3 = output_fold+name + '.mp3'
    output_wav = output_fold+name + '.wav'
    output_wmv = output_fold + name+ '.wmv'
    output_mp4 = output_fold + name+ '.mp4'
    image_fold = ymlu.get_image_folder(name)


if __name__ == "__main__":
    earthsystemmusic()
