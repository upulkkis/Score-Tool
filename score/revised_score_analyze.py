HEROKU = False

if HEROKU:
    import os
    from random import randint
    import flask

dropd_color = 'black'
dropd_back = 'gray'

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
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


def help(topic):
    return html.Div(html.Details([html.Summary('?', className= 'button'), html.Div(get_help.help(topic))]))
#Encoder that conferts numpy arrays to list for json dumps
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


with open('no_data_orchestra.pickle', 'rb') as handle:
    orchestra = pickle.load(handle)


if HEROKU:
    server = flask.Flask(__name__)
    server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))

    app = dash.Dash(__name__, server=server)
    app = dash.Dash(__name__, server=server)
else:
    app = dash.Dash(__name__)

#I think either one works, here are both :)
app.config['suppress_callback_exceptions'] = True
app.config.suppress_callback_exceptions = True

##################
# Find all indexes of item in a list:
def list_idx_of_item(list, item): return [ i for i in range(len(list)) if list[i] == item ]


############################################################
############################################################
################# ANALYZE SCORE CONTENT HERE  ##############
############################################################
############################################################

image_filename3 = 'test_score.png' # Orchestration Analyzer logo
encoded_image3 = base64.b64encode(open(image_filename3, 'rb').read())

pianoroll_resolution=10 #In milliseconds
inst_list=list(orchestra.keys())
tech_list=['normal']
dyn_list=['p', 'mf', 'f']
note_numbers=np.arange(128)
notenames=[]
roll = pretty_midi.PrettyMIDI('test_score.mid')

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
            'displayModeBar': False
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
              html.Th('target/orch.'),
              html.Th('on/off')
                      ])]
    def set_id(set_type, index):
        return {
            'type': set_type,
            'index': index
        }

    for i in range(length):
        if midi_data.instruments[i].program != 0:
            instrument = midi_data.instruments[i]
            valid_instruments.append(i)
            if instrument.program == 41-1:
                inst_name='violin'
            elif instrument.program == 43-1:
                inst_name='cello'
            elif instrument.program == 74-1:
                inst_name='flute'
            elif instrument.program == 57-1:
                inst_name='trumpet'
            else:
                inst_name='violin'
            score_name = instrument.name
            #inst_lista.append(inst_name)
            tch = 'normal'
            #tech_lista.append(tch)
            onoff = 1
            #onoff_lista.append(onoff)
            target = 0
            #target_lista.append(target)

            graphs.append(html.Tr(children=[
                html.Th(html.Div(id=set_id('scorename',i), children=score_name,
                         style={'display': 'inline-block', 'padding': '8px', 'fontSize': '25px', 'color': 'grey', 'textAlign':'left'}),
                        ),
                html.Th(dcc.Dropdown(
                    options=[{'label': val, 'value': val} for val in inst_list],
                    # className='select',
                    value=inst_name,
                    multi=False,
                    id=set_id('instrument', i),
                    style={'backgroundColor': dropd_back, 'color': dropd_color, 'display': 'inline-block', 'opacity': 1,
                           'border': 'none', 'width': '150px', 'fontSize': '25px', 'bottom': '-10px'},
                )),
                html.Th(dcc.Dropdown(
                    options=[{'label': val, 'value': val} for val in tech_list],
                    className='select',
                    value=tch,
                    multi=False,
                    id=set_id('tech',i),
                    style={'backgroundColor': dropd_back, 'color': dropd_color, 'display': 'inline-block', 'opacity': 1,
                           'border': 'none', 'width': '150px', 'fontSize': '25px', 'bottom': '-10px'},
                )),
                #For target, value is 100+something, for orchestration 0+something :)
                html.Th(dcc.Dropdown(
                    options=[{'label': 'target', 'value': 100+i}, {'label': 'orchestration', 'value': 0+i}],
                    className='select',
                    value=0+i,
                    multi=False,
                    id=set_id('target',i),
                    style={'backgroundColor': dropd_back, 'color': dropd_color, 'display': 'inline-block', 'opacity': 1,
                           'border': 'none', 'width': '200px', 'fontSize': '25px', 'bottom': '-10px'},
                )),
                html.Th(dcc.Dropdown(
                    options=[{'label': 'on', 'value': 1}, {'label': 'off', 'value': 0}],
                    className='select',
                    value=onoff,
                    multi=False,
                    id=set_id('onoff',i),
                    style={'backgroundColor': dropd_back, 'color': dropd_color, 'display': 'inline-block', 'opacity': 1,
                           'border': 'none', 'width': '100px', 'fontSize': '25px', 'bottom': '-10px'},
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


from chord import maskingCurve_peakInput
from helpers import constants, get_fft, findPeaks


def get_masking(data, peaks):
        #app.logger.info(peaks)
        #app.logger.info(data)
        #S = get_fft.get_fft(data)
        if len(peaks) == 0:
            masking_threshold=np.zeros(106)#-30
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



def do_graph(midi_data, instrument, tech, tgt, onoff, score_range, bar_offset):
    all_traces = []
    target_pianoroll = []
    orchestration_pianoroll = []
    all_data = midi_data.get_piano_roll(pianoroll_resolution) # Do not set range yet! [:, score_range[0]:score_range[1]]   #Do an overall pianoroll score
    score_length = len(all_data[0,:])
    all_data = all_data[:, score_range[0]:score_range[1]]
    alltrace = add_trace(all_data, 'orchestration')
    all_traces.append(alltrace.copy())
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
            target_pianoroll.append(t_PR[:, score_range[0]:score_range[1]]) #Append to the list of targets, took away copy()
            all_traces.append(add_trace(target_pianoroll[-1], midi_data.instruments[tgt[ind]-100].name, 'red').copy()) #Add target to traces
        if onoff[ind]==1 and tgt[ind]<100:
            o_PR = midi_data.instruments[tgt[ind]].get_piano_roll(pianoroll_resolution)
            o_PR_len = len(o_PR[0, :]) #Append zeros to make all piano roll equal length
            o_PR = np.hstack([o_PR, np.zeros([128, score_length - o_PR_len])])
            orchestration_pianoroll.append([o_PR[:, score_range[0]:score_range[1]], midi_data.instruments[tgt[ind]].name].copy())
    #print(all_traces)
        #Get values where bar changes
    tickvals=midi_data.get_downbeats()[bar_offset[0]:bar_offset[1]]
        #Get offset for first value
    offset=tickvals[0]*pianoroll_resolution
    fig_layout['xaxis']['tickmode']='array'
    fig_layout['xaxis']['tickvals']=[round(i*pianoroll_resolution-offset) for i in tickvals] #Do the math to get the right place
    fig_layout['xaxis']['ticktext']=np.arange(len(midi_data.get_downbeats()[bar_offset[0]:bar_offset[1]]))+bar_offset[0]+1 #Do the math to get the right text

    #masking3d=do3dgraph(midi_data, tgt, orchestration_pianoroll)
    masking3d=''
    graph = dcc.Graph(id='midi_graph', figure={'data': all_traces,
                                          'layout': fig_layout
                                          }, config=fig_config)
    graph3d = masking3d
    return html.Div([graph3d, graph])

#graafi=do_graph(roll, 1)
###POISTA SIT TÄSTÄ
# roll = pretty_midi.PrettyMIDI('symphonic_songs.mid')
#piano=go.Heatmap(z=roll.get_piano_roll())
# alles=roll.get_piano_roll()
# alles[np.where(alles == 0)]=None
# trace1 = {
#             "type": "heatmap",
#             'z':alles,
#     "zmin": 0,
#     "zmax": 1,
#             "name": "all",
#             'colorscale': [[0, 'black'], [1, 'white']],
#             'showlegend': True,
#             'legendOrientation': 'h',
#             'showscale': False,
#             #'visible': True
#         }
# puts=roll.instruments[0].get_piano_roll()
# puts[np.where(puts == 0)]=None
# trace2 = {
#             "type": "heatmap",
#             'z': puts,
#             "name": "1st stave",
#             'colorscale': [[0, 'black'], [1, 'red']],
#     "zmin": 0,
#     "zmax": 1,
#             'showlegend': True,
#             'showscale': False,
#             'visible': True,
#         }
#
# traces=[trace1, trace2]
#graafi = dcc.Graph(id='jopo', figure = figur,config = fig_config)
# graafi = dcc.Graph(id='jopo', figure = {'data':traces,
#           'layout': fig_layout
#           },config = fig_config)
###POISTA SIT TÄHÄ

examples = ['Test_score', 'Brahms', 'Chamber music', 'Own works', 'Push here to load an example score']
slider_range=[]
analyzer_layout = html.Div(children=[
    #html.Div(id="hidden", style={'visible': False}),
    #html.Div(id="temp", style={'visible': False}),
    #html.Div(id="temp2", style={'visible': False}),
    #html.Button(id='analyze_button', n_clicks=0, children='Push here for analysis', className='button',),
    html.Div('NOTE: Score upload is disabled to save server calculation time. '
             'However, you can test pre-loaded by pressing ´Push here to analyze´. '
             'The score of pre-loaded material can be seen by pressing ´Show score´. '
             'Analysis takes time, and appears at the bottom of the page.', style={'color':'red', 'textSize': 24}),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select File'),
        ],
            style={
                'textAlign': 'center',
                'color': 'grey'
            }
        ),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'color': 'grey'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),

    dcc.Dropdown(
        options=[{'label': val, 'value': val} for val in examples],
        className='select',
        value=examples[-1],
        multi=False,
        id='score_select',
        style={'backgroundColor': dropd_back, 'color': dropd_color, 'display': 'inline-block', 'opacity': 1,
               'border': 'none', 'width': '100%', 'fontSize': '25px', 'bottom': '-10px'},
    ),

    ###Tämä pitäisi tulla callbackinä, ei toimi!

    ### Tähän asti siirrettävä callbackiin!!


    html.Div(id='load_return'),
    #html.Div(add_instruments(roll)),

    html.Div(id='graafi', className='waiting'),
    html.Div(id='3d', style={'width': '100%'}),
    #graafi,# dcc.Graph(
    #     id='piano_scroll',
    #     figure=fig,
    #     config = fig_config
    # ),
    # dcc.Graph(
    #     id='testaus',
    # ),
    html.Div(id='valikot'),
    html.Div(id='testi',
             style={
                 'color': 'grey'})
            # children=dcc.Graph(figure = {'data':[{'z':pm.get_piano_roll(), 'type':'heatmap', 'colorscale': [[0, 'white'], [1, 'blue']]}],
            #                     'layout': fig_layout
            #                     },
            #                    config=fig_config)
            #  )
],
)

def define_score_instruments(midifile):
    return html.Div([
    add_instruments(midifile),
    html.Div('bars', style={'textAlign': 'center', 'color': 'grey'}),
    dcc.RangeSlider(
        id='score_range',
        min=1,
        max=len(roll.get_downbeats()),
        step=1,
        value=[1, len(roll.get_downbeats())],
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
    html.Div(id='slider_return', style={'textAlign': 'center', 'color': 'grey'}),

    html.Button(id='analyze_button', n_clicks=0, children='Push here for analysis', className='button',),

    html.Details([html.Summary('Show score', className='button'), html.Div(
        html.Div(html.Div(children=[html.Img(src='data:image/png;base64,{}'.format(encoded_image3.decode()), style={'width': '100%'})], style={'textAlign': 'center'})),
    )]),])

@app.callback(
    Output('slider_return', 'children'),
    [Input('score_range', 'value')])
def range_output(value):
    text="Analysis range set from bar {} to {}".format(value[0], value[1]-1)
    return text

########### RANGE SLIDER IS GIVING WRONG BARS EVERY OTCHER NUMBER!
###########

@app.callback(
    Output('graafi', 'children'),
    [Input('analyze_button', 'n_clicks'),],
    [State('hidden_score', 'children'),
     State({'type': 'instrument', 'index': ALL}, 'value'),
    State({'type': 'tech', 'index': ALL}, 'value'),
    State({'type': 'target', 'index': ALL}, 'value'),
    State({'type': 'onoff', 'index': ALL}, 'value'),
     State('score_range', 'value')
     ])
def button_output(value, hidden_score, instrument, tech, target, onoff, score_range):
    if value>0:
        score_range[0]-=1 #Adjust range to show right value
        hidden_score = json.loads(hidden_score)
        hidden_score = base64.b64decode(hidden_score)
        midi_data = pretty_midi.PrettyMIDI(io.BytesIO(hidden_score))
        #Get downbeats for range:
        downbeats= midi_data.get_downbeats()
        #get midi range timings from slider:
        s_range=[int(round(downbeats[score_range[0]]*pianoroll_resolution)), int(round(downbeats[score_range[1]-1]*pianoroll_resolution))]
        return do_graph(midi_data, instrument, tech, target, onoff, s_range, score_range)
    return ''

@app.callback(
    [Output('hidden_score', 'children'),
     Output('load_return', 'children')],
    [Input('score_select', 'value')])
def select_output(value):
    if value == 'Test_score':
        with open('test_score.mid', mode='rb') as file:  # b is important -> binary
            midifile = file.read()
        this_midifile = pretty_midi.PrettyMIDI('test_score.mid')
        encoded_midi = base64.b64encode(midifile)  #Encode midifile with base64
        dump = json.dumps(encoded_midi.decode('utf-8')) #Decode into string for json dumps

        load_return = define_score_instruments(this_midifile)
        decoded = base64.b64decode(dump)    #convert back with base64 decode
        midi_data=pretty_midi.PrettyMIDI(io.BytesIO(decoded)) #Load to midi as io.bytes object
        #pretty_midi.PrettyMIDI(decoded)
        return [dump, load_return]
    return ['','']

'''
@app.callback(
    Output('load_return', 'children'), #temp -> load_return
    [Input('score_select', 'value')]) #vaihda: testi -> score_select child->value
def select_output(value):
    if value == 'Test_score':
        roll = pretty_midi.PrettyMIDI('test_score.mid')
        content = html.Div([add_instruments(roll), html.Div('bars', style={'textAlign': 'center', 'color': 'grey'}),
    dcc.RangeSlider(
        id='score_range',
        min=0,
        max=len(roll.get_downbeats()),
        step=1,
        value=[0, len(roll.get_downbeats())],
        pushable=1,
        dots=True,
        tooltip={
            'always_visible': True,
            'placement': 'bottom'
        },
        # marks={
        #     0:'0',
        #     5:'5',
        #     10:'10'
        # }
    ),
    html.Div(id='slider_return', style={'textAlign': 'center', 'color': 'grey'}),
    html.Button(id='analyze_button', n_clicks=0, children='Push here for analysis', className='button',)])
        return content
    return
'''

def parse_contents(contents, filename, date):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            pm = pretty_midi.PrettyMIDI(io.BytesIO(decoded))
            return pm
            # return {'data': [{'z': pm.get_piano_roll(), 'type': 'heatmap', 'colorscale': [[0, 'black'], [1, 'white']]}],
            #         'layout': fig_layout
            #         }
        except Exception as e:
            print(e)


@app.callback(Output('testi', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        tiedot = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        rolli = tiedot[0]
        piano=go.Heatmap(z=rolli.get_piano_roll(pianoroll_resolution))
        trace1 = {
            "type": "heatmap",
            'z':rolli.get_piano_roll(pianoroll_resolution),
            "name": "1st stave",
            'colorscale': [[0, 'black'], [1, 'white']],
            'showlegend': True,
            'showscale': False,
        }
        trace2 = {
            "type": "heatmap",
            'z': rolli.instruments[0].get_piano_roll(pianoroll_resolution),
            "name": "1st stave",
            'colorscale': [[0, 'black'], [1, 'white']],
            'showlegend': True,
            'showscale': False,
        }

        return dcc.Graph(figure = {'data':[trace1, trace2],
        'layout': fig_layout
        },config = fig_config)



############################################################
############################################################
################## ANALYZE SCORE CONTENT ENDS ##############
############################################################
############################################################

app.layout = html.Div([
                       html.Div(id='score', children=analyzer_layout, style={'display': 'block'}),

                       html.Div(id='testing'),

                       html.Div(id='hidden-container', style={'display': 'none'}),
                       html.Div(id='hidden2', style={'display': 'none'}),
                       html.Div(id='hidden3', style={'display': 'none'}),
                       html.Div(id='hidden4', style={'display': 'none'}),
                        html.Div(id='hidden_score', style={'display': 'none'}),
                       ])

app.title = 'Orchestration_Analyzer'

if HEROKU:
    if __name__ == '__main__':
        app.run_server(debug=False, threaded=True)
else:
    PORT = 8050
    ADDRESS = '0.0.0.0' #'127.0.0.1'

    if __name__ == '__main__':
        app.run_server(port=PORT, host=ADDRESS, debug=True)