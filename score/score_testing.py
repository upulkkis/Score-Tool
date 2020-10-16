import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_admin_components as dac
from dash.exceptions import PreventUpdate
import dash_daq as daq
import score_component as sc
from dash.dependencies import Input, Output, State, ALL, MATCH
import plotly.graph_objs as go
import visdcc
import base64
import io
import pretty_midi
from textwrap import dedent
import numpy as np
import json
import pickle
from help import get_help
from helpers import dyn_to_vel, get_fft, findPeaks, sort_for_vexflow, vel_to_color
from score import masking_warning_color
from score import feature_slice
from score import score_graphs_from_graph_data
import music21.converter
import music21.midi.translate
from chord import chord_testing, add_chord_element_list, maskingCurve_peakInput
import heapq
from flask_caching import Cache

def score(app, orchestra, cache):

    dummy_fft_size = 22048  # original: 22048
    dropd_color = 'black'
    dropd_back = 'gray'

    image_filename3 = './examples/test_score.png' # Orchestration Analyzer logo
    encoded_image3 = base64.b64encode(open(image_filename3, 'rb').read())

    pianoroll_resolution=10 #In milliseconds
    inst_list=list(orchestra.keys())
    tech_list=['normal']
    dyn_list=['p', 'mf', 'f']
    note_numbers=np.arange(128)
    notenames=[]
    # roll = pretty_midi.PrettyMIDI('./examples/test_score.mid')

    for i in range(128):
        notenames.append(pretty_midi.note_number_to_name(i))


    fig_layout = {
        'title': 'Score',
               'plot_bgcolor': 'black',
               'paper_bgcolor': 'black',
                'font': {
                    'color': 'white'
                },
                'xaxis': {'title': 'Bar',
                          #'rangeslider': {'visible': True},
                          #'rangeselector': {'visible': True},
                          },
                'yaxis': {
                    'tickmode': 'array',
                    'tickvals': np.arange(128),
                    'ticktext': notenames,
                    'range': [36, 96],
                    'nticks': 10,
                    'title': 'note'
                },
                'dragmode': 'pan',
                #'showscale': False,
                #'coloraxis_showscale': False
           }
    fig_config = {
                'displayModeBar': False,
        'scrollZoom': False,
        #'modeBarButtons':{'zoom3d':True}
            }

    trace_template = {
        "type": "heatmap",
        "zmin": 0,
        "zmax": 1,
        'showlegend': True,
        'showscale': False,
        #'opacity': 0.5,
    }
    valid_instruments=[]
    target_lista=[]
    inst_lista=[]
    tech_lista=[]
    onoff_lista=[]
    def add_instruments(midi_data):
        length=len(midi_data.instruments)
        graphs =  [html.Tr([
                  html.Th('Score name'),
                  html.Th('Database name'),
                  html.Th('technique'),
                  html.Th('dynamic'),
                  html.Th('target/orch.'),
                  html.Th('on/off')
                          ])]
        def set_id(set_type, index):
            return {
                'type': set_type,
                'index': index
            }

        from helpers import assign_midi_name
        for i in range(length):

            ### This was an initial check that the miditrack is not empty. Will fail if all tracks are set to instrument 1.

            if midi_data.instruments[i].program != -1: #Changed from 0 to -1 to get all the staves
                instrument = midi_data.instruments[i]
                valid_instruments.append(i)
                score_name = instrument.name
                #Try to guess the instrument according to midi program or the name
                inst_name = assign_midi_name.set_name(instrument.program, instrument.name)
                #inst_lista.append(inst_name)
                tch = 'normal'
                #tech_lista.append(tch)
                dynamics_list = ['from score', 'p', 'mf', 'f']
                onoff = 1
                #onoff_lista.append(onoff)
                target = 0
                #target_lista.append(target)

                graphs.append(html.Tr(children=[
                    html.Th(html.Div(id=set_id('scorename',i), children=score_name,
                                     style={'display': 'inline-block', 'width': '100%'}
                             #style={'display': 'inline-block', 'padding': '8px', 'fontSize': '25px', 'color': 'grey', 'textAlign':'left'}),
                                     )),
                    html.Th(dcc.Dropdown(
                        options=[{'label': val, 'value': val} for val in inst_list],
                        # className='select',
                        value=inst_name,
                        multi=False,
                        id=set_id('instrument_sc', i),
                        style = {'display': 'inline-block', 'width':'100%'}
                        #style={'backgroundColor': dropd_back, 'color': dropd_color, 'display': 'inline-block', 'opacity': 1,
                        #       'border': 'none', 'width': '150px', 'fontSize': '25px', 'bottom': '-10px'},
                    )),
                    html.Th(dcc.Dropdown(
                        options=[{'label': val, 'value': val} for val in tech_list],
                        className='select',
                        value=tch,
                        multi=False,
                        id=set_id('tech_sc',i),
                        style={'display': 'inline-block', 'width':'100%'}
                        #style={'backgroundColor': dropd_back, 'color': dropd_color, 'display': 'inline-block', 'opacity': 1,
                        #       'border': 'none', 'width': '150px', 'fontSize': '25px', 'bottom': '-10px'},
                    )),
                    html.Th(dcc.Dropdown(
                        options=[{'label': val, 'value': val} for val in dynamics_list],
                        className='select',
                        value=dynamics_list[0],
                        multi=False,
                        id=set_id('dyn_sc', i),
                        style={'display': 'inline-block', 'width':'100%'}
                        #style={'backgroundColor': dropd_back, 'color': dropd_color, 'display': 'inline-block', 'opacity': 1,
                        #       'border': 'none', 'width': '150px', 'fontSize': '25px', 'bottom': '-10px'},
                    )),
                    #For target, value is 100+something, for orchestration 0+something :)
                    html.Th(dcc.Dropdown(
                        options=[{'label': 'target', 'value': 100+i}, {'label': 'orchestration', 'value': 0+i}],
                        className='select',
                        value=0+i,
                        multi=False,
                        id=set_id('target_sc',i),
                        style={'display': 'inline-block', 'width':'100%'}
                        #style={'backgroundColor': dropd_back, 'color': dropd_color, 'display': 'inline-block', 'opacity': 1,
                        #       'border': 'none', 'width': '200px', 'fontSize': '25px', 'bottom': '-10px'},
                    )),
                    html.Th(dcc.Dropdown(
                        options=[{'label': 'on', 'value': 1}, {'label': 'off', 'value': 0}],
                        className='select',
                        value=onoff,
                        multi=False,
                        id=set_id('onoff_sc',i),
                        style={'display': 'inline-block', 'width':'100%'}
                        #style={'backgroundColor': dropd_back, 'color': dropd_color, 'display': 'inline-block', 'opacity': 1,
                        #       'border': 'none', 'width': '100px', 'fontSize': '25px', 'bottom': '-10px'},
                    )),
                    #html.Th(html.Div(id="graph_{}".format(i))),
                ]))
        graphs=html.Table(graphs, style={'width': '100%'})
        return graphs

    def add_trace(trace_data, name, color='white'):
        trace_data[np.where(trace_data == 0)] = None #Replace zeros with none
        new_trace=trace_template #load predefined data
        new_trace['colorscale'] = [[0, 'black'], [1, color]]
        new_trace['z'] = trace_data #add data to trace
        new_trace['name'] = name
        return new_trace

    from helpers import constants
    def get_masking(data, peaks):
            #app.logger.info(peaks)
            #app.logger.info(data)
            #S = get_fft.get_fft(data)
            if len(peaks) == 0:
                masking_threshold=np.zeros(107)#-30
                #masking_threshold = map(lambda number: None if number == 0 else number, masking_threshold) #Change zeros to None
                return masking_threshold
            S=np.zeros(22048)+70
            masking_threshold = maskingCurve_peakInput.maskingCurve(S, peaks)  # Calculate the masking curve

            '''
            try:
                masking_threshold = maskingCurve_peakInput.maskingCurve(S, peaks) #Calculate the masking curve
            except:
                #print("Masking calculation fail, using flat masking curve")
                masking_freq = constants.threshold[:, 0]
                masking_threshold = np.zeros(106)-30
            '''
            return masking_threshold


    from score import combine_peaks
    def do3dgraph(midi_data, target, whole_orchestra_pianoroll):
        ##FOR DEBUG:
        target_lista[0]=1 #Force first instrument as target!!

        orch3d=[]
        tar3d=[]

        #For orchesdtration:
        for i in range(len(midi_data.get_piano_roll(pianoroll_resolution)[0, :])):
            sound_slice_o = np.zeros(44100) #Orchestra empty vector
            peaks_o = []
            sound_slice_t = np.zeros(44100) #Target empty vector
            peaks_t = []
            for ind in range(len(valid_instruments)):
                #for orchestration:
                if target_lista[ind]==0 and onoff_lista[ind]==1:
                    valid = valid_instruments[ind]
                    s_inst = inst_lista[ind]
                    s_tech = tech_lista[ind]
                    try:
                        s_slice = whole_orchestra_pianoroll[valid][0][:, i]#[:, i]
                        notenumbers=np.nonzero(s_slice)
                        dynamics=s_slice[notenumbers]
                        #app.logger.info(notenumbers)
                        for p in range(len(notenumbers)):
                            notenumber=notenumbers[p]
                            dynamic=dynamics[p]
                            if dynamic<50:
                                dyny='p'
                            elif dynamic>80:
                                dyny='f'
                            else:
                                dyny='mf'
                            #sound_o =  orchestra[s_inst][s_tech][dyny][notenumber[0]]['data']
                            #sound_slice_o=sound_slice_o+orchestra[s_inst][s_tech][dyny][notenumber[0]]['data']
                            pks = orchestra[s_inst][s_tech][dyny][notenumber[0]]['peaks'] #findPeaks.peaks(get_fft.get_fft(sound_o), notenumber)
                            peaks_o = combine_peaks.combine_peaks(peaks_o, pks)#orchestra[s_inst][s_tech][dyny][notenumber[0]]['peaks'])
                    except:
                        pass
                #for target:
                elif target_lista[ind] == 1 and onoff_lista[ind] == 1:
                    valid = valid_instruments[ind]
                    s_inst = inst_lista[ind]
                    s_tech = tech_lista[ind]
                    try:
                        s_slice = whole_orchestra_pianoroll[valid][0][:, i]  # [:, i]
                        notenumbers = np.nonzero(s_slice)
                        dynamics = s_slice[notenumbers]
                        #app.logger.info(notenumbers)
                        for p in range(len(notenumbers)):
                            notenumber = notenumbers[p]
                            dynamic = dynamics[p]
                            if dynamic < 50:
                                dyny = 'p'
                            elif dynamic > 80:
                                dyny = 'f'
                            else:
                                dyny = 'mf'
                            #sound_t = orchestra[s_inst][s_tech][dyny][notenumber[0]]['data']
                            #sound_slice_t = sound_slice_t + orchestra[s_inst][s_tech][dyny][notenumber[0]]['data']
                            pl, pf = orchestra[s_inst][s_tech][dyny][notenumber[0]]['peaks'] #findPeaks.peaks(get_fft.get_fft(sound_t), notenumber)
                            peaks_t = combine_peaks.combine_peaks(peaks_t, pks)#orchestra[s_inst][s_tech][dyny][notenumber[0]]['peaks'])
                    except:
                        pass
            orch3d.append(get_masking(sound_slice_o, peaks_o))
            if any(sound_slice_t) == False:
                tar3d.append(get_masking(sound_slice_t, peaks_t))
            else:
                tar3d.append(get_masking(sound_slice_t, peaks_t)+10)

        #app.logger.info(orch3d)
        #app.logger.info(tar3d)

        #Set 3d camera direct above:
        camera = dict(
            eye=dict(x=1, y=0., z=2.5)
        )
        layout = {
            'plot_bgcolor': 'black',
            'paper_bgcolor': 'black',
            'font': {
                'color': 'white'
            },#'width': '800', 'height': '200',
            'scene': {
                "aspectratio": {"x": 1, "y": 4, "z": 0.5},
                'camera': camera,
            },

        }
        return dcc.Graph(figure = {'data':[go.Surface(z=orch3d, opacity=1, colorscale= 'Greys', showscale=False),
                                           go.Surface(z=tar3d, opacity=1, colorscale= 'Greens', showscale=False)], 'layout': layout}, config=fig_config)

    @cache.memoize()
    def fetch_midi_piano_scroll(midi_data):
        return midi_data.get_piano_roll(pianoroll_resolution)

    @cache.memoize()
    def cached_note_colors(notes, colors):
        for entry in range(len(notes)):
            # get note or chord of each entry
            note = notes[entry]
            # print('nuotti')
            # print(notes)
            # print('vari')
            # print(colors)
            if colors[entry]:
                colors[entry] = [vel_to_color.color(x) for x in colors[entry]]
            for ind in range(len(note)):
                # convert all to note names and to lower casw
                notes[entry][ind] = pretty_midi.note_number_to_name(notes[entry][ind]).lower()
        return notes, colors


    @cache.memoize()
    def cached_masking_order_idx(orchestration_all_masking_curves, target_masking_curves_array):
        for j in range(len(orchestration_all_masking_curves)):
            if target_masking_curves_array:
                # !! check 15 loudest peaks on target, subtract them from orchestration and check the heaviest masker:
                tgt_peaks = heapq.nlargest(15, range(len(target_masking_curves_array)),
                                           key=target_masking_curves_array.__getitem__)
                orchestration_all_masking_curves[j] = np.subtract(orchestration_all_masking_curves[j][tgt_peaks],
                                                                     np.array(target_masking_curves_array)[
                                                                         tgt_peaks])
                orchestration_all_masking_curves[j] = np.sum(orchestration_all_masking_curves[j])
                # orchestration_all_masking_curves[i][j] = np.subtract(orchestration_all_masking_curves[i][j], np.array(target_masking_curves_array[i]))
            else:
                orchestration_all_masking_curves[j] = np.sum(orchestration_all_masking_curves[j][0:40])
        masking_order_idx = heapq.nlargest(len(orchestration_all_masking_curves),
                                           range(len(orchestration_all_masking_curves)),
                                           key=orchestration_all_masking_curves.__getitem__)
        return masking_order_idx

    @cache.memoize()
    def cached_masking_percent(target_peaks_array, orchestration_masking_curves):
        idx_above = target_peaks_array[1] > np.interp(target_peaks_array[0], constants.threshold[:, 0],
                                                         orchestration_masking_curves)
        if np.count_nonzero(idx_above == True) == 0:
            masking_percent = 100  # If all peaks are under masking threshold, percent is 100
        else:
            masking_percent = 100 - 100 * (np.count_nonzero(idx_above == True) / len(idx_above))

        if not list(target_peaks_array[0]):  # If no peaks are found, percent is NaN
            masking_percent = 0
        return masking_percent

    @cache.memoize()
    def cached_orchestral_calculation(orch_mfcc_array, peaks_o, o_cents, S):
        orch_mfcc_array = np.delete(orch_mfcc_array, 0, axis=0)  # Poistetaan nollat alusta häiritsemästä

        cv = lambda x: np.std(x) / np.mean(x)
        var = np.apply_along_axis(cv, axis=0, arr=orch_mfcc_array)
        var_coeff = np.mean(abs(var))

        orch_mfcc = np.mean(orch_mfcc_array, axis=0)
        o_cents = np.mean(o_cents)
        masking_threshold = maskingCurve_peakInput.maskingCurve(S, peaks_o)  # Calculate the masking curve

        return masking_threshold, orch_mfcc, var_coeff, o_cents

    def do_graph(midi_data, instrument, tech, dyn, tgt, onoff, score_range, bar_offset):
        all_traces = []
        target_pianoroll = []
        orchestration_pianoroll = []
        all_data =  fetch_midi_piano_scroll(midi_data)# Do not set range yet! [:, score_range[0]:score_range[1]]   #Do an overall pianoroll score
        score_length = len(all_data[0,:])
        all_data = all_data[:, score_range[0]:score_range[1]]

        alltrace = add_trace(all_data, 'orchestration')
        all_traces.append(alltrace.copy())

        target_instruments=[]
        target_techs=[]
        target_dyns=[]
        orch_instruments=[]
        orch_techs=[]
        orch_dyns=[]
        # Do separate scores for targets, if they are on
        for ind in range(len(tgt)):
            if onoff[ind]==1 and tgt[ind]>=100: #Remember, target indices are 100+idx, orchestration are 0+idx
                    #Get the instruments piano roll, from range start to end
                t_PR = midi_data.instruments[tgt[ind] - 100].get_piano_roll(pianoroll_resolution)
                    #Check current inst pianoroll length
                t_PR_len = len(t_PR[0,:])
                    #Append zeros to make all piano roll equal length
                t_PR = np.hstack([t_PR, np.zeros([128,score_length-t_PR_len])])

                    #Append all to list and traces
                target_pianoroll.append([t_PR[:, score_range[0]:score_range[1]], midi_data.instruments[tgt[ind]-100].name]) #Append to the list of targets, took away copy()
                trace_copy = t_PR[:, score_range[0]:score_range[1]].copy()
                all_traces.append(add_trace(trace_copy, midi_data.instruments[tgt[ind]-100].name, 'red').copy()) #Add target to traces

                    #Append database instruments and techs into array
                target_instruments.append(instrument[ind])
                target_techs.append(tech[ind])
                target_dyns.append(dyn[ind])
            if onoff[ind]==1 and tgt[ind]<100:
                o_PR = midi_data.instruments[tgt[ind]].get_piano_roll(pianoroll_resolution)
                o_PR_len = len(o_PR[0, :]) #Append zeros to make all piano roll equal length
                o_PR = np.hstack([o_PR, np.zeros([128, score_length - o_PR_len])])
                orchestration_pianoroll.append([o_PR[:, score_range[0]:score_range[1]], midi_data.instruments[tgt[ind]].name].copy())

                orch_instruments.append(instrument[ind])
                orch_techs.append(tech[ind])
                orch_dyns.append(dyn[ind])
        #print(all_traces)
            #Get values where bar changes
        tickvals=midi_data.get_downbeats()[bar_offset[0]:bar_offset[1]]
            #Get offset for first value
        offset=tickvals[0]*pianoroll_resolution
        ticks_for_bar_start = [int(round(i*pianoroll_resolution-offset)) for i in tickvals] #Do the math to get the right place



        #bars =[round(tick*pianoroll_resolution) for tick in tickvals]
        #Orchestration pianoroll first indexes are instrumentation, second 0 is pianoroll, second 1 is instrument name, then is
        #print(np.shape(orchestration_pianoroll[0][0]))
        #bar1 = orchestration_pianoroll[4][0][:,ticks_for_bar_start[0]:ticks_for_bar_start[1]]
        #print(orchestration_pianoroll[4][1])  #Name of the instrument
        #print(len(bar1[0,:])) #Length of the bar in pianoroll indees
        #print(np.shape(bar1))


        ###############
        ## Do Orchestration note array from piano roll
        ###############
        #Go through all the instruments
        orchestration_array = []
        orch_inst_per_instr_array = dict()
        orch_inst_per_instr_array['notes'] = []
        orch_inst_per_instr_array['dyns'] = []
        orch_inst_per_instr_array['inst'] = []
        orch_inst_per_instr_array['tech'] = []
        orch_inst_per_instr_array['highlights'] = []
        orch_dyn_array = []
        name_array = []
        for j in range (len(orchestration_pianoroll)):
            bars = []
            dynamics = []
            orch_inst_per_instr_array['notes'].append([])
            orch_inst_per_instr_array['dyns'].append([])
            orch_inst_per_instr_array['tech'].append(orch_techs[j])
            orch_inst_per_instr_array['inst'].append(orch_instruments[j])
            orch_inst_per_instr_array['highlights'].append([])
            #Go through all the bars
            for i in range (len(ticks_for_bar_start)):
                orch_inst_per_instr_array['highlights'][j].append([])
                bars.append([])
                dynamics.append([])

                @cache.memoize()
                def get_notenumbers(roll_column):
                    return np.nonzero(roll_column) #check from array which notes are played, i.e. the index of the column

                bar = []
                if i<len(ticks_for_bar_start)-1:
                    bar = orchestration_pianoroll[j][0][:,ticks_for_bar_start[i]:ticks_for_bar_start[i+1]]
                else:
                    bar = orchestration_pianoroll[j][0][:, ticks_for_bar_start[i]:]
                #Go through notes in a bar:
                for k in range(len(bar[0, :])):

                    orch_inst_per_instr_array['highlights'][j][i].append('')
                    notenumber = get_notenumbers(bar[:, k])
                    dynamic = bar[notenumber, k] #Get the values of the index, which is the dynamics

                    #Tolist converts numpy type to native python
                    orch_inst_per_instr_array['notes'][j].append(notenumber[0].tolist())

                    #Check if user overrides the dynamics, else take value from score velocity
                    if orch_dyns[j] == 'from score':
                        this_dyn = dynamic[0].tolist()
                    else:
                        d = dyn_to_vel.to_vel(orch_dyns[j])
                        this_dyn = [d, d, d, d, d, d] #add many instances if note is a chord
                    orch_inst_per_instr_array['dyns'][j].append(this_dyn)

                    bars[i].append(list(notenumber[0])) #Push the note numbers to bar, remember to make a list of np.array
                    dynamics[i].append(this_dyn) #Push the dynamics to colors-array, only the first value, same for all the notes in a chord

            name_array.append(orchestration_pianoroll[j][1])
            orchestration_array.append(bars)
            orch_dyn_array.append(dynamics)
        #print(orch_inst_per_instr_array['notes'][0])
        #print(orch_inst_per_instr_array['inst'][0])
        #######
        ## Do orchestration masking graph
        #######
        #go through bars
        orchestration_masking_curves = []
        orchestration_centroids  = []
        orchestration_mfccs = []
        orchestration_var_coeffs = []
        orchestration_all_masking_curves = []
        S = np.ones(dummy_fft_size) + 70 #this is a dummy constant for masking calculation
        for j in range(len(orchestration_array[0])):
            #go through notes
            notes = orchestration_array[0][j]
            for entry in range(len(notes)):

                last_orch_slice=[]
                peaks_o = []
                orch_mfcc_array = np.array(np.zeros(12))
                o_cents = []

                #Empty array for masking slice for each instrument
                momentary_masking_array=[]

                #go through instruments
                for i in range(len(orchestration_array)):

                    #If there's content in entry:
                    if (orchestration_array[i][j][entry]):

                        #Init an empty masking array:
                        chord_masking_array=np.zeros(107)
                        for chordnotes in range(len(orchestration_array[i][j][entry])):
                            #current instrument:
                            inst = orch_instruments[i]

                            #current tech:
                            tch = orch_techs[i]

                            #current dynamic:

                            dyna = orch_dyns[i]
                            if orch_dyns[i]=='from score':
                                #Current dynamic:
                                val = orch_dyn_array[i][j][entry][chordnotes]
                                dyna = assign_dyns.dyns(val)


                            #Current entry:
                            note = orchestration_array[i][j][entry][chordnotes]

                            ## Here are the values to go through:   orchestra[inst][tch][dyna][note]
                            this_orch_slice = [inst, tch, dyna, note]

                            try:
                                peaks, mfcc, centroid, masking = feature_slice.get_feature_slice(inst, tch, dyna, note, orchestra, dummy_fft_size)
                                orch_mfcc_array = np.vstack([orch_mfcc_array,mfcc])

                                peaks_o = combine_peaks.combine_peaks(peaks_o, [peaks[0], peaks[1]])

                                #Get the added placeholder and add masking curves of found notes into it
                                #!!momentary_masking_array[-1].append(masking) #!!

                                #This selects maximum values of each band for notes in chord:
                                chord_masking_array=np.maximum(chord_masking_array, masking)
                            except:
                                print('Out of range notes found')
                        try:
                            o_cents.append(centroid)
                        except:
                            print('out of range notes')
                        momentary_masking_array.append(chord_masking_array)
                    else:
                        momentary_masking_array.append(np.zeros(107))

                #Check if orchestral instruments found and do calculations
                if list(peaks_o):

                    masking_threshold, orch_mfcc, var_coeff, o_cents = cached_orchestral_calculation(orch_mfcc_array, peaks_o, o_cents, S)

                    '''   Try cached                 
                    orch_mfcc_array = np.delete(orch_mfcc_array, 0, axis=0)  # Poistetaan nollat alusta häiritsemästä

                    cv = lambda x: np.std(x) / np.mean(x)
                    var = np.apply_along_axis(cv, axis=0, arr=orch_mfcc_array)
                    var_coeff = np.mean(abs(var))


                    orch_mfcc = np.mean(orch_mfcc_array, axis=0)
                    o_cents = np.mean(o_cents)
                    masking_threshold = maskingCurve_peakInput.maskingCurve(S, peaks_o)  # Calculate the masking curve
                    '''

                    #print('momentary:')
                    #print(momentary_masking_array)
                    #Append all the values into the vectors
                    orchestration_masking_curves.append(masking_threshold)
                    orchestration_mfccs.append(orch_mfcc)
                    orchestration_var_coeffs.append(var_coeff)
                    orchestration_centroids.append(o_cents)
                    orchestration_all_masking_curves.append(momentary_masking_array) #!!
                    #print('ork pituus:')
                    #print(len(momentary_masking_array))
                else:
                    orchestration_masking_curves.append(np.zeros(107)-20)
                    orchestration_mfccs.append(np.zeros(12))
                    orchestration_var_coeffs.append(0)
                    orchestration_centroids.append(0)
                    orchestration_all_masking_curves.append(momentary_masking_array)  # !!


        #Stave list for score_component

        #Go through instruments
        #for i in range(len(orchestration_array)):
        #    name=name_array[i]
        #    clef='treble'

        ##########################
        ### Do note array from target pianoroll
        ########################

        #Go through all the instruments
        target_array = []
        target_dyn_array = []
        target_name_array = []
        target_inst_per_instr_array = dict()
        target_inst_per_instr_array['notes'] = []
        target_inst_per_instr_array['dyns'] = []
        target_inst_per_instr_array['inst'] = []
        target_inst_per_instr_array['tech'] = []
        for j in range (len(target_pianoroll)):
            bars = []
            dynamics = []
            target_inst_per_instr_array['notes'].append([])
            target_inst_per_instr_array['dyns'].append([])
            target_inst_per_instr_array['inst'].append(target_instruments[j])
            target_inst_per_instr_array['tech'].append(target_techs[j])
            #Go through all the bars
            for i in range (len(ticks_for_bar_start)):
                bars.append([])
                dynamics.append([])
                bar = []
                if i<len(ticks_for_bar_start)-1:
                    bar = target_pianoroll[j][0][:,ticks_for_bar_start[i]:ticks_for_bar_start[i+1]]
                else:
                    bar = target_pianoroll[j][0][:, ticks_for_bar_start[i]:]
                #Go through notes in a bar:
                for k in range(len(bar[0, :])):

                    notenumber = np.nonzero(bar[:, k]) #check from array which notes are played, i.e. the index of the column
                    dynamic = bar[notenumber, k] #Get the values of the index, which is the dynamics

                    target_inst_per_instr_array['notes'][j].append(notenumber[0].tolist())

                    if target_dyns[j] == 'from score':
                        this_dyn=dynamic[0].tolist()
                    else:
                        d = dyn_to_vel.to_vel(target_dyns[j])
                        this_dyn = [d, d, d, d, d, d]  # add many instances if note is a chord
                    target_inst_per_instr_array['dyns'][j].append(this_dyn)

                    bars[i].append(list(notenumber[0])) #Push the note numbers to bar, remember to make a list of np.array
                    dynamics[i].append(this_dyn) #Push the dynamics to colors-array, only the first value, same for all the notes in a chord

            target_name_array.append(target_pianoroll[j][1])
            target_array.append(bars)
            target_dyn_array.append(dynamics)

        #######
        ## Do Target feature graph
        #######
        # go through bars

        #To prevent error:
        if not target_array:
            target_array = [[]]

        target_peaks_array = []
        target_centroids = []
        target_mfccs = []
        target_var_coeffs = []
        target_masking_curves_array = []

        S = np.ones(dummy_fft_size) + 70  # this is a dummy constant for masking calculation
        for j in range(len(target_array[0])):
            # go through notes
            notes = target_array[0][j]
            for entry in range(len(notes)):

                last_orch_slice = []
                peaks_t = []
                target_mfcc_array = np.array(np.zeros(12))
                t_cents = []
                # go through instruments
                for i in range(len(target_array)):

                    # If there's content in entry:
                    if (target_array[i][j][entry]):

                        for chordnotes in range(len(target_array[i][j][entry])):
                            # current instrument:
                            inst = target_instruments[i]

                            # current tech:
                            tch = target_techs[i]

                            # current dynamic:

                            dyna = target_dyns[i]
                            if target_dyns[i] == 'from score':
                                # Current dynamic:
                                val = target_dyn_array[i][j][entry][chordnotes]
                                if val < 70:
                                    dyna = 'p'
                                elif val < 90:
                                    dyna = 'mf'
                                else:
                                    dyna = 'f'

                            # Current entry:
                            note = target_array[i][j][entry][chordnotes]

                            ## Here are the values to go through:   orchestra[inst][tch][dyna][note]
                            this_target_slice = [inst, tch, dyna, note]

                            try:
                                peaks, mfcc, centroid, masking = feature_slice.get_feature_slice(inst, tch, dyna, note, orchestra)

                                target_mfcc_array = np.vstack([target_mfcc_array, mfcc])
                                t_cents.append(centroid)
                                peaks_t = combine_peaks.combine_peaks(peaks_t, [peaks[0], peaks[1]])
                            except:
                                print('Out of range notes found')
                                #pass


                # Check if target instruments found and do calculations
                if list(peaks_t):

                    masking_threshold, target_mfcc, var_coeff, t_cents = cached_orchestral_calculation(target_mfcc_array,
                                                                                                     peaks_t, t_cents,
                                                                                                     S)
                    '''
                    target_mfcc_array = np.delete(target_mfcc_array, 0, axis=0)  # Poistetaan nollat alusta häiritsemästä

                    cv = lambda x: np.std(x) / np.mean(x)
                    var = np.apply_along_axis(cv, axis=0, arr=target_mfcc_array)
                    var_coeff = np.mean(abs(var))

                    target_mfcc = np.mean(target_mfcc_array, axis=0)
                    t_cents = np.mean(t_cents)
                    masking_threshold = maskingCurve_peakInput.maskingCurve(S, peaks_t)  #!! Calculate the masking curve
                    '''

                    # Append all the values into the vectors
                    target_peaks_array.append(peaks_t)
                    target_mfccs.append(target_mfcc)
                    target_var_coeffs.append(var_coeff)
                    target_centroids.append(t_cents)
                    target_masking_curves_array.append(masking_threshold) #!!
                else:
                    target_peaks_array.append([[],[]])
                    target_mfccs.append(np.zeros(12))
                    target_var_coeffs.append(0)
                    target_centroids.append(0)
                    target_masking_curves_array.append(np.ones(107))  # !!

        #Map target peaks on masking graph for 3d
        target_peaks_over_masking=[]
        for k in range(len(target_peaks_array)):
            momentary_peaks=[]
            for i in range(len(constants.threshold[:, 0])):
                peak_on_band = -20
                if list(target_peaks_array[k]):
                    for peak in range(len(target_peaks_array[k][0])):
                        if list(target_peaks_array[k][0]):
                            if i>0:
                                if target_peaks_array[k][0][peak]< \
                                        constants.threshold[:, 0][i] and target_peaks_array[k][0][peak]> \
                                        constants.threshold[:, 0][i - 1]: #If target peak freq is within the band
                                    if target_peaks_array[k][1][peak]>peak_on_band: #Get the highest peak on band
                                        peak_on_band=target_peaks_array[k][1][peak]
                momentary_peaks.append(peak_on_band)
            target_peaks_over_masking.append(momentary_peaks)

        target_masking_percent_array = []
        ### Calculate target masking at all notes
        for i in range (len(target_peaks_array)):

            masking_percent = cached_masking_percent(target_peaks_array[i], orchestration_masking_curves[i])

            ''' try cached!
            idx_above = target_peaks_array[i][1] > np.interp(target_peaks_array[i][0], constants.threshold[:, 0], orchestration_masking_curves[i])
            if np.count_nonzero(idx_above == True) == 0:
                masking_percent = 100 #If all peaks are under masking threshold, percent is 100
            else:
                masking_percent = 100 - 100 * (np.count_nonzero(idx_above == True) / len(idx_above))

            if not list(target_peaks_array[i][0]): #If no peaks are found, percent is NaN
                masking_percent = 0
            '''

            target_masking_percent_array.append(masking_percent)
        #!!
        # print('pituudet:')
        # print(len(orchestration_all_masking_curves))
        # print(len(orchestration_all_masking_curves[0]))
        # print(len(target_masking_curves_array))
        # print(len(orch_inst_per_instr_array['highlights']))
        # print(len(orch_inst_per_instr_array['highlights'][0][0]))
        #Go through individual orchestration masking curves: #!!
        for i in range(len(orchestration_all_masking_curves)):
            #Go through curves in every note entry #!!
            if target_masking_curves_array:
                cached_tgt_array = target_masking_curves_array[i]
            else:
                cached_tgt_array = []
            masking_order_idx = cached_masking_order_idx(orchestration_all_masking_curves[i], cached_tgt_array)
            ''' Try cached!
            for j in range(len(orchestration_all_masking_curves[i])):
                if target_masking_curves_array:
                    #!! check 15 loudest peaks on target, subtract them from orchestration and check the heaviest masker:
                    tgt_peaks = heapq.nlargest(15, range(len(target_masking_curves_array[i])), key=target_masking_curves_array[i].__getitem__)
                    orchestration_all_masking_curves[i][j] = np.subtract(orchestration_all_masking_curves[i][j][tgt_peaks], np.array(target_masking_curves_array[i])[tgt_peaks])
                    orchestration_all_masking_curves[i][j] = np.sum(orchestration_all_masking_curves[i][j])
                    #orchestration_all_masking_curves[i][j] = np.subtract(orchestration_all_masking_curves[i][j], np.array(target_masking_curves_array[i]))
                else:
                    orchestration_all_masking_curves[i][j] = np.sum(orchestration_all_masking_curves[i][j][0:40])
            
            masking_order_idx = heapq.nlargest(len(orchestration_all_masking_curves[i]), range(len(orchestration_all_masking_curves[i])), key=orchestration_all_masking_curves[i].__getitem__)
            '''
            #!!print('indeksit')
            # print(masking_order_idx)
            # print(orch_inst_per_instr_array['highlights'][masking_order_idx[0]])
            #print(len(orch_inst_per_instr_array['highlights'][masking_order_idx[0]]))
            if masking_order_idx and i<len(orch_inst_per_instr_array['highlights'][masking_order_idx[0]][0]):
                orch_inst_per_instr_array['highlights'][masking_order_idx[0]][0][i] = 'red'
                if len(masking_order_idx)>1:
                    orch_inst_per_instr_array['highlights'][masking_order_idx[1]][0][i] = 'magenta'
                    if len(masking_order_idx) > 2:
                        orch_inst_per_instr_array['highlights'][masking_order_idx[2]][0][i] = 'yellow'
            #!!
        #print(orchestration_all_masking_curves)

        ##Divide masking percent array into bars and do color array:
        orchestration_masker_colors_array = [] #!!
        target_masking_percent_array_with_bars = []
        bar = []
        bar_orch_color=[]
        bar_number=0
        j=0;
        for i in range(len(target_masking_percent_array)):

            #Look how many percent target is masked and assign color according to that
            hearing_value = target_masking_percent_array[i]
            masking_color = masking_warning_color.color(hearing_value)
            bar.append(masking_color)

            list_of_instruments = []
            instrument_colors = []
            #check the instrumentation on current slice

            #!! if j<len(orchestration_all_masking_curves)-1:
            #     for instr in range (len(orchestration_all_masking_curves[j])):
            #         largest_note_masking_value = 0;
            #         #Check the notes of instrument in current slice
            #         for inst_notes in range(len(orchestration_all_masking_curves[j][instr])):
            #
            #             # Calculate the masking amount on specific bands from masking curve:
            #             value = sum(orchestration_all_masking_curves[j][instr][inst_notes][5:20])
            #
            #             if value>largest_note_masking_value:
            #                 largest_note_masking_value=value
            #             #list_of_instruments[-1].append(sum(orchestration_all_masking_curves[j][instr][inst_notes][2:40]))
            #             #orchestration_all_masking_curves[j][instr][inst_notes]
            #
            #         #This list holds masking values for all instruments
            #         list_of_instruments.append(largest_note_masking_value)
            #         #This list has the same shape as masking values list, but contains colors
            #         if hearing_value >= 70:
            #             #orch_inst_per_instr_array['highlights'][instr][bar_number][i] = 'black'
            #             instrument_colors.append('black')
            #         else:
            #             #orch_inst_per_instr_array['highlights'][instr][bar_number][i] = ''
            #             instrument_colors.append('')
            #
            #     if hearing_value >= 70:
            #         #Assign colors according to the masking values of all instruments:
            #         if len(orchestration_all_masking_curves[j]) == 1:
            #             instrument_colors[0]='red'
            #             orch_inst_per_instr_array['highlights'][0][bar_number][i] = 'red'
            #         elif len(orchestration_all_masking_curves[j]) == 2:
            #             instrument_colors[0]='magenta'
            #             instrument_colors[1]='magenta'
            #             orch_inst_per_instr_array['highlights'][0][bar_number][i] = 'magenta'
            #             orch_inst_per_instr_array['highlights'][1][bar_number][i] = 'magenta'
            #             index_max = max(range(len(list_of_instruments)), key=list_of_instruments.__getitem__)
            #             instrument_colors[index_max]='red'
            #             orch_inst_per_instr_array['highlights'][index_max][bar_number][i]='red'
            #         elif len(orchestration_all_masking_curves[j]) > 2:
            #             three_largest_idx = heapq.nlargest(3, range(len(list_of_instruments)), key=list_of_instruments.__getitem__)
            #             instrument_colors[three_largest_idx[0]] = 'red'
            #             instrument_colors[three_largest_idx[1]] = 'magenta'
            #             instrument_colors[three_largest_idx[2]] = 'yellow'
            #             orch_inst_per_instr_array['highlights'][three_largest_idx[0]][bar_number][i]='red'
            #             orch_inst_per_instr_array['highlights'][three_largest_idx[1]][bar_number][i]='magenta'
            #             orch_inst_per_instr_array['highlights'][three_largest_idx[2]][bar_number][i]='yellow'
            #
            #!! bar_orch_color.append(instrument_colors)


            j += 1
            if i+1 in ticks_for_bar_start:
                target_masking_percent_array_with_bars.append(bar)
                #!!orchestration_masker_colors_array.append(bar_orch_color)
                bar_number += 1
                j=0
                bar=[]
                bar_orch_color=[]

        #Add two empty bars in the end to avoid errors (bad programming, I know)
        target_masking_percent_array_with_bars.append(bar)
        #!!orchestration_masker_colors_array.append(bar_orch_color)
        target_masking_percent_array_with_bars.append(bar)
        #!!orchestration_masker_colors_array.append(bar_orch_color)

        ################
        ### Do orchestration stave_list for pianoroll-component
        ################
        # Go through bars
        from helpers import assign_clef
        stave_list = []
        for j in range(len(orchestration_array[0])):

            bars = []
            # Go through instruments
            for i in range(len(orchestration_array)):
                name = orch_instruments[i]
                clef = assign_clef.clef(name)
                # get the note array of current instrument
                notes, colors = cached_note_colors(orchestration_array[i][j], orch_dyn_array[i][j])

                ''' Try cached!
                notes = orchestration_array[i][j]
                colors = orch_dyn_array[i][j]
                for entry in range(len(notes)):
                    # get note or chord of each entry
                    note = notes[entry]
                    # print('nuotti')
                    # print(notes)
                    # print('vari')
                    # print(colors)
                    if colors[entry]:
                        colors[entry] = [vel_to_color.color(x) for x in colors[entry]]
                    for ind in range(len(note)):
                        # convert all to note names and to lower casw
                        notes[entry][ind] = pretty_midi.note_number_to_name(notes[entry][ind]).lower()
                '''

                # notes = [pretty_midi.note_number_to_name(i).lower() for i in notes]
                #!! if  orchestration_masker_colors_array[j]:
                #     #print(orchestration_masker_colors_array[j])
                #     highlights = orch_inst_per_instr_array['highlights'][i][j] #list(list(zip(*orchestration_masker_colors_array[j]))[i])
                # else:
                #!!     highlights = []
                # print('tahti:')
                # print(name)
                # print(notes)
                # print(orch_inst_per_instr_array['highlights'][i][j])
                bar = {'name': name, 'clef': clef, 'notes': notes, 'colors': colors, 'highlights': orch_inst_per_instr_array['highlights'][i][j]} #!!, 'highlights': highlights
                bars.append(bar)
            stave_list.append(bars)

        #####
        ##Append Target into score with masking information
        #####
        for j in range(len(target_array[0])):

            bars = []
            # Go through instruments
            for i in range(len(target_array)):
                name = target_instruments[i]
                clef = assign_clef.clef(name)
                # get the note array of current instrument
                notes = target_array[i][j]
                for entry in range(len(notes)):
                    #get note or chord of each entry
                    note = notes[entry]
                    for ind in range(len(note)):
                        #convert all to note names and to lower case
                        notes[entry][ind]=pretty_midi.note_number_to_name(notes[entry][ind]).lower()
                #notes = [pretty_midi.note_number_to_name(i).lower() for i in notes]
                bar = {'name': name, 'clef': clef, 'notes': notes, 'colors': target_masking_percent_array_with_bars[j]} #Color masked notes red
            stave_list[j].insert(0, bar)

        #Calculate target mfcc distance
        mfcc_distance_vector=[]
        for i in range(len(target_mfccs)):
            #Calculate euclidian distance of orchestration and target
            mfcc_distance=np.linalg.norm(orchestration_mfccs[i][1:]-target_mfccs[i][1:])
            if target_mfccs[i].all() == 0:
                mfcc_distance=0
            mfcc_distance_vector.append(mfcc_distance)

        analyzed_material = {'orchestration': orch_inst_per_instr_array, 'target': target_inst_per_instr_array}

        #There is for some reason extra bar at the end of stave list, this will take it out
        if len(stave_list)>1:
            stave_list.pop(-1)

        #Collect all data
        graph_data = dict()
        graph_data['stave_list']=stave_list
        graph_data['bar_offset']=bar_offset
        graph_data['ticks_for_bar_start']=ticks_for_bar_start
        graph_data['instrument']=instrument
        graph_data['downbeats']=midi_data.get_downbeats()
        graph_data['score_length']=len(all_data[0,:])
        graph_data['orchestration_masking_curves']=orchestration_masking_curves
        graph_data['target_peaks_over_masking']=target_peaks_over_masking
        graph_data['target_masking_percent_array']=target_masking_percent_array
        graph_data['orchestration_var_coeffs']=orchestration_var_coeffs
        graph_data['orchestration_centroids']=orchestration_centroids
        graph_data['target_centroids']=target_centroids
        graph_data['mfcc_distance_vector']=mfcc_distance_vector
        graph_data['analyzed_material']=analyzed_material
        graph_data['all_traces']=all_traces

        return graph_data


    @app.callback(
        [Output('3d_graph', 'config'),
        Output('3d_graph', 'id'),
         ],
        [Input('zoom_enable', 'checked')],
        [State('3d_graph', 'config'),
         State('3d_graph', 'id'),
         #State('3d_graph', 'figure'),
         ]
    )
    def set_mouse_zoom(check, config, id):

        if check:
            config['scrollZoom'] = True
            id='zoom_enabled'
        else:
            config['scrollZoom'] = False
            id = '3d_graph'
        return [config, id]

    @app.callback(
        [Output('zoom_enabled', 'config'),
         Output('zoom_enabled', 'id'),
         ],
        [Input('zoom_enable', 'checked')],
        [State('zoom_enabled', 'config'),
         State('zoom_enabled', 'id'),
         # State('3d_graph', 'figure'),
         ]
    )
    def set_mouse_zoom(check, config, id):

        if not check:
            config['scrollZoom'] = False
            id = '3d_graph'
        #print(config['scrollZoom'])
        return [config, id]


    examples = ['Test_score', 'Brahms', 'Chamber music', 'Own works', 'Push here to load an example score']
    slider_range=[]

    ############################################
    ### Intial box to upload or choose score ###
    ############################################

    score_load_help = html.Details([html.Summary('Score load help'), html.Div(html.Div('Upload file loads nearly any open-source notation format (MusicXML, Midi, Lilypond etc.). If you are using Sibelius or Finale, choose export -> Music-XML or export -> midi (be sure to switch human playback off, as it creates unnecessary mididata). You can also write score in text editor (Word, Pages etc.) using ABC notation (check wiki for syntax). There are also pre-loaded example scores in dropdown menu, such as test_score to test the program functionality and the whole 1st part of the Brahms violin concerto.'),
        style={'border': '4px solid sienna', 'borderRadius': '5px', 'margin': '10px', 'padding':'5px'})])

    empty_content = html.Div([
        html.Div('Assign target and database instruments for your score',
                 style={'textAlign': 'center', 'fontSize': 24}),
        #add_instruments(midifile),
        html.Div('Select range to analyze', style={'textAlign': 'center', 'fontSize': 24}),
        html.Div('Caution! Analysis of 10 bars takes about 25-35sec.',
                 style={'textAlign': 'center', 'fontSize': 12, 'color': 'red'}),
        html.Div('bars', style={'textAlign': 'center', 'color': 'grey'}),
        dcc.RangeSlider(
            id='score_range',
            min=1,
            max=2,
            step=1,
            value=[1, 2],
            pushable=1,
            dots=True,
            updatemode='drag',
            tooltip={
                'always_visible': False,
                'placement': 'bottom'
            },
            # marks={
            #     0:'0',
            #     5:'5',
            #     10:'10'
            # }
        ),
        html.Div(id='slider_return_score', style={'textAlign': 'center', 'color': 'sienna'}),

        # html.Button(id='analyze_button', n_clicks=0, children='Push here for analysis', className='button',),
        html.Div('Before clicking, make sure your parameters are correct',
                 style={'textAlign': 'center', 'fontSize': 24}),
        dbc.Button(id='analyze_button', n_clicks=0, children='Push here for analysis', block=True),
        dbc.Row([
            dbc.Col(dbc.Button(id='pause_analyze', n_clicks=0, children='Pause analysis', block=True)),
            dbc.Col(dbc.Button(id='continue_analyze', n_clicks=0, children='Continue analysis', block=True)),
            dbc.Col(dbc.Button(id='reset_analyze', n_clicks=0, children='Reset analysis', block=True)),
            dbc.Col(dbc.Button(id='save_analyze', n_clicks=0, children='Save current analysis', block=True)),
        ]),
        html.A('', id='score_download', download="data.score", href="", target="_blank", ),
        visdcc.Run_js(id='javascript_score'),
        visdcc.Run_js(id='javascript_download'),
        html.Div(id='calc_container', children=[html.Br(), dbc.Progress('0', value=0, id='calc_time', color='warning',
                                                                        striped=True, animated=True,
                                                                        style={'height': 30})]),
        html.Div(id='wait_graph'),

    ], style={'display':'none'})

    analyzer_layout = dac.Box([dac.BoxHeader(title='Load and setup score'),
                               dac.BoxBody(
        html.Div(children=[
            score_load_help,
        dbc.Row([dbc.Col(
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('select score file (MusicXml, etc...)'),
            ],
                style={
                    'textAlign': 'center',
                    #'color': 'grey'
                }
            ),
            style={
                'width': '100%',
                'height': '40px',
                'lineHeight': '40px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                #'margin': '10px',
                'backgroundColor': 'white',
                #'color': 'grey'
            },
            multiple=False
        ),
        width=4),
        dbc.Col(
            dcc.Upload(
                id='upload-score',
                children=html.Div([
                    'Upload ',
                    html.A('saved analysis'),
                ],
                    style={
                        'textAlign': 'center',
                        # 'color': 'grey'
                    }
                ),
                style={
                    'width': '100%',
                    'height': '40px',
                    'lineHeight': '40px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    # 'margin': '10px',
                    'backgroundColor': 'white',
                    # 'color': 'grey'
                },
                multiple=False
            ),
            #html.Div('Or', style={'textAlign':'center', 'height':'40px', 'fontSize':20}),
        width=4),
            dbc.Col([ #html.Br(style={'height':'1px'}),
            dcc.Dropdown(
            options=[{'label': val, 'value': val} for val in examples],
            value=examples[-1],
            multi=False,
            id='score_select',
            style={'display': 'inline-block', 'opacity': 1,
                   'width': '100%', 'fontSize': '20px'},
        )],width=4, style={'height':'40px', 'topMargin':'10px'}, #Dropbox column params
            )
        ]),
        html.Div(id='load_return', style={'margin':10}, children=empty_content,),
        #html.Div(add_instruments(roll)),

        html.Div(id='3d', style={'width': '100%'}),
        html.Div(id='valikot_score'),
        html.Div(id='testi_score',
                 style={
                     'color': 'grey'})
    ],
    ))],width=12) #Box width

    def make_box(title, content, closed=False):
        box=dac.Box([
            dac.BoxHeader(title=title),
            dac.BoxBody(content)
        ], width=12, collapsed=closed, style={})
        return box

    def empty_graphs():
        empty = {'clef': 'treble', 'name': '', 'notes': [], 'colors': []}
        graph_data = dict()
        graph_data['stave_list'] = [[empty]]
        graph_data['bar_offset'] = [0, 0]
        graph_data['ticks_for_bar_start'] = []
        graph_data['instrument'] = []
        graph_data['downbeats'] = []
        graph_data['score_length'] = 0
        graph_data['orchestration_masking_curves'] = []
        graph_data['target_peaks_over_masking'] = []
        graph_data['target_masking_percent_array'] = []
        graph_data['orchestration_var_coeffs'] = []
        graph_data['orchestration_centroids'] = []
        graph_data['target_centroids'] = []
        graph_data['mfcc_distance_vector'] = []

        orch_inst_per_instr_array = dict()
        orch_inst_per_instr_array['notes'] = []
        orch_inst_per_instr_array['dyns'] = []
        orch_inst_per_instr_array['inst'] = []
        orch_inst_per_instr_array['tech'] = []

        target_inst_per_instr_array = dict()
        target_inst_per_instr_array['notes'] = []
        target_inst_per_instr_array['dyns'] = []
        target_inst_per_instr_array['inst'] = []
        target_inst_per_instr_array['tech'] = []

        graph_data['analyzed_material'] = {'orchestration': orch_inst_per_instr_array,
                                           'target': target_inst_per_instr_array}
        graph_data['all_traces'] = []

        return graph_data

    def do_analyze_boxes():

        graph_data = empty_graphs()

        names = ['Orchestral score with target on top', 'Target masking percent in score',
                 'Homogenuity of the orchestration', 'Orchestration and target centroid comparison',
                 'Target sound color distance from orchestration', '3d graph of masking',
                 'Registral representation of the score']
        closed = [False, False, False, False, False, False, False]  # Close pianoroll in the start?
        analyzer_graphs = score_graphs_from_graph_data.score_graphs_from_graph_data(graph_data)
        boxes = []
        material = analyzer_graphs[-1]  # This is a dict containing analyzed score and target notes and dyns

        for i in range(len(analyzer_graphs) - 1):
            boxes.append(make_box(names[i], analyzer_graphs[i], closed[i]))

        #Hide the last graph, as it is currently not needed
        boxes[-1].style={'display':'none'}
        return boxes

    def define_score_instruments(midifile, name):
        return_content=html.Div([
        html.Div('Assign target and database instruments for your score', style={'textAlign':'center', 'fontSize':24}),
        add_instruments(midifile),
        html.Div('Select range to analyze', style={'textAlign': 'center', 'fontSize': 24}),
        html.Div('Caution! Analysis of 10 bars takes about 25-35sec.', style={'textAlign': 'center', 'fontSize': 12, 'color':'red'}),
        html.Div('bars', style={'textAlign': 'center', 'color': 'grey'}),
        dcc.RangeSlider(
            id='score_range',
            min=1,
            max=len(midifile.get_downbeats()),
            step=1,
            value=[1, len(midifile.get_downbeats())],
            pushable=1,
            dots=True,
            updatemode='drag',
            tooltip={
                'always_visible': False,
                'placement': 'bottom'
            },
            # marks={
            #     0:'0',
            #     5:'5',
            #     10:'10'
            # }
        ),
        html.Div(id='slider_return_score', style={'textAlign': 'center', 'color': 'sienna'}),

        #html.Button(id='analyze_button', n_clicks=0, children='Push here for analysis', className='button',),
        html.Div('Before clicking, make sure your parameters are correct', style={'textAlign': 'center', 'fontSize': 24}),
        dbc.Button(id='analyze_button', n_clicks=0, children='Push here for analysis', block=True),
        dbc.Row([
            dbc.Col(dbc.Button(id='pause_analyze', n_clicks=0, children='Pause analysis', block=True)),
            dbc.Col(dbc.Button(id='continue_analyze', n_clicks=0, children='Continue analysis', block=True)),
            dbc.Col(dbc.Button(id='reset_analyze', n_clicks=0, children='Reset analysis', block=True)),
            dbc.Col(dbc.Button(id='save_analyze', n_clicks=0, children='Save current analysis', block=True)),
        ]),
            html.A('', id='score_download', download="data.score", href="", target="_blank",),
            visdcc.Run_js(id='javascript_score'),
            visdcc.Run_js(id='javascript_download'),
            html.Div(id='calc_container', children=[html.Br(), dbc.Progress('0', value=0, id='calc_time', color='warning', striped=True, animated=True, style={'height':30})]),
            html.Div(id='wait_graph'),

        ])

        if name == 'test_score':
            show_score = html.Details([html.Summary('Show score', className='button'), html.Div(
                html.Div(html.Div(children=[
                    html.Img(src='data:image/png;base64,{}'.format(encoded_image3.decode()), style={'width': '100%'})],
                                  style={'textAlign': 'center'})),
            )])
            return [show_score, return_content]
        return return_content

    @app.callback(
        [Output('slider_return_score', 'children'),
         Output('wait_time', 'children'),
         Output('analyze_button', 'children'),
         ],
        [Input('score_range', 'value')])
    def range_output(value):
        text="Analysis range set from bar {} to {}, analysing {} bars".format(value[0], value[1], value[1]-value[0])
        t = (value[1]-value[0])*5
        if t<60:
            est_t=str(int(t))+"s"
        else:
            m = int(t/60)
            s = t%60
            est_t = str(m)+"min. "+str(s)+"s"
        est = 'Click to analyze, calculation time: {}'.format(est_t)
        return [text, t, est]

    from helpers import assign_dyns
    ###
    #Send modal of current orchestration to the screen
    ###
    @app.callback(
    [Output('scoremodal', 'is_open'),
     Output('outer_orchestration_dropdown{}'.format('score'), 'children')],
        [Input({'type': 'a_graph', 'index': ALL}, 'clickData'),
         Input('pianoroll_graph', 'onClick'),
         ], #Input('3d_graph', 'clickData'),], #Click from 3d disturbs panning!!
        [State('hidden_material', 'children'),
         State('user_uuid', 'children')])
    def check_orchestration(click, onclick, material, user_uuid):
        point=[]
        myClick = None
        #if click3d!=None:
        #    point=click3d['points'][0]['y']

        #Check which graph fired
        ctx = dash.callback_context  # Callback context to recognize which input has been triggered
        if not ctx.triggered:
            raise PreventUpdate
        else:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if input_id!='3d_graph' and input_id!='pianoroll_graph': #Count out 3d graph
            idx=int(input_id[9]) #Get the index number from string
            myClick=click[idx-1] #Convert to python indexing by -1 :)

        if myClick!=None:
            point = myClick['points'][0]['x']

        if input_id=='pianoroll_graph':
            if onclick:
                point = onclick['note_index']

        if point:
            #print(type(material))
            # material = json.loads(material)

            material = json.loads(cache.get(user_uuid + 'material'))

            orchestration = []
            for i in range(len(material['orchestration']['notes'])):
                notes = material['orchestration']['notes'][i][point]
                if list(notes):
                    for note in notes:
                        dyny = assign_dyns.dyns(int(material['orchestration']['dyns'][i][point][0]))
                        current_entry = dict()
                        current_entry['inst'] = material['orchestration']['inst'][i]
                        current_entry['tech'] = material['orchestration']['tech'][i]
                        current_entry['dynamic'] = dyny
                        current_entry['note'] = note
                        current_entry['target'] = False
                        current_entry['onoff'] = True
                        orchestration.append(current_entry)

            for i in range(len(material['target']['notes'])):
                notes = material['target']['notes'][i][point]
                if list(notes):
                    for note in notes:
                        dyny = assign_dyns.dyns(int(material['target']['dyns'][i][point][0]))
                        current_entry = dict()
                        current_entry['inst'] = material['target']['inst'][i]
                        current_entry['tech'] = material['target']['tech'][i]
                        current_entry['dynamic'] = dyny
                        current_entry['note'] = note
                        current_entry['target'] = True
                        current_entry['onoff'] = True
                        orchestration.append(current_entry)

            point_instrumentation = add_chord_element_list.add(orchestra, orchestration, 'score')
            orch_dropdown = [dbc.Badge("", id='add_badge{}'.format('score'), color="success",
                       style={'zIndex': 10000, 'position': 'absolute'}),
             # style={'top':-10, 'right':-5, 'zIndex':100000, 'verticalAlign': 'bottom','marginBottom':5}),
             dbc.DropdownMenu(id='orchestration_dropdown{}'.format('score'),
                              label='Click to check or modify your orchestration', children=point_instrumentation, className='orch_drpdwn'),
             ]

            return True, orch_dropdown

        if point:
            material = json.loads(material)
            # Convert notes to note names and set to lower case for React
            notes =[]
            annotations = []
            for i in range(len(material['orchestration']['notes'])):
                note = material['orchestration']['notes'][i][point]
                if list(note):
                    for n in note:
                        notes.append(n)
                        #print(material['orchestration']['dyns'][i][point])
                        dyny = assign_dyns.dyns(int(material['orchestration']['dyns'][i][point][0]))
                        annotations.append(material['orchestration']['inst'][i]+" "+dyny)
            tgts =[]
            for i in range(len(material['target']['notes'])):
                note = material['target']['notes'][i][point]
                if list(note):
                    for n in note:
                        tgts.append(len(notes))
                        notes.append(n)
                        #print('target')
                        #print(material['target']['dyns'][i][point])
                        dyny = assign_dyns.dyns(material['target']['dyns'][i][point][0])
                        annotations.append(material['target']['inst'][i]+" "+dyny)

            #Gotta sort the notes, annotations nd targets in ascending order for vexflow:
            notes, annotations, tgts, highs = sort_for_vexflow.sort_notes(notes, annotations, tgts)

            notes = [pretty_midi.note_number_to_name(int(i)) for i in notes]  # Change to note names
            notes = [i.lower() for i in notes]
            #print(notes)
            #print(annotations)
            # Use my shiny new Score module!
            orch = [sc.Orchestration(notes=notes, instruments=annotations, target=tgts, width=200)]

            show = dbc.Modal([
                dbc.ModalBody(html.Div(children=[html.H2('Orchestration at clicked point:'), html.Div(orch, style={'height': '50vh', 'backgroundColor': '#eed', 'textAlign':'center'})], className='fadein'))
            ], scrollable=True, is_open=True, size='s')
            return True, show
        return False, ''
    ########### RANGE SLIDER IS GIVING WRONG BARS EVERY OTCHER NUMBER!
    ###########

    ######################
    #### PROGRESS BAR ####
    ######################

    @app.callback(Output('wait_graph', 'children'),
                  [Input('analyze_button', 'n_clicks'),],
                  [State('wait_time', 'children')])
    def waiting_out(btn_clk, t):
        if btn_clk > 0:
            n = {'display': 'inline-block'}
            wait= html.Div([
                html.Br(),
                html.Div('Calculation time approximately: {}s'.format(t) ,style={'textAlign':'center'}),
                html.Div([
                html.Div(html.Div(className='progress-value'), className="progress", style={'--waitingtime':'{}s'.format(t), 'width':'600px',}),
                ], className='progressbody',style={ 'textAlign': 'center'})
            ], id='waiting_to_hide')
            return ''#wait
        return ''

    # @app.callback(Output('3d', 'children'),
    #               [Input('pianoroll_graph', 'onClick'), ],)
    # def pianoscore(onclick):
    #     print(onclick)
    #     return ''
    ########################
    ### LONG CALCULATION ###
    ########################

    # @app.callback(
    #     [Output('graafi_score', 'children'),
    #     Output('hidden_material', 'children'),
    #     Output('waiting_to_hide', 'children'),
    #      ],
    #     [Input('analyze_button', 'n_clicks'),],
    #     [State('hidden_score', 'children'),
    #      State({'type': 'instrument_sc', 'index': ALL}, 'value'),
    #     State({'type': 'tech_sc', 'index': ALL}, 'value'),
    #     State({'type': 'dyn_sc', 'index': ALL}, 'value'),
    #     State({'type': 'target_sc', 'index': ALL}, 'value'),
    #     State({'type': 'onoff_sc', 'index': ALL}, 'value'),
    #      State('score_range', 'value')
    #      ])
    # def button_output(value, hidden_score, instrument, tech, dyn, target, onoff, score_range):
    #     if value>0:
    #         score_range[0]-=1 #Adjust range to show right value
    #         hidden_score = json.loads(hidden_score)
    #         hidden_score = base64.b64decode(hidden_score)
    #         midi_data = pretty_midi.PrettyMIDI(io.BytesIO(hidden_score))
    #         #Get downbeats for range:
    #         downbeats= midi_data.get_downbeats()
    #         #get midi range timings from slider:
    #         s_range=[int(round(downbeats[score_range[0]]*pianoroll_resolution)), int(round(downbeats[score_range[1]-1]*pianoroll_resolution))]
    #         names = ['Orchestral score with target on top', 'Target masking percent in score', 'Homogenuity of the orchestration', 'Orchestration and target centroid comparison', 'Target sound color distance from orchestration', '3d graph of masking', 'Registral representation of the score']
    #         closed = [False, False, False, False, False, False, False] #Close pianoroll in the start?
    #
    #         #Get the graph data
    #         graph_data = do_graph(midi_data, instrument, tech, dyn, target, onoff, s_range, score_range)
    #
    #         #Construct graphs from data
    #         analyzer_graphs = score_graphs_from_graph_data.score_graphs_from_graph_data(graph_data)
    #
    #         boxes = []
    #         material = analyzer_graphs[-1] #This is a dict containing analyzed score and target notes and dyns
    #         for i in range(len(analyzer_graphs)-1):
    #             boxes.append(make_box(names[i], analyzer_graphs[i], closed[i]))
    #         return [boxes, json.dumps(material), '']
    #     return ['', '', '']

    #Update available techs according to instrument selection:
    @app.callback(
        Output({'type': 'tech_sc', 'index': ALL}, 'options'),
        [Input({'type': 'instrument_sc', 'index': ALL}, 'value'),]
    )
    def set_techs(instr):
        techs = []
        for i in instr:
            techs.append([{'label': val, 'value': val} for val in list(orchestra[i].keys())])
        return techs

    #Prepare instrumentation for download
    @app.callback(Output('javascript_download', 'run'),
                  [Input('save_analyze', 'n_clicks')],
                  [
                      State('pianoroll_graph', 'stave_list'),
                      State('3d_graph', 'figure'),
                      State({'type': 'a_graph', 'index': ALL}, 'figure'),
                      State('hidden_material', 'children'),
                      State('user_uuid', 'children')
                  ]
                  )
    def prepare_download(c, pianoroll, graph3d, all_graphs, analyzed_material, user_uuid):
        if c>0:
            all_data = {'pianoroll': pianoroll, '3d': graph3d, 'all': all_graphs, 'material': json.loads(cache.get(user_uuid + 'material'))}
            all_data = json.dumps(all_data)
            script = '''
            function loadScript(url, callback)
            {
               var head = document.getElementsByTagName('head')[0];
               var script = document.createElement('script');
               script.type = 'text/javascript';
               script.src = url;
            
               script.onreadystatechange = callback;
               script.onload = callback;
            
               head.appendChild(script);
            }
            
            var downloader = function() {
            var blob = new Blob([' '''+all_data+''' '], {type: "text/plain;charset=utf-8"});
            saveAs(blob, "orchestration.score");
            };
            
            loadScript("./bin/assets/FileSaver.js", downloader);
                '''
            return script
        raise PreventUpdate
        return ''

    #Prepare instrumentation for download
    # @app.callback(Output('score_download', 'href'),
    #               [Input('save_analyze', 'n_clicks')],
    #               [
    #                   State('pianoroll_graph', 'stave_list'),
    #                   State('3d_graph', 'figure'),
    #                   State({'type': 'a_graph', 'index': ALL}, 'figure'),
    #                   State('hidden_material', 'children'),
    #               ]
    #               )
    # def prepare_download(c, pianoroll, graph3d, all_graphs, analyzed_material):
    #     if c > 0:
    #         #media_type = 'text/txt'
    #
    #         all_data = {'pianoroll':pianoroll, '3d':graph3d, 'all':all_graphs, 'material': analyzed_material}
    #         all_data = json.dumps(all_data)
    #         all_data = all_data.replace("#", "SHP")
    #         return '/downloadScore?value={}'.format(all_data) #all_data.replace("#", "SHP")
    #         #href_data_downloadable = f'data:{media_type};charset=utf-8,{pianoroll}'
    #         #return href_data_downloadable
    #     return ''
    #
    # @app.server.route('/downloadScore')
    # def download_score_file():
    #     value = flask.request.args.get('value')
    #     value = value.replace("SHP", "#")
    #     str_io = io.StringIO()
    #     str_io.write(value)
    #     mem = io.BytesIO()
    #     mem.write(str_io.getvalue().encode('utf-8'))
    #     mem.seek(0)
    #     str_io.close()
    #     return flask.send_file(mem,
    #                            mimetype='text/plain',
    #                            attachment_filename='orchestration.score',
    #                            as_attachment=True,
    #                            cache_timeout=0
    #                         )

    #Auto-click download link with javascript after creation
    @app.callback(
        Output('javascript_score', 'run'),
        [Input('score_download', 'href'),
         Input('pianoroll_png', 'n_clicks')])
    def auto_click_download(x, png):
        ctx = dash.callback_context  # Callback context to recognize which input has been triggered
        if not ctx.triggered:
            raise PreventUpdate
        else:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        #print(input_id)
        if input_id=='score_download':
            if x:
                return "var a = document.getElementById('score_download'); a.click();"

        if input_id=='pianoroll_png':
            return '''
            function loadScript(url, callback)
            {
                // adding the script tag to the head as suggested before
               var head = document.getElementsByTagName('head')[0];
               var script = document.createElement('script');
               script.type = 'text/javascript';
               script.src = url;
            
               // then bind the event to the callback function 
               // there are several events for cross browser compatibility
               script.onreadystatechange = callback;
               script.onload = callback;
            
               // fire the loading
               head.appendChild(script);
            }
            
            var myPrettyCode = function() {
            var svg = document.getElementById('pianoroll_graph').getElementsByTagName("svg")[0];
            Pablo(svg).load(svg).download('png', 'score.png')
            };
            
            loadScript("./bin/assets/pablo.min.js", myPrettyCode);
            '''

        return ""

    @app.callback(
        [
        Output('hidden_material', 'children'),
        #Output('waiting_to_hide', 'children'),
        Output('pianoroll_container', 'children'),
        Output('3d_graph', 'figure'),
        Output({'type': 'a_graph', 'index': ALL}, 'figure'),
        Output('midi_graph', 'figure'),
        Output('int_container', 'children'),
        Output('calc_time', 'value'),
        Output('calc_time', 'children'),
        Output('counter', 'children'),
         ],
        [Input('int', 'n_intervals'),Input('confirm', 'submit_n_clicks'), Input('upload-score', 'contents')],
        [State('hidden_score', 'children'),
         State({'type': 'instrument_sc', 'index': ALL}, 'value'),
        State({'type': 'tech_sc', 'index': ALL}, 'value'),
        State({'type': 'dyn_sc', 'index': ALL}, 'value'),
        State({'type': 'target_sc', 'index': ALL}, 'value'),
        State({'type': 'onoff_sc', 'index': ALL}, 'value'),
         State('score_range', 'value'),
         State('pianoroll_graph', 'stave_list'),
         State('pianoroll_graph', 'bar_offset'),
         State('3d_graph', 'figure'),
         State({'type': 'a_graph', 'index': ALL}, 'figure'),
         State('midi_graph', 'figure'),
         State('score_range', 'value'),
         State('hidden_material', 'children'),
         State('counter', 'children'),
         State('user_uuid', 'children')
         ])
    def button_output(value, reset, upload_score,hidden_score, instrument, tech, dyn, target, onoff, score_range, stave_list, bar_offset, figure_3d, figures_all, figure_midi, max_int, analyzed_material, counter, user_uuid):

        #Get the right end of the slider
        value = counter + max_int[0]
        max_int = max_int[1]

        # If reset is clicked, reset all data:
        ctx = dash.callback_context  # Callback context to recognize which input has been triggered
        if not ctx.triggered:
            raise PreventUpdate
        else:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        #print('value: {}, counter: {}'.format(value, counter))

        #Set the bar under calculation, counter+start bar


        if reset and input_id=='confirm':
            graph_data = empty_graphs()
            interval = dcc.Interval(id='int', interval=8000, max_intervals=0, n_intervals=0)
            calc_percent = 0
            calc_text = ''
            figure_3d['data'][0]['z'] = []
            figure_3d['data'][1]['z'] = []
            figure_3d['layout']['scene']['yaxis']['tickvals'] = []
            figure_3d['layout']['scene']['yaxis']['ticktext'] = []
            figure_midi['data'] = []
            for fig in figures_all:
                fig['data'][0]['x'] = []
                fig['layout']['xaxis']['tickvals'] = []
                fig['layout']['xaxis']['ticktext'] = []
                fig['data'][0]['y'] = []
            analyzed_material=None

            score_pianoroll = sc.Pianoroll(id='pianoroll_graph', stave_list=graph_data['stave_list'],
                                           bar_offset=0,
                                           width=200,
                                           height=200,
                                           stave_spacing=70)
            score_pianoroll = html.Div(children=score_pianoroll, style={'backgroundColor': '#eed', 'height': 200})
            score_pianoroll = html.Div(id='pianoroll_container', children=[
                html.Div('Score with the target at the top. The redness of the target means less audibility',
                         style={'backgroundColor': '#eed', 'color': 'black', 'fontSize': 30, 'textAlign': 'center'}),
                score_pianoroll], style={'backgroundColor': '#eed', 'width': '100%', 'overflowX': 'auto'})
            counter=0
            return [None, score_pianoroll, figure_3d, figures_all, figure_midi, interval, calc_percent, calc_text, counter]

        #If material dict is empty, let's create one, else load old one
        if not cache.get(user_uuid+'material'):
            analyzed_material=dict(target=dict(dict(notes=[], dyns=[], inst=[], tech=[])), orchestration=dict(dict(notes=[], dyns=[], inst=[], tech=[])))
        else:
            analyzed_material=json.loads(cache.get(user_uuid+'material'))

        if input_id=='upload-score':
            #Decode uploaded file:
            content_type, content_string = upload_score.split(',')
            decoded = base64.b64decode(content_string)
            decoded = decoded.decode('utf-8')
            all_data = json.loads(decoded)

            stave_list = all_data['pianoroll']

            figure_3d = all_data['3d']
            figures_all = all_data['all']
            analyzed_material = all_data['material']
            if not isinstance(cache.set(user_uuid + 'material'), str):
                analyzed_material = json.dumps(analyzed_material)

            figure_midi = ''
            interval = dcc.Interval(id='int', interval=8000, max_intervals=0, n_intervals=0)
            scale=2
            score_length = len(set(figure_3d['layout']['scene']['yaxis']['ticktext']))
            score_height = len(stave_list[0])
            bar_offset = figure_3d['layout']['scene']['yaxis']['ticktext'][0]
            score_pianoroll = sc.Pianoroll(id='pianoroll_graph', stave_list=stave_list,
                                           bar_offset=bar_offset,
                                           width=  score_length * 200 * scale,
                                           height= (score_height * 70) / scale + 100,
                                           scale=1 / scale,
                                           stave_spacing=70)
            score_pianoroll = html.Div(children=score_pianoroll,
                                       style={'backgroundColor': '#eed',
                                              'width': ((score_length * 200) + 100) / scale,
                                              'height': (score_height * 70) / scale + 100})

            cache.set(user_uuid+'material', analyzed_material)

            return ['analyzed_material', score_pianoroll, figure_3d, figures_all, figure_midi, interval, 0, '', 0]


        if input_id=='int' and value>0 and value<max_int and max_int!=0:
            start_bar = score_range[0]-1
            score_range[0]-=1 #Adjust range to show right value
            score_range=[value-1, value+1]
            # hidden_score = json.loads(hidden_score)
            hidden_score = cache.get(user_uuid+'score')
            hidden_score = base64.b64decode(hidden_score)
            midi_data = pretty_midi.PrettyMIDI(io.BytesIO(hidden_score))
            #Get downbeats for range:
            downbeats= midi_data.get_downbeats()
            #get midi range timings from slider:
            s_range=[int(round(downbeats[score_range[0]]*pianoroll_resolution)), int(round(downbeats[score_range[1]-1]*pianoroll_resolution))]

            #names = ['Orchestral score with target on top', 'Target masking percent in score', 'Homogenuity of the orchestration', 'Orchestration and target centroid comparison', 'Target sound color distance from orchestration', '3d graph of masking', 'Registral representation of the score']
            #closed = [False, False, False, False, False, False, False] #Close pianoroll in the start?

            #Get the graph data
            graph_data = do_graph(midi_data, instrument, tech, dyn, target, onoff, s_range, score_range)
            graph_data['bar_offset'][0] = start_bar
            #stave_list.append(graph_data['stave_list'])
            figure_3d['data'][0]['z']= figure_3d['data'][0]['z']+graph_data['orchestration_masking_curves']
            figure_3d['data'][1]['z']= figure_3d['data'][1]['z']+graph_data['target_peaks_over_masking']

            # Adjust ticks for measures
            if figures_all[0]['layout']['xaxis']['tickvals']:
                last_tick = figures_all[0]['layout']['xaxis']['tickvals'][-1]
                graph_data['ticks_for_bar_start'] = [i + last_tick for i in graph_data['ticks_for_bar_start']]
                # Pop the last tick as it's the 0
                graph_data['ticks_for_bar_start'].pop(0)
                graph_data['ticks_for_bar_start'] = figures_all[0]['layout']['xaxis']['tickvals'] + graph_data['ticks_for_bar_start']

            tickvals_enhanced = []
            k = start_bar
            for i in range(graph_data['ticks_for_bar_start'][-1]):
                tickvals_enhanced.append(k)
                if i + 1 in graph_data['ticks_for_bar_start']:
                    k += 1

            figure_3d['layout']['scene']['yaxis']['tickvals'] = np.arange(len(figure_3d['layout']['scene']['yaxis']['tickvals'])+graph_data['score_length'])  # ticks_for_bar_start
            figure_3d['layout']['scene']['yaxis']['ticktext'] = tickvals_enhanced


            for fig in figures_all:
                fig['data'][0]['x'] = np.arange(len(fig['data'][0]['x'])+graph_data['score_length'])
                fig['layout']['xaxis']['tickvals'] = graph_data['ticks_for_bar_start']
                fig['layout']['xaxis']['ticktext'] = np.arange(len(graph_data['downbeats'][graph_data['bar_offset'][0]:graph_data['bar_offset'][1]])) + \
                                              graph_data['bar_offset'][0] + 1  # Do the math to get the right text



            figures_all[0]['data'][0]['y']= figures_all[0]['data'][0]['y']+graph_data['target_masking_percent_array']

            orchestration_var_coeffs = np.array(graph_data['orchestration_var_coeffs'])
            orchestration_var_coeffs[orchestration_var_coeffs > 5] = 5  # Delete anomalies in var_coeff
            figures_all[1]['data'][0]['y']= np.concatenate([figures_all[1]['data'][0]['y'], orchestration_var_coeffs])

            figures_all[2]['data'][0]['y']=figures_all[2]['data'][0]['y']+graph_data['orchestration_centroids']
            figures_all[2]['data'][1]['x'] = np.arange(len(fig['data'][0]['x']) + graph_data['score_length'])
            figures_all[2]['data'][1]['y']=figures_all[2]['data'][1]['y']+graph_data['target_centroids']

            figures_all[3]['data'][0]['y']=figures_all[3]['data'][0]['y']+graph_data['mfcc_distance_vector']

            figure_midi['data']=graph_data['all_traces']

            analyzed_material['orchestration']['inst'] += graph_data['analyzed_material']['orchestration']['inst']
            analyzed_material['orchestration']['tech'] += graph_data['analyzed_material']['orchestration']['tech']
            analyzed_material['target']['inst'] += graph_data['analyzed_material']['target']['inst']
            analyzed_material['target']['tech'] += graph_data['analyzed_material']['target']['tech']

            #If note data exists, append next bar using zip:
            if analyzed_material["orchestration"]["notes"]:
                analyzed_material["orchestration"]["notes"] = [a + b for a, b in zip(analyzed_material["orchestration"]["notes"], graph_data['analyzed_material']['orchestration']['notes'])]
                analyzed_material['orchestration']['dyns'] = [a + b for a, b in zip(analyzed_material["orchestration"]["dyns"], graph_data['analyzed_material']['orchestration']['dyns'])]
                analyzed_material['target']['notes'] = [a + b for a, b in zip(analyzed_material["target"]["notes"], graph_data['analyzed_material']['target']['notes'])]
                analyzed_material['target']['dyns'] = [a + b for a, b in zip(analyzed_material["target"]["dyns"], graph_data['analyzed_material']['target']['dyns'])]
            else:
                analyzed_material["orchestration"]["notes"] += graph_data['analyzed_material']['orchestration']['notes']
                analyzed_material['orchestration']['dyns'] += graph_data['analyzed_material']['orchestration']['dyns']
                analyzed_material['target']['notes'] += graph_data['analyzed_material']['target']['notes']
                analyzed_material['target']['dyns'] += graph_data['analyzed_material']['target']['dyns']

            if stave_list[0][0]['notes']:
                stave_list.append(graph_data['stave_list'][0])
            else:
                stave_list = graph_data['stave_list']

            score_length=len(fig['layout']['xaxis']['tickvals'])
            scale = 2  # calculated 1/scale values, i.e. 2 = 1/2 = 0.5
            score_pianoroll = sc.Pianoroll(id='pianoroll_graph', stave_list=stave_list,
                                           bar_offset=graph_data['bar_offset'][0],
                                           width=score_length * 200 * scale,
                                           height=(len(graph_data['instrument']) * 70 / scale) + 100,
                                           scale=1 / scale,
                                           stave_spacing=70)
            score_pianoroll = html.Div(children=score_pianoroll,
                                       style={'backgroundColor': '#eed',
                                              'width': ((score_length * 200) + 100) / scale,
                                              'height': (len(graph_data['instrument']) * 70 / scale) + 100})

            #Send an interval to allow graphs to update before next calculation
            interval = dcc.Interval(id='int', interval=2000, max_intervals=2, n_intervals=1)

            v= value-graph_data['bar_offset'][0]+1
            m = max_int-graph_data['bar_offset'][0]
            calc_percent = int((v/(m-1))*100)
            calc_text = 'calculating bar {} of {}'.format(v, m-1)
            if v>m-1:
                calc_percent=0
                calc_text=''

            counter += 1

            cache.set(user_uuid + 'material', json.dumps(analyzed_material))

            return [json.dumps('analyzed_material'), score_pianoroll, figure_3d, figures_all, figure_midi, interval, calc_percent, calc_text, counter]
        else:
            raise PreventUpdate
        cache.set(user_uuid + 'material', json.dumps(analyzed_material))
        return [json.dumps('analyzed_material'), '', figure_3d, figures_all, figure_midi, 8000, 0, '0%', counter]

    ###############################################
    ###### LOAD DATA FROM UPLOAD OR DROPDOWN ######
    ###############################################

    def midi_load(midifile, name):
        encoded_midi = base64.b64encode(midifile)  # Encode midifile with base64
        dump = json.dumps(encoded_midi.decode('utf-8'))  # Decode into string for json dumps
        decoded = base64.b64decode(dump)  # convert back with base64 decode
        this_midifile = pretty_midi.PrettyMIDI(io.BytesIO(decoded))
        load_return = define_score_instruments(this_midifile, name)

        # midi_data=pretty_midi.PrettyMIDI(io.BytesIO(decoded)) #Load to midi as io.bytes object
        return dump, load_return

    @app.callback(
        [Output('hidden_score', 'children'),
         Output('load_return', 'children'),
         Output('load_return', 'style'),
         ],
        [Input('score_select', 'value'),
         Input('upload-data', 'contents')],
        [State('upload-data', 'filename'),
        State('upload-data', 'last_modified'),
         State('user_uuid', 'children')])
    def select_output(value, list_of_contents, list_of_names, list_of_dates, user_uuid):
        dump=''
        load_return=empty_content
        style = {'margin':10}
        if value == 'Test_score':
            with open('./examples/test_score.mid', mode='rb') as file:  # b is important -> binary
                midifile = file.read()
            dump, load_return = midi_load(midifile, 'test_score')
            style = {'margin': 10}
        if value == 'Brahms':
            with open('./examples/brahms_violin_concert.mid', mode='rb') as file:  # b is important -> binary
                midifile = file.read()
            dump, load_return = midi_load(midifile, 'brahms')
            style = {'margin': 10}
        if list_of_contents is not None:
            #tiedot = [
            #    parse_contents(c, n, d) for c, n, d in
            #    zip(list_of_contents, list_of_names, list_of_dates)]
            tiedot = parse_contents(list_of_contents)
            midifile = tiedot[0]
            dump = tiedot[1]
            load_return = define_score_instruments(midifile, 'Own upload')
            style = {'margin': 10}
        cache.set(user_uuid+'score', dump)

        return ['', load_return, style]


    def parse_contents(contents):#, filename, date):
        if contents is not None:

            content_type, content_string = contents.split(',')

            if content_type.find('data:text')>=0:
                try:
                    #First decode base64 encoded file:
                    decoded = base64.b64decode(content_string)
                    #Return is binary, so convert to text:
                    decoded_string = decoded.decode('utf-8')
                    #Get the music21 object and convert to midi
                    m21_conv = music21.converter.parseData(decoded_string)
                    mf = music21.midi.translate.streamToMidiFile(m21_conv)
                    mf = mf.writestr()
                    #For my own program, encode midi file to base64 and text for json
                    encoded = base64.b64encode(mf)
                    dump = json.dumps(encoded.decode('utf-8'))
                    #To ensure the file is usable, decode back and read as midi
                    decoded = base64.b64decode(encoded)
                    pm = pretty_midi.PrettyMIDI(io.BytesIO(decoded))
                    return [pm, dump]
                except Exception as e:
                    print(e)
            elif content_type.find('data:audio/mid')>=0:
                try:
                    dump = json.dumps(content_string)
                    decoded = base64.b64decode(content_string)
                    #print(decoded)
                    pm = pretty_midi.PrettyMIDI(io.BytesIO(decoded))
                    return [pm, dump]
                    # return {'data': [{'z': pm.get_piano_roll(), 'type': 'heatmap', 'colorscale': [[0, 'black'], [1, 'white']]}],
                    #         'layout': fig_layout
                    #         }
                except Exception as e:
                    print(e)
            else:
                print('Not a valid file')

    ##########################################
    ### Callback to do one bar at the time ###
    ##########################################
    @app.callback(Output('confirm', 'displayed'), [Input('reset_analyze', 'n_clicks')])
    def warning(reset):
        if reset>0:
            return True
        return False

    @app.callback([Output('calc_container', 'children'), Output('outer_container', 'children')],
                  [Input('analyze_button', 'n_clicks'), Input('pause_analyze', 'n_clicks'), Input('continue_analyze', 'n_clicks')],
                  [
                   State('score_range', 'value'),
                   State('outer_container', 'children'),
                  State('counter', 'children')])
    def trig(btn, btn2, btn3, slider_value, outer_cont, n_int):
        if btn>0:
            ctx = dash.callback_context  # Callback context to recognize which input has been triggered
            if not ctx.triggered:
                raise PreventUpdate
            else:
                input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            #print(input_id)
            if input_id == 'analyze_button':
                percent = 100 / (slider_value[1] - slider_value[0])
                prog_bar = [html.Br(),
                            dbc.Progress('calculating bar 1 of {}'.format(slider_value[1] - slider_value[0]),
                                         value=percent, id='calc_time', color='warning', striped=True, animated=True,
                                         style={'height': 30})]
                container = html.Div(dcc.Interval(id='int', interval=20000, max_intervals=2, n_intervals=1),
                                     id='int_container')
                return [prog_bar, container]
            if input_id == 'pause_analyze':
                percent = n_int*100 / (slider_value[1] - slider_value[0] - 1)
                prog_bar = [html.Br(),
                            dbc.Progress('PAUSED',
                                         value=percent, id='calc_time', color='warning', striped=True, animated=True,
                                         style={'height': 30})]
                return [prog_bar, '']
            if input_id == 'continue_analyze':
                percent = n_int * 100 / (slider_value[1] - slider_value[0] - 1)
                prog_bar = [html.Br(),
                            dbc.Progress('Continuing...'.format(n_int - slider_value[0] - 1),
                                         value=percent, id='calc_time', color='warning', striped=True, animated=True,
                                         style={'height': 30})]
                container = html.Div(dcc.Interval(id='int', interval=20000, max_intervals=2, n_intervals=1), id='int_container')
                return [prog_bar, container]
        else:
            raise PreventUpdate
        return ['', '']

    insert_new, orchestration_chord = chord_testing.chord_testing(app, orchestra, 'score', 'score')
    # print(orchestration_chord)
    show = dbc.Modal([
        dbc.ModalBody(
            html.Div(children=[html.H2('Orchestration at clicked point:'), html.Div([insert_new, orchestration_chord])],
                     className='fadein'))
    ], scrollable=True, is_open=False, size='xl', id='scoremodal')

    Score_testing_layout=html.Div([
                           html.Div(id='score', children=[analyzer_layout],),
                            html.Div(id='analyze_boxes', children=do_analyze_boxes()),
                            html.Div(id='graafi_score', className='waiting'),
                           html.Div(id='testing_score'),
                            html.Div(show, id='check_orchestration'),
                           html.Div(id='hidden-container_score', style={'display': 'none'}),
                           html.Div(id='hidden2_score', style={'display': 'none'}),
                           html.Div(id='hidden3_score', style={'display': 'none'}),
                           html.Div(id='wait_time', style={'display': 'none'}),
                           html.Div(id='hidden_material', style={'display': 'none'}),
                            html.Div(id='hidden_score', style={'display': 'none'}),
                            html.Div(0, id='counter', style={'display': 'none'}),
                            html.Div(html.Div(dcc.Interval(id='int', interval=20000, max_intervals=0, n_intervals=1), id='int_container'), id='outer_container'),
                            dcc.ConfirmDialog(id='confirm', message='Warning! This will erase your current analysis data, are you sure you want to continue?', ),
                           ])
    return Score_testing_layout


