
import os

from climate_music_maker import climate_music_maker
from music_utils import folder
from matplotlib import pyplot
import matplotlib.gridspec as gridspec
import numpy as np


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
    return np.array(new_times), np.array(new_data)


class climate_music_plotter:
    def __init__(self, cmm):
        """
        Make the plots
        cmm
        """
        self.cmm = cmm
        self.globals = cmm.globals
        self.tracks = cmm.tracks
        self.video_paths = []
        self._make_data_plots()
        self._make_pitch_plots()
        self._make_video_plots_()

        for t, time in enumerate(sorted(self.globals['all_times'].keys())):
            #continue
            if t % self.globals.get('plot_every', 1) !=0:
                continue
            self._make_video_plots_(plot_id=t, time_line=time)


    def _make_video_plots_(self, plot_id=None, time_line=None):
        image_fold = self.cmm.globals['output_path']
        if not image_fold:
            image_fold = get_image_folder(name)

        if plot_id is None:
            outpath = image_fold+'/video.png'
        else:
            self.video_folder = folder(image_fold+'/video_frames/')

            outpath = self.video_folder+ 'frame_'+str(plot_id).zfill(6)+'.png'
            self.video_paths.append(outpath)
        if os.path.exists(outpath):
            return
        #outpath = image_fold+'/image_0.png'
        #if os.path.exists(outpath):
        #    continue
        fig = pyplot.figure()
        dpi = self.globals.get('dpi', 250.)
        image_size = self.globals.get('image_size', [1920., 1280.])
        fig.set_size_inches(image_size[0]/dpi,image_size[1]/dpi)

        axes = {}
        panes  = {}
        numbered_axes = {}
        ylabels={}

        for i, track, in enumerate(sorted(self.tracks.keys())):
            # get pane number, default is alphabetical
            panes[track] = self.tracks[track].get('pane', i+1)
        panes_count = max({pane:True for track, pane in panes.items()}.keys())
        gs1 = gridspec.GridSpec(panes_count, 1)
        gs1.update(wspace=0., hspace=0.) # set the spacing between axes.

        subplot_indices = {}
        for track, pane in panes.items():
            subplot_index = (panes_count, pane)
            if subplot_index in subplot_indices:
                # Link to existing subplot
                axes[track] = subplot_indices[subplot_index]
            else:
                # Create new subplot
                #axes[track] = gridspec.GridSpec(panes_count, pane)
                axes[track] = pyplot.subplot(gs1[pane-1])
                #axes[track] = pyplot.subplot(panes_count, 1, pane, xmargin=0., ymargin=0.05)
                numbered_axes[pane] = axes[track]
                ylabels[pane] = self.tracks[track].get('y_label', '')
                subplot_indices[(panes_count, pane)] = axes[track]

        # make plot.
        for track, track_dict in self.tracks.items():
            colour = track_dict['colour']
            name = track_dict['longname']

            # Recalculated data
            recalc_times = sorted(track_dict['recalc_data'].keys())
            recalc_data = [track_dict['recalc_data'][t] for t in recalc_times]
            new_times, new_data = quantize_time(recalc_times, recalc_data)

            if self.globals.get('scroll', False):
                tmin = np.min(new_times)
                tmax = np.max(new_times)
                # Start
                if t - tmin <= scroll:
                    tmin = tmin
                    tmax = tmin + scroll
                # Middle
                if t - tmin > scroll: # and tmax - t >scroll:
                    tmin = t - scroll
                    tmax = t + 1.
                pyplot.xlim(tmin-0.5, tmax+0.5)
            else:
                # No scrolling , plot entire axis at once.
                pyplot.xlim(np.min(new_times)-0.5, np.max(new_times)+0.5)

            if time_line is None:
                axes[track].plot(new_times, new_data, color=colour, lw=0.8, label = name)
                continue
            pre_new_data = np.ma.masked_where(new_times > time_line, new_data)
            post_new_data = np.ma.masked_where(new_times <= time_line, new_data)

            pyplot.axvline(x=time_line, c = 'black', lw = 0.7)
            axes[track].plot(new_times, pre_new_data, color=colour, lw=1.5, label = name)
            axes[track].plot(new_times, post_new_data, color=colour, lw=1.5, alpha=0.3)

        # edit subplots.
        for pane, ax in numbered_axes.items():
            legend_loc =  self.globals.get('legend_loc', 'lower left')
            #legend = ax.legend(frameon=False, loc=legend_loc)
            legend = ax.legend(loc=legend_loc)
            legend.get_frame().set_linewidth(0.0)

            ax.set_ylabel(ylabels[pane])
            if pane == panes_count:
                ax.set_xlabel('Year')
            else:
                ax.set_xticklabels([])
                ax.axes.get_xaxis().set_visible(False)

        pyplot.suptitle(self.globals['title'])
        print("saving", outpath)
        pyplot.savefig(outpath, dpi=dpi)
        pyplot.close()


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