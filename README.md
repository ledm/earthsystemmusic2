


Earth System Music
===================

This is a python toolkit that can  convert csv, netcdf into midi.

This documentation assumes a basic knowledge of python, yaml and music theory. 

Work in Progress.


The bulk of the work is done via yaml files. 

A typical Yaml file for this work would be composed of a "global" section
which sets the global parameters, 
followed by a tracks section, which includes settings for each track.

E

Below is a typical Global section:

```
global:
    name: 'MarineHeatWaves_bass'
    title: 'MarineHeatWaves_bass'
    output_path: 'output/MHW'
    bpm: 120.
    #Notes per beat is actually "years per musical beat". 
    # with weekly L4 data, want 2 data points per chord, or about
    beats_per_year: &beats_per_year_anchor 4 
    notes_per_beat: &notes_per_beat_anchor 1  
    beats_per_chord: &beats_per_chord_anchor 0.5
    quantize: &quantize_anchor 'demi-semi-quaver'

    # graphical options:
    image_res: '4K'  # 4K: 2840 x 2160
    frame_rate: 30
    plot_every: 1  
    video_timerange: [2000., 2020.99999] 
    scroll: 0.
    annual_plot: True  
    final_note_duration: 4
    hold_last_frame: False  # best to have too long than too short here!

    text_color: 'black'
    xlabel: ' '
    legend_loc: 'upper right'
    show_raw_data: True

```

The important settings here are:

- `name`: Name of the piece
- `title`: Title of the piece, to be shown in output images.
- `output_path`: The path to put the MIDI file and other output files.

The musical settings are:

- `bpm`: Beats per minute of the final piece.
- `beats_per_year`: Number of musical beats per year of input data.
- `notes_per_beat`: The number of notes per beat - This should probably always be one. 
- `beats_per_chord`: The number of beats in each chords/scale (see below).
- `quantize`: The musical binning of data, ie semi-quaver is 16 notes per 4 beats.





```
tracks:
  cnrm_temp_bass:
      longname: 'Temperture_bass'
      channel: 0
      units: r'$\degree$C'
      beats_per_year: *beats_per_year_anchor  
      notes_per_beat: *notes_per_beat_anchor
      beats_per_chord: *beats_per_chord_anchor 
      quantize: *quantize_anchor
      scales: &scales_anchor [ # Britneyspears - hit me baby one more time.
        'Cmin', 'Cmin', 'Cmin', 'Cmin', 'Cmin', 'Cmin', 'Cmin', 'Gmaj', 
        'Gmaj', 'Gmaj', 'Gmaj', 'Gmaj', 'Gmaj', 'Gmaj', 'Dmaj', 'Dmaj',
        'Ebmin', 'Ebmin', 'Ebmin', 'Ebmin', 'Ebmin', 'Ebmin',  'Ebmin', 'Ebmin',
        'Fmaj', 'Fmaj', 'Fmaj', 'Fmaj', 'Gmaj', 'Bbmin', 'C5', 'C5',
      ]
      play_new_chords: True
      data_paths: ['csv/CNRM_thetao_con.csv', ]
      volume_paths:  ['csv/CNRM_thetao_con.csv', ]
      time_range: [1976., 2070.99999]
      # type options [ shelve, nc, csv]
      data_type: 'csv'
      data_key:  'thetao_con'
      data_kwargs: []
      instrument: 'Piano'
      music_range: [41, 67]
      # data range: set min/max data range to match music range
      data_range: [22., 33.]
      plot_range: [22., 33.]
        
      moving_average: '0.5 years'
      volume_range: [60, 110]
      colour: '#87CEFA' # 'light blue'
      pane: 1
      y_label: ' ' 

```






