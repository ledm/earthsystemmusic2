
from climate_music_maker import climate_music_maker
from matplotlib import pyplot


def get_image_folder(name):
    fold = get_output_folder(name)
    image_fold = fold+'images'
    try:
        os.makedirs(image_fold)
    except:
        pass
    print("get_image_folder:", image_fold )
    return image_fold


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


class climate_music_plotter:
    def __init__(self, cmm):
        """
        Make the plots
        cmm
        """
        self.cmm = cmm
        self.globals = cmm.globals
        self.tracks = cmm.tracks
        self._make_data_plots()
        self._make_pitch_plots()


    def _make_data_plots(self,):
        image_fold = self.cmm.globals['output_path']
        if not image_fold:
            image_fold = get_image_folder(name)

        outpath = image_fold+'/tmp.png'
        #outpath = image_fold+'/image_0.png'
        #if os.path.exists(outpath):
        #    continue

        fig, ax = pyplot.subplots()

        for track, track_dict in self.tracks.items():
            colour = track_dict['colour']
            name = track_dict['longname']

            # Raw data:
            raw_times = sorted(track_dict['raw_data'].keys())
            raw_data = [track_dict['raw_data'][t] for t in raw_times]
            #new_times, new_data = quantize_time(raw_times,raw_data)
            ax.plot(raw_times, raw_data, color=colour, lw= 0.5, label = name)

            # Smoothed data
            times = sorted(track_dict['data'].keys())
            data = [track_dict['data'][t] for t in times]
            #new_times, new_data = quantize_time(times, data)
            ax.plot(times, data, color=colour, ls=':', lw=0.7)#, label = name)

            # Recalculated data
            recalc_times = sorted(track_dict['recalc_data'].keys())
            recalc_data = [track_dict['recalc_data'][t] for t in recalc_times]
            new_times, new_data = quantize_time(recalc_times, recalc_data)
            ax.plot(new_times, new_data, color=colour, lw=0.2)#, label = name)
            #break

        pyplot.legend()
        pyplot.suptitle(self.globals['title'])
        #fig.tight_layout()
        print("saving", outpath)
        dpi = 250.

        pyplot.savefig(outpath, dpi=dpi)
        pyplot.close()

    def _make_pitch_plots(self,):
        image_fold = self.cmm.globals['output_path']
        if not image_fold:
            image_fold = get_image_folder(name)

        outpath = image_fold+'/pitch.png'
        #outpath = image_fold+'/image_0.png'
        #if os.path.exists(outpath):
        #    continue

        fig, ax = pyplot.subplots()

        for track, track_dict in self.tracks.items():
            colour = track_dict['colour']
            name = track_dict['longname']

            # pitches
            times = sorted(track_dict['pitches'].keys())
            pitches = [track_dict['pitches'][t] for t in times]
            new_times, new_data = quantize_time(times, pitches)
            ax.plot(new_times, new_data, color=colour, lw=0.5, label = name)

            # float pitches
            times = sorted(track_dict['pitches_float'].keys())
            pitches = [track_dict['pitches_float'][t] for t in times]
            new_times, new_data = quantize_time(times, pitches)
            ax.plot(new_times, new_data, color=colour, lw=0.2)#, label = name)

        pyplot.legend()
        pyplot.suptitle(self.globals['title'])
        #fig.tight_layout()
        print("saving", outpath)
        dpi = 250.

        pyplot.savefig(outpath, dpi=dpi)
        pyplot.close()
            # linestyle = linestyles[key])



        #for i, t in enumerate(times[fields[0]]):
        #    if i % plot_every != 0: continue



        # fig, ax1 = pyplot.subplots()
		# fig.set_size_inches(1920./dpi, 1280./dpi)
