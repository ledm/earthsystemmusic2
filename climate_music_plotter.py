
import matplotlib as mpl
mpl.use('Agg')

import os
import shutil
from PIL import Image

from climate_music_maker import climate_music_maker
from music_utils import folder, symlink
from matplotlib import pyplot, rc
#import matplotlib.font_manager
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

#def calc_time_line_data(t0, t1, d0, d1, time_line):
#      slope = (raw_data[ind1] - raw_data[ind0])/(raw_times[1] - raw_times[0])
#      intersect = raw_data[ind1] - slope*raw_times[1]
#      extra_times = [time_line, post_new_times.compressed()[0]]



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
        self.textcolor = self.globals.get('text_color', 'black')
        #assert 0

        if self.globals.get('frame_rate', False):

            beats_per_year = self.globals.get('beats_per_year', 1)

            data_rate = self.globals['bpm']/60.*self.globals['notes_per_beat']/beats_per_year # Notes per second ie 5
            # data rate is number of years per second
            # frame rate is number of frames per second.
            frame_rate = self.globals.get('frame_rate', 0.) # ie 30
            data_per_frame = data_rate/ frame_rate  # ie 1.66 years of data per frame
            
            video_timerange = [self.globals['all_times'].min(), self.globals['all_times'].max()  + data_per_frame]
            video_timerange = self.globals.get('video_timerange', video_timerange)
            time_steps = np.arange(
                video_timerange[0],
                video_timerange[1],
                data_per_frame)
            #rint(time_steps[0], time_steps[-1])
            #ssert 0
            self._final_frame = len(time_steps)
            for t, time in enumerate(time_steps):
                print('plotting: frame', t,'time:', time)
                if t % self.globals.get('plot_every', 1) !=0:
                    continue
                print('plotting: frame', t,'time:', time)
                self._make_video_plots_(plot_id=t, time_line=time)
        else:
            # frame_rate = str(bpm/60.*notes_per_beat/plot_every)
            for t, time in enumerate(self.globals['all_times']):
                #continue
                if t % self.globals.get('plot_every', 1) !=0:
                    continue
                self._make_video_plots_(plot_id=t, time_line=time)
     
        if self.globals.get('hold_last_frame', 12):
            self.extend_last_frame()


    def _make_video_plots_(self, plot_id=None, time_line=None):
        image_fold = self.cmm.globals['output_path']
        if not image_fold:
            image_fold = get_image_folder(name)

        if plot_id is None:
            outpath = image_fold+'/video.png'
        else:
            self.video_folder = folder(image_fold+'/video_frames/')

            outpath = self.video_folder+ 'img'+str(plot_id).zfill(6)+'.png'
            self.video_paths.append(outpath)
        if os.path.exists(outpath):
            return
        #outpath = image_fold+'/image_0.png'
        #if os.path.exists(outpath):
        #    continue
        fig = pyplot.figure()
        dpi = self.globals.get('dpi', 250.)
        video_format = self.globals.get('image_res','HD')
        if video_format == 'HD':
            image_size = [1920., 1280.]
            dpi = 250.
        if video_format == '4K':
            image_size = [3840., 2160.]
            dpi = 390.

        #image_size = self.globals.get('image_size', [1920., 1080.])
        fig.set_size_inches(image_size[0]/dpi,image_size[1]/dpi)

        if self.globals.get('background_colour', False):
            fig.patch.set_facecolor(self.globals.get('background_colour', 'white'))

        if self.globals.get('background_image', False):
            datafile = self.globals.get('background_image', False)
            ax1 = fig.add_axes([0.0, 0.0, 1.00, 1.00])
            #ax1.get_xaxis().set_visible(False)
            #ax1.get_yaxis().set_visible(False)
            img = pyplot.imread(datafile)
            ax1.imshow(img, zorder=0)# alpha=0.2) #xtent=[0.5, 8.0, 1.0, 7.0])
            
        axes = {}
        panes  = {}
        numbered_axes = {}
        ylabels={}

        for i, track, in enumerate(sorted(self.tracks.keys())):
            # get pane number, default is alphabetical
            panes[track] = self.tracks[track].get('pane', i+1)
        panes_count = max({pane:True for track, pane in panes.items()}.keys())
        gs1 = gridspec.GridSpec(panes_count, 1)
        gs1.update(wspace=0., hspace=0.15) # set the spacing between axes.

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
            pyplot.sca(axes[track])
            colour = track_dict['colour']
            name = track_dict['longname']
            instrument = track_dict.get('instrument', '')

            # Recalculated data
            recalc_times = sorted(track_dict['recalc_data'].keys())
            recalc_data = [track_dict['recalc_data'][t] for t in recalc_times]
            new_times, new_data = quantize_time(recalc_times, recalc_data)

            # raw dat:
            raw_times = [t for t in sorted(track_dict['raw_data'].keys())]
            raw_data = [track_dict['raw_data'][t] for t in raw_times]

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
            elif self.globals.get('annual_plot', False):
                print('annual_plot', time_line)
                pyplot.xlim(int(time_line), int(time_line)+1.)
            else:
                # No scrolling no annual plot, plot entire axis at once.
                pyplot.xlim(np.min(new_times)-0.5, np.max(new_times)+0.5)

            if time_line is None:
                axes[track].plot(new_times, new_data, color=colour, lw=0.8, label = name)
                continue
            #axes[track].plot(new_times, new_data, color=colour, lw=0., alpha=0.)
            
            pre_new_data = np.ma.masked_where(new_times > time_line, new_data)
            
            if plot_id != self._final_frame -1:
                # no vertical line on the last frame.
                pyplot.axvline(x=time_line, c = self.textcolor, lw = 0.9,zorder=2)
#            else:
#                assert 0
            #pyplot.text(0.1, 0.9, instrument , ha='center', va='center', transform= axes[track].transAxes, size='x-small',c = self.textcolor)

            # Draw up to the time line:
            #lasttime = np.ma.masked_where(pre_new_data.mask, new_times).compressed()#[-1]
            #if len(lasttime):
            #    lasttime = lasttime[-1]
            #    dat = pre_new_data.compressed()[-1]
            #    axes[track].plot([lasttime, time_line], [dat, dat], color=colour, lw=1.5)

            if self.tracks[track].get('plot_range', False):
                axes[track].set_ylim(self.tracks[track].get('plot_range',[None, None]))

            if self.globals.get('show_raw_data', False): 
                future_lines = 'scatter' 
            else: future_lines = 'thin'

            if future_lines == 'scatter':
                post_new_data = np.ma.masked_where(raw_times <= time_line, raw_data)
                if self.tracks[track].get('plot_range', False):
                    post_new_data = np.ma.clip(post_new_data, self.tracks[track]['plot_range'][0],self.tracks[track]['plot_range'][1])
                axes[track].scatter(raw_times, post_new_data, marker='o', s=5, color=colour, label=name )

            if future_lines == 'thin':
                post_new_data = np.ma.masked_where(new_times <= time_line, new_data)
                axes[track].plot(new_times, post_new_data, color=colour, lw=1.5, alpha=0.3)
            
            if future_lines == 'raw_data':
#                future_times = np.array([t for t in sorted(track_dict['data'].keys())])
#                future_times = np.ma.masked_outside(future_times,
#                                                    time_line,
#                                                    track_dict['time_range'][1]).compressed()
#                future_data = np.array([self.tracks[track]['data'][t] for t in future_times])
#                future_times, future_data = quantize_time(future_times, future_data)
#                axes[track].plot(future_times, future_data, color=colour, lw=1.5, alpha=0.3)

                post_new_data = np.ma.masked_where(raw_times <= time_line, raw_data)
                post_new_times = raw_times.copy()

                axes[track].plot(post_new_times, post_new_data, color=colour, lw=1.5, alpha=0.3)

                # Draw from the time line:
                t1 =  np.ma.masked_where(post_new_data.mask, post_new_times).compressed()
                if len(t1): 
                    t1=t1[0]
                    ind1 = np.where(post_new_times==t1)[0]
                    if isinstance(ind1, (list, tuple, np.ndarray, np.ma.array)): 
                        ind1 = ind1[0]
                    ind0 = ind1-1
                    #print(ind0, ind1,type(ind0), type(ind1))
                    #print(ind0, ind1, raw_times[ind0], raw_data[ind0],raw_times[ind1], raw_data[ind1])
                    if raw_data[ind0]:
                        slope = (raw_data[ind1] - raw_data[ind0])/(raw_times[ind1] - raw_times[ind0]) 
                        intersect = raw_data[ind1] - slope*raw_times[ind1]
                        time_line_d = slope*time_line + intersect
                        extra_times = [time_line, raw_times[ind1]]
                        extra_dat = [time_line_d, raw_data[ind1]]
                        axes[track].plot(extra_times, extra_dat, color=colour, lw=1.5, alpha=0.3)
                        #axes[track].scatter(extra_times, extra_dat, marker='o', color=colour) #lpha=0.3)


            # Draw instrument second:
            #axes[track].plot(new_times, new_data, color=colour, lw=0., alpha=0.)
            #axes[track].plot(new_times, pre_new_data, color=colour, lw=1.5, label = instrument)
           
            #ote_times, note_edges = recalc_times
            recalc_times = sorted(track_dict['recalc_data'].keys())
            for t in recalc_times:
                note_edges = track_dict['recalc_times'][t]
                if time_line < note_edges[0]: continue
                value = track_dict['recalc_data'][t]
                #print(t, note_edges, value, time_line)
                if note_edges[0] <= time_line < note_edges[1]:
                    axes[track].plot([note_edges[0], time_line], [value, value], color=colour, lw=2.5,label = instrument, )
                if time_line >= note_edges[1]:
                    axes[track].plot(note_edges, [value, value], color=colour, lw=2.5,label = instrument)

            #assert 0


#            pre_new_data = np.ma.masked_where(new_times > time_line, new_data)
#
#            if self.globals.get('show_raw_data', False):
#                post_new_data = np.ma.masked_where(raw_times <= time_line, raw_data)
#                post_new_times = raw_times.copy()
#
#            else:
#                post_new_data = np.ma.masked_where(new_times <= time_line, new_data)
#                post_new_times = new_times.copy()
#
#            pyplot.axvline(x=time_line, c = self.textcolor, lw = 0.7)
#            axes[track].plot(new_times, pre_new_data, color=colour, lw=1.5, label = name)
#            axes[track].plot(post_new_times, post_new_data, color=colour, lw=1.5, alpha=0.3)
#            if self.tracks[track].get('plot_range', False):
#                axes[track].set_ylim(self.tracks[track].get('plot_range',[None, None]))


        # edit subplots.
        for pane, ax in numbered_axes.items():
            pyplot.sca(ax)
            legend_loc =  self.globals.get('legend_loc', 'lower left')

            # sort or reorder the labels and handles
            current_handles, current_labels = pyplot.gca().get_legend_handles_labels()
            reversed_handles = list(reversed(current_handles))
            reversed_labels = list(reversed(current_labels))
            hands, labs = [], []
            for l,h in zip(reversed_labels,reversed_handles):
                if l not in labs:
                    labs.append(l)
                    hands.append(h)
            #legend = ax.legend(frameon=False, loc=legend_loc)
            legend = ax.legend(hands, labs, loc=legend_loc, framealpha=0. , markerfirst=False)
            legend.get_frame().set_linewidth(0.0)
            for text in legend.get_texts():
                pyplot.setp(text, color = self.textcolor, size='x-small')

            # Hide the right and top spines
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)

            # Only show ticks on the left and bottom spines
            ax.yaxis.set_ticks_position('left')
            ax.xaxis.set_ticks_position('bottom')
            pyplot.yticks(fontsize='x-small')

            ax.set_ylabel(ylabels[pane])
            if pane == panes_count: # ie bottom pane in the stack
                if self.globals.get('annual_plot', False):
                    xlabel = str(int(time_line))
                    ax.set_xticks([int(time_line)+a/12. for a in range(12)])#,labels=None)
                    months= ['J', 'F', 'M', 'A', 'M', 'J','J', 'A', 'S', 'O', 'N', 'D',]
                    months = ['        '+m for m in months]
                    ax.set_xticklabels(months, fontsize='x-small')
                    for tick in ax.get_xticklabels():
                        tick.set_horizontalalignment("left")
                else:
                    xlabel = self.globals.get('xlabel', 'Year')
                ax.set_xlabel(xlabel)
            else:
                ax.set_xticklabels([])
                ax.axes.get_xaxis().set_visible(False)

            if self.globals.get('background_colour', False):
                ax.set_facecolor(self.globals.get('background_colour', 'white'))
            else:
                ax.patch.set_alpha(0.)
            
            # set to a standard colour
            ax.spines['bottom'].set_color(self.textcolor)
            #ax.spines['top'].set_color(self.textcolor)
            #ax.spines['right'].set_color(self.textcolor)
            ax.spines['left'].set_color(self.textcolor)
            ax.tick_params(axis='x', colors=self.textcolor)
            ax.tick_params(axis='y', colors=self.textcolor)
            ax.yaxis.label.set_color(self.textcolor)
            ax.xaxis.label.set_color(self.textcolor)

        # Add Chyron text:
        if self.globals.get('chyron_text',False):
            chryons = self.globals.get('chyron_text',False)
            fig.subplots_adjust(bottom=0.2)
            if self.globals.get('frame_rate', False):
                total_figs = self._final_frame
            else:
                total_figs = len(self.globals['all_times'])
            chy_no = int((float(plot_id)/float(total_figs))*len(chryons))
            chy_fl = (float(plot_id)/float(total_figs))*len(chryons)-chy_no # number beteen 0 and 1
            chy_0 = (chy_no /len(chryons))*total_figs
            chy_p1 = ((chy_no+1) /len(chryons))*total_figs

            #fade in and out:
            fr = self.globals.get('frame_rate', False)
            chy_alpha=1.
            if fr and (plot_id - chy_0)<= fr: # fade in
                chy_alpha = np.abs(plot_id - chy_0)/fr # fade in over one second.

            if fr and (chy_p1 -  plot_id) <= fr: # fade out
                chy_alpha = np.abs(chy_p1 -  plot_id)/fr # fade out over one second.

            pyplot.figtext(0.5,0.1,chryons[chy_no],
                        alpha = chy_alpha,
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontsize='x-small',
                        color=self.textcolor)


        title = self.globals.get('title', '')
        pyplot.suptitle(title,color=self.textcolor, size='medium')

#       if self.globals.get('background_image', False):
#           datafile = self.globals.get('background_image', False)
#           ax1 = fig.add_axes([0.0, 0.0, 1.00, 1.00])
#           #ax1.get_xaxis().set_visible(False)
#           #ax1.get_yaxis().set_visible(False)
#           img = pyplot.imread(datafile)
#           ax1.imshow(img, zorder=0,  alpha=0.2) #xtent=[0.5, 8.0, 1.0, 7.0])


        print("saving", outpath)
        if self.globals.get('background_image', False):
            pyplot.savefig(outpath, dpi=dpi, transparent=True)
        else: pyplot.savefig(outpath, dpi=dpi)
        pyplot.close()

        if self.globals.get('background_image', False):

            background_path =  self.globals.get('background_image', False)
            background = Image.open(background_path).convert(mode='RGBA')
            foreground = Image.open(outpath)
            final = Image.new("RGBA", background.size) 

            final = Image.alpha_composite(final, background,)
            final = Image.alpha_composite(final, foreground,)

            final.save(outpath)



    def _make_data_plots(self,):
        image_fold = self.cmm.globals['output_path']
        if not image_fold:
            image_fold = get_image_folder(name)

        outpath = image_fold+'/add_data.png'
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

        leg = pyplot.legend()
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
    def extend_last_frame(self):
        """
        Copies the last frame for a some seconds (default is 12 seconds).
        #Copy is more reliable that symbolic links in Windows.
        """
        hold_last_frame = self.globals.get('hold_last_frame', 12)

        frame_rate = self.globals.get('frame_rate', 0.) # ie 30
        if not frame_rate:
            frame_rate = str(bpm/60.*notes_per_beat/plot_every)

        last_path =  os.path.abspath(sorted(self.video_paths)[-1])
        last_path_number = int(last_path[-10:-4])

        new_steps = frame_rate * hold_last_frame

        for t in np.arange(new_steps):
            link_path =  self.video_folder+'img'+str(t+last_path_number+1).zfill(6)+'.png'
            print('extend_last_frame', t, last_path, '->', link_path)
            shutil.copy2(last_path, link_path)
