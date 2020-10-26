import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_admin_components as dac
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash.exceptions import PreventUpdate
import dash_daq as daq
import score_component as dsc
import visdcc
import base64
import io
import pretty_midi
import numpy as np
import json
from helpers import hertz_to_microtone, sort_for_vexflow
from chord import chord_db_to_color
from chord import add_chord_element_list

def chord_testing(app, orchestra, custom_id='', initial_data=''):
    initial_chord = []
    collapse = False

    if initial_data:
        collapse=True
        #Initial data doesn't work, so using this to collapse menu!
        #initial_chord = add_chord_element_list.add(orchestra, initial_data, custom_id)

    chord_selector_list = ['brass_and_flutes', 'tutti_orchestra', 'woodwinds', 'solo_singer']
    pre_selected_chords = [
        [
        {'inst':'flute', 'tech':'normal', 'dynamic':'mf', 'note':72, 'target':True, 'onoff':True},
        {'inst':'trumpet', 'tech':'normal', 'dynamic':'mf', 'note':64, 'target':False, 'onoff':True},
        {'inst':'trumpet', 'tech':'normal', 'dynamic':'mf', 'note':60, 'target':False, 'onoff':True},
        {'inst':'tenor_trombone', 'tech':'normal', 'dynamic':'mf', 'note':52, 'target':False, 'onoff':True},
    ],
        [
        {'inst': 'flute', 'tech': 'normal', 'dynamic': 'p', 'note': 76, 'target': False, 'onoff': True},
        {'inst': 'oboe', 'tech': 'normal', 'dynamic': 'p', 'note': 64, 'target': False, 'onoff': True},
        {'inst': 'clarinet', 'tech': 'normal', 'dynamic': 'p', 'note': 55, 'target': False, 'onoff': True},
        {'inst': 'bassoon', 'tech': 'normal', 'dynamic': 'p', 'note': 48, 'target': False, 'onoff': True},
        ],
    ]

    dropdown_color = 'black'
    dropdown_backgroundColor = 'lightgray'

    orchestration_toast = dbc.Toast([html.Div('Here ↑', style={'textAlign':'right'}),
        "When you add instruments, they appear on the closed menu. The menu can be opened by clicking the top right corner clipboard-icon: ", html.Br(),dac.Icon(icon='clipboard', size='2x')
    ],
        id="orchestration-toast{}".format(custom_id),
        header="Add instrument help",
        is_open=False,
        dismissable=True,
        icon="success",
        # top: 66 positions the toast below the navbar
        style={"position": "fixed", "top": 50, "right": 10, "width": 350, 'opacity':1, 'backgroundColor':'#eed solid'},
        body_style={'opacity': 1, 'backgroundColor': '#eed solid', 'color': 'black'}
    ),

    from compare import test_instrument_input
    add_instruments_box = html.Div([
        dac.Box([
        dac.BoxHeader("minimize → ",title='Add instruments  ', style={'height':60}),
        dac.BoxBody([
            dbc.Row([
            dbc.Col(dcc.Dropdown(id='chord_selector{}'.format(custom_id),
                         options=[{'label': i, 'value': i} for i in chord_selector_list],
                         placeholder='Click for pre-defined chords', className='chordSelector', style={'width': '100%'},), #style={'width': '100%'},
                    ),
            dbc.Col(dcc.Upload(dbc.Button('Load saved orchestration', size='sm', style={'margin':'0px', 'padding':'8px', 'width': '100%'}), id='upload_chord{}'.format(custom_id), ),
                    ),
            dbc.Col([dbc.Button('Save current orchestration', id='download{}'.format(custom_id), n_clicks=0, size='sm', style={'padding':'8px','width': '100%'},),
            html.A('',id='json-download{}'.format(custom_id), download="data.orchestration",href="",target="_blank",style={'width': '100%'}
                ),
                    ]),
            dbc.Col(dbc.Button('clear all', id='clear_all{}'.format(custom_id), n_clicks=0, size='sm', style={'padding':'8px','width': '100%'})),
                visdcc.Run_js(id='javascript_chrd{}'.format(custom_id)),
            ], justify='between', style={'margin':'1px'}, no_gutters=True),
            dbc.Row([
        #dbc.Button(id='add_instrument_button{}'.format(custom_id), n_clicks=0, children=['Click to add current selection to orchestration', dbc.Badge("", id='add_badges{}'.format(custom_id), color="success", style={'top':-10, 'right':-5})],),
        #,
        html.Div( #Hide the remove button until fixed!
        html.Div(id='hidebutton{}'.format(custom_id), children=[dbc.Button(id='submit{}'.format(custom_id), n_clicks=0, children='Remove last instrument'),]),
        style={'display':'none'}),
        dbc.Button(id='view_orchestration{}'.format(custom_id), n_clicks=0, children='Click for help', style={'display':'none'}),
            ], justify='between', style={'margin':'1px'}),
        html.Div(test_instrument_input.new_instrument_input(app, orchestra, custom_id), style={'textAlign': 'center', }),
            dbc.Button(id='add_instrument_button{}'.format(custom_id), n_clicks=0, children='Click to add current selection to orchestration', style={'width':'100%', 'border':0, 'color':'black'}, className='addinst_btn'),
        ]),
        ],elevation=4, width=12, style={'width':'100%'}, collapsed=collapse
        ),
        html.Div(id='idx_container{}'.format(custom_id), style={'display':'none'})
    ])
    #print(add_instruments_box)

    #print(dsc.__version__)
    # test_orchestration_layout=html.Div([
    # help('single_start'),
    # help('single_analyze'),
    # html.Div(id='result', className='waiting')
    # ])
    test_orchestration_layout = html.Div([
        dbc.Row([
            dbc.Col(
        html.Div(id='summary_container{}'.format(custom_id)), width=8
            ),
            dbc.Col(
        html.Div([dbc.Badge("", id='add_badge{}'.format(custom_id), color="success",
                            style={'zIndex': 10000, 'position': 'absolute'}),
                  # style={'top':-10, 'right':-5, 'zIndex':100000, 'verticalAlign': 'bottom','marginBottom':5}),
                  dbc.DropdownMenu(id='orchestration_dropdown{}'.format(custom_id),
                                   label='Click to check or modify your orchestration', children=initial_chord, className='orch_drpdwn'),
                  ], id='outer_orchestration_dropdown{}'.format(custom_id), ), width=4
            ),
        ]),
        html.Div(id='instrumentation_container{}'.format(custom_id), style={'display':'none'}),
        dbc.Row([
        dbc.Col(dac.Box([
            dac.BoxHeader(title='Orchestration', style={'height': 60}, collapsible=False),
            dac.BoxBody(
                html.Div(children=html.Div(''),#dsc.Orchestration(notes=[], instruments=[], target=[]),
                         id='orchestration{}'.format(custom_id), style={'width': 330, 'backgroundColor': '#eed'}))
        ], elevation=4, style={'display': 'inline-block'}),
            width=3),
        dbc.Col(dac.Box([
    #dac.BoxHeader(title='Analysis data'),
    dac.BoxBody([html.Div(id='result{}'.format(custom_id), className='waiting')

        ])
    ],width=12),width=9)
        ])])

    @app.callback(
        Output("orchestration-toast{}".format(custom_id), "is_open"),
        [Input("view_orchestration{}".format(custom_id), "n_clicks")],
    [State('orchestration_dropdown{}'.format(custom_id), 'children')])
    def open_toast(n, children):
        if n % 2:
            return True
        return False

    inst_list=list(orchestra.keys())
    tech_list=['normal']
    dyn_list=['p', 'mf', 'f']
    note_list=np.arange(128)

    instrument_lista=[]
    dropdown_lista=[]
    check_lista=[]
    tech_lista=[]
    dyn_lista=[]
    note_lista=[]
    onoff_lista=[]

    #print(add_instruments_box)
    #Tällä callbackillä luetaan käyttäjän asettamat soitinspeksit ja päivitetään graafit reaaliajassa:
    from score import new_masking_slice
    @app.callback(
        [Output('hidden-container{}'.format(custom_id), 'children'),
         #Output({'type': 'tech', 'index': ALL}, 'options'), #Päivitetään tekniikat valitun instrumentin mukaan
        #Output({'type': 'note', 'index': ALL}, 'options'), #Päivitetään käytettävät nuotit instrumentin mukaan
        Output('summary_container{}'.format(custom_id), 'children'),
        Output('result{}'.format(custom_id), 'children'),
         Output('orchestration{}'.format(custom_id), 'children'),
         Output({'type': 'orch_outer{}'.format(custom_id), 'index': ALL}, 'style'),
         Output('idx_container{}'.format(custom_id), 'children'),
         ],
        [Input({'type': 'inst{}'.format(custom_id), 'index': ALL}, 'value'), #Päivitetään valikot vain jos instrumentti vaihtuu
        #],
        Input({'type': 'tech{}'.format(custom_id), 'index': ALL}, 'value'), #Katsotaan valikoiden arvot State:lla niin ei turhaan päivitetä
         Input({'type': 'dyn{}'.format(custom_id), 'index': ALL}, 'value'),
         Input({'type': 'note{}'.format(custom_id), 'index': ALL}, 'value'),
         Input({'type': 'target{}'.format(custom_id), 'index': ALL}, 'value'),
         Input({'type': 'onoff{}'.format(custom_id), 'index': ALL}, 'value'),
         ],
        [State('orchestration{}'.format(custom_id), 'children'),
         State({'type': 'orch_outer{}'.format(custom_id), 'index': ALL}, 'style')]
    )
    def list_update(inst, tech, dyn, note, tgt, onoff, orch, outer_style):

        note = [int(n) for n in note]
        instrumentation=dict()
        instrumentation['inst']=inst
        instrumentation['tech']=tech
        #techs = [[{'label': val, 'value': val} for val in list(orchestra[i].keys())] for i in inst] #Tsekataan kustakin soittimesta saatavat tekniikat
        instrumentation['dyn']=dyn
        instrumentation['note']=note
        #notes = [[{'label': pretty_midi.note_number_to_name(val), 'value': val} for val in list(orchestra[i]['normal']['mf'].keys())] for i in inst] #Tsekataan instrumentin nuottivalikoima
        instrumentation['target']=tgt
        instrumentation['onoff']=onoff
        json_dump = json.dumps(instrumentation) #Dumpataan json muodossa piilotettuun div:n
        #View the warning, which will be replaced
        graphs=html.Div('Technique, dynamic or note out of range')
        summary=html.Div('')
        tgts=[]
        #Notes must be converted for react component
        notes=[]
        #Annotation for notes in score
        annotations=[]
        orchestration_slice = []
        if inst!=[]:

            for i in range(len(inst)):
                # Check that you input proper values:
                if tech[i] in list(orchestra[inst[i]].keys()):
                    if dyn[i] in list(orchestra[inst[i]][tech[i]].keys()):
                        if int(note[i]) in list(orchestra[inst[i]][tech[i]][dyn[i]].keys()):
                            orchestration_slice.append([inst[i], tech[i], dyn[i], int(note[i]), tgt[i], onoff[i]]) # Note comes as string, convert to int
                            #Do annotations
                            annotations.append(inst[i]+" "+dyn[i]+" "+tech[i])
                            #If marked as target, add to target list
                            if tgt[i]:
                                tgts.append(i)
                            # Do the graphics slice

        #This used to be the place of "orchestration"-module
        #Sort notes as numbers:

        def format_notecolor(peaks, masking_notevalues):
            for i in range(len(masking_notevalues)):
                if i>0:
                    if masking_notevalues[i]-masking_notevalues[i-1]<4 and peaks[i-1]!=0:
                        peaks[i]=0
            peaks = [i**3 for i in peaks]
            peaks = [i/(90**3) for i in peaks]

            return peaks

        srt_idx=[]
        if orchestration_slice != []:
            #Return dicts: orchestration & target + graph:
            orchestration, target, graphs, summary, masking_order_idx = new_masking_slice.get_slice(orchestration_slice, orchestra)  # [dcc.Graph(id='masking-graph',figure=fig, config=fig_config)] #html.Div(''.join(kaikki)),

            #Decimate red squares too close each other #No need in the new module!
            masking_notevalues = [pretty_midi.hz_to_note_number(int(i)) for i in orchestration['peak_locs']]
            orch_masking_mod_locs = orchestration['masking_locs'].copy()
            orch_masking_mod_locs[0]=20;

            #New masking_notevalues from masking vector instead of the overtones
            masking_notevalues = [pretty_midi.hz_to_note_number(int(i)) for i in orch_masking_mod_locs]

            #orch_peaks = format_notecolor(orchestration['peaks'], masking_notevalues)
            #masking_colors = ['rgba(255, 0, 0, {})'.format(i) for i in orch_peaks]

            #New masking colors from orchestration masking threshold vector
            masking_colors = ['rgba(255, 0, 0, {})'.format(i/100) for i in orchestration['masking_threshold']]
            masking_colors = [chord_db_to_color.color(i) for i in orchestration['masking_threshold']]

            masking_notesizes = np.ones(len(masking_notevalues)) + 100

            target_notevalues = [pretty_midi.hz_to_note_number(int(i)) for i in target['peak_locs']]
            target_peaks = format_notecolor(target['peaks'], target_notevalues)
            target_colors = ['rgba(0, 0, 0, {})'.format(i) for i in target_peaks]

            target_notesizes = np.ones(len(target_notevalues)) + 40

            score_mask = dsc.Masking(masking_notevalues=masking_notevalues, masking_colors=masking_colors,
                                     masking_notesizes=masking_notesizes,
                                     target_notevalues=target_notevalues, target_colors=target_colors,
                                     target_notesizes=target_notesizes)
            centroid_notes = []
            centroid_markings = []
            if orchestration['centroid']:
                centroid_markings.append('Orch. {:.1f}Hz'.format(float(orchestration['centroid'])))
                centroid_notes.append(orchestration['centroid'])
            if target['centroid']:
                centroid_markings.append('Target {:.1f}Hz'.format(float(target['centroid'])))
                centroid_notes.append(target['centroid'])

            centroid_notes, centroid_markings, tgts_dummy, highs, dummy_sort_idx = sort_for_vexflow.sort_notes(centroid_notes, centroid_markings, [])
            centroid_notes = [hertz_to_microtone.convert(i) for i in centroid_notes]

            centroids_score = dsc.Orchestration(id='centroid_score{}'.format(custom_id), notes=centroid_notes, instruments=centroid_markings, target=[], width=100)

            #Do highlights array and append colors for 1st masker=red, 2nd=magenta and 3rd=yellow:

            for style in outer_style:
                style['backgroundColor'] = 'primary'

            for i in tgts:
                try:
                    outer_style[i]['backgroundColor'] = 'green'
                except:
                    pass

            highlights=[]
            for i in range(len(orchestration_slice)):
                highlights.append('')
            for i in range(len(masking_order_idx)):
                try:
                    if i==0:
                        highlights[masking_order_idx[i]]='red'
                        outer_style[masking_order_idx[i]]['backgroundColor'] = 'red'
                    if i==1:
                        highlights[masking_order_idx[i]] = 'magenta'
                        outer_style[masking_order_idx[i]]['backgroundColor'] = 'magenta'
                    if i == 2:
                        highlights[masking_order_idx[i]] = 'yellow'
                        outer_style[masking_order_idx[i]]['backgroundColor'] = 'yellow'
                except:
                    pass

            note, annotations, tgts, highlights, srt_idx = sort_for_vexflow.sort_notes(note, annotations, tgts, highlights)

            # Convert notes to note names and set to lower case for React
            notes = [pretty_midi.note_number_to_name(int(i)) for i in note]  # Change to note names
            notes = [i.lower() for i in notes]

            # Use my shiny new Score module!
            orch = [html.Div('Your orchestration score. Target is marked on green. If target is masked, heaviest masker is marked on red, second heaviest on magenta, third on yellow.', style={'color': 'black'}),
                    dsc.Orchestration(id='orch{}'.format(custom_id), notes=notes, instruments=annotations, target=tgts,
                                      target_color='green', highlights=highlights, width=150, text_space=200),
                    html.Div(
                        'Registers masked by orchestration. Green means almost no masking, yellow some masking and red heavy masking on register. Orchestration and target centroids, i.e. "where you hear the sound", is marked on right.',
                        style={'color': 'black'}),
                    ]
            orch.append(score_mask)
            orch.append(centroids_score)

        return json_dump, summary, graphs, orch, outer_style, json.dumps(srt_idx)

    @app.callback(
        [Output('orch{}'.format(custom_id), 'target'),
         Output({'type': 'target{}'.format(custom_id), 'index': ALL}, 'value'),
         ],
        [Input('orch{}'.format(custom_id), 'onClick')],
        [State('orch{}'.format(custom_id), 'target'),
         State({'type': 'target{}'.format(custom_id), 'index': ALL}, 'value'),
         State('idx_container{}'.format(custom_id),'children')]
    )
    def quickTarget(onclick, tgt, tgt_lst, srt_idx):
        if onclick == None:
            raise PreventUpdate
        print(onclick)
        print(srt_idx)

        #Get indexes of the sort and get the original index
        srt_idx = json.loads(srt_idx)
        old_tgt = srt_idx[onclick] #Index of original target index

        if onclick in tgt:
            tgt.remove(onclick)
            tgt_lst[old_tgt]=False
        else:
            tgt.append(onclick)
            tgt_lst[old_tgt]=True
        return [tgt, tgt_lst]

    #Uusi callback
    @app.callback(
        [Output('orchestration_dropdown{}'.format(custom_id), 'children'),
        Output('hidebutton{}'.format(custom_id), 'style'),
         Output('add_badge{}'.format(custom_id), 'children'),
         Output('instrumentation_container{}'.format(custom_id), 'children')],
        [Input('add_instrument_button{}'.format(custom_id), 'n_clicks'),
         Input('submit{}'.format(custom_id), 'n_clicks'),
         Input('chord_selector{}'.format(custom_id), 'value'),
         Input('upload_chord{}'.format(custom_id), 'contents'),
        Input({'type': 'delete{}'.format(custom_id), 'index': ALL}, 'n_clicks'),
         Input('clear_all{}'.format(custom_id), 'n_clicks')],
        [State('orchestration_dropdown{}'.format(custom_id), 'children'),
         State('instrument-input{}'.format(custom_id),'value'),
    State('techs-input{}'.format(custom_id),'value'),
    State('dynamics-input{}'.format(custom_id),'value'),
    State('notes-input{}'.format(custom_id),'value'),
    State('target-input{}'.format(custom_id),'on'),
    State('instrumentation_container{}'.format(custom_id), 'children'),
         ])
    def display_dropdowns(n_clicks, remove, chord_selector, upload, delete, clear_all, children, instrument, techs, dynamics, notes, tgt, instrumentation):
        ctx = dash.callback_context  # Callback context to recognize which input has been triggered
        if not ctx.triggered:
            raise PreventUpdate
        else:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if not instrumentation:
            instrumentation = []
        else:
            instrumentation = json.loads(instrumentation)

        #Delete the right index
        try: #Must use try, because json load will fail on plain ascii
            input_id=json.loads(input_id)
            if input_id['type'] == 'delete{}'.format(custom_id):
                for child in range(len(children)):
                    if children[child]['props']['id']['index'] == input_id['index']:
                        index_to_pop = child
                        children.pop(index_to_pop)
                        instrumentation.pop(index_to_pop)
        except:
            pass

        if input_id == 'clear_all{}'.format(custom_id):
            children=[]

        #If user loads pre-defined chords, do the selection
        if input_id == 'chord_selector{}'.format(custom_id):
            if chord_selector == 'brass_and_flutes':
                children = add_chord_element_list.add(orchestra, pre_selected_chords[0], custom_id)
                instrumentation = pre_selected_chords[0]
            else:
                pass

        if input_id == 'upload_chord{}'.format(custom_id):
            valid = False

            # Check if we have data
            if upload:
                content_type, content_string = upload.split(',')

                decoded = base64.b64decode(content_string)
                decoded = decoded.decode('utf-8')
                decoded.replace(": true,", ": True,").replace(": false,", ": False,")

                # Check if file contains a list of valid objects:
                try:
                    js = json.loads(decoded)
                    for instrument in js:
                        keys = list(instrument.keys())
                        if all(x in keys for x in ['inst', 'tech', 'dynamic', 'note', 'target', 'onoff']):
                            valid = True
                except Exception as e:
                    print(e)
                    return html.Div([
                        'There was an error processing this file.'
                    ])
            if valid:
                children = add_chord_element_list.add(orchestra, js, custom_id)
                instrumentation = js

        if input_id == 'add_instrument_button{}'.format(custom_id):
            # if n_clicks == 0:
            #     children = []
            #     return [children, {'display': 'none'},'']
            #
            # clicks=n_clicks-remove
            #
            # if remove == 0:
            #     pass
            # if clicks==0 and len(children)==2:
            #     children = []
            #     return [children, {'display': 'none'},'']
            # elif len(children)>clicks and len(children)>0:
            #     children.pop()
            #     if len(children)==0: rem_button={'display': 'none'}
            #     else: rem_button={'display': 'block'}
            #     return [children, rem_button,len(children)]

            def set_id(set_type):
                return {
                    'type': set_type,
                    'index': n_clicks
                }
            onoff = 1

            #Check that you input proper values:
            if techs in list(orchestra[instrument].keys()):
                if dynamics in list(orchestra[instrument][techs].keys()):
                    if notes in list(orchestra[instrument][techs][dynamics].keys()):
                        instrumentation.append({'inst': instrument, 'tech': techs, 'dynamic': dynamics,
                                           'note': notes, 'target': tgt, 'onoff': onoff})
                        children.append(html.Div([html.Div('{}: {} {}'.format(str(len(children)+1), instrument, pretty_midi.note_number_to_name(notes)), style={'display':'inline-block', 'marginRight':'4px', 'textShadow':'2px 2px 2px black'}),
                                                  dbc.Button(
                                                      "Octave up", id=set_id("octave-up{}".format(custom_id)),
                                                      size='sm', color="sienna",
                                                      style={'border': 'none', 'display': 'inline-block', 'width':'100px'}
                                                  ),
                                                  dbc.Button(
                                                      "Octave down", id=set_id("octave-down{}".format(custom_id)),
                                                      size='sm', color="sienna",
                                                      style={'border': 'none', 'display': 'inline-block', 'width':'100px'}
                                                  ),
                                                      dbc.Select(
                                                          options=[{'label': val, 'value': val} for val in list(orchestra.keys())],
                                                          value=instrument,
                                                          style={'backgroundColor':dropdown_backgroundColor, 'width':100, 'color': dropdown_color, 'display':'inline-block'},
                                                          bs_size='sm',
                                                          id=set_id('inst{}'.format(custom_id)),
                                                      ),
                                                      dbc.Select(
                                                          options=[{'label': val, 'value': val} for val in list(orchestra[instrument].keys())],
                                                          value=techs,
                                                          style={'backgroundColor': dropdown_backgroundColor, 'width':100, 'color': dropdown_color, 'display':'inline-block'},
                                                          bs_size='sm',
                                                          id=set_id('tech{}'.format(custom_id)),
                                                      ),
                                                      dbc.Select(
                                                          options=[{'label': val, 'value': val} for val in
                                                                   list(orchestra[instrument][techs].keys())],
                                                          value=dynamics,
                                                          style={'backgroundColor': dropdown_backgroundColor, 'width': 60,
                                                                 'color': dropdown_color,},
                                                          bs_size='sm',
                                                          id=set_id('dyn{}'.format(custom_id)),
                                                      ),
                                                      dbc.Select(
                                                          options=[{'label': pretty_midi.note_number_to_name(val), 'value': val} for val in
                                                                   list(orchestra[instrument][techs][dynamics].keys())],
                                                          value=notes,
                                                          style={'backgroundColor': dropdown_backgroundColor, 'width': 60,
                                                                 'color': dropdown_color, 'display': 'inline-block'},
                                                          bs_size='sm',
                                                          id=set_id('note{}'.format(custom_id)),
                                                      ),
                                                      daq.ToggleSwitch(
                                                          label='target',
                                                          color='red',
                                                          size=15,
                                                          value=tgt,
                                                          vertical=True,
                                                          id=set_id('target{}'.format(custom_id)),
                                                          style={'display': 'inline-block', 'textShadow':'2px 2px 2px black'}
                                                      ),html.Div('\xa0 \xa0', style={'display': 'inline-block'}),
                                                      daq.ToggleSwitch(
                                                          label='on/off',
                                                          color='green',
                                                          size=15,
                                                          value=onoff,
                                                          vertical=True,
                                                          id=set_id('onoff{}'.format(custom_id)),
                                                          style={'display': 'inline-block', 'textShadow':'2px 2px 2px black'}
                                                      ),
                                                  dbc.Button(
                                                      "DELETE", id=set_id("delete{}".format(custom_id)),
                                                      size='sm', color="danger",
                                                      style={'border': 'none', 'display': 'inline-block',
                                                             'width': '100px', 'backgroundColor':'red'}
                                                      ),
                                                  html.Hr(style={'borderTop': '1px solid #bbb'}),
                                                      ], id=set_id('orch_outer{}'.format(custom_id)), style={'backgroundColor':'primary'}))
        orch_len = str(len(children))

        if len(children)==1:
            orch_len += ' instrument in orchestration'
        else:
            orch_len += ' instruments in orchestration'
        return [children, {'display': 'block'}, orch_len, json.dumps(instrumentation)]



    fig_layout = {
               'plot_bgcolor': "rgba(0,0,0,0)",
               'paper_bgcolor': "rgba(0,0,0,0)",
                'font': {
                    'color': 'white'
                }
           }
    fig_config = {
                'displayModeBar': False
            }

    from score import new_masking_slice
    @app.callback(Output('result{}'.format(custom_id), 'id'), [Input('submit{}'.format(custom_id), 'n_clicks')],
                  [State('hidden-container{}'.format(custom_id), 'children'),
                  State({'type': 'inst{}'.format(custom_id), 'index': ALL}, 'value'),
                  State({'type': 'tech{}'.format(custom_id), 'index': ALL}, 'value'),
                   State({'type': 'dyn{}'.format(custom_id), 'index': ALL}, 'value'),
                   State({'type': 'note{}'.format(custom_id), 'index': ALL}, 'value'),
                   State({'type': 'target{}'.format(custom_id), 'index': ALL}, 'value'),
                   State({'type': 'onoff{}'.format(custom_id), 'index': ALL}, 'value'),
                  ])
    def display_result(n_clicks, json_dump, inst, tech, dyn, note, target, onoff):
        if n_clicks >0:
            instrumentation = json.loads(json_dump) #Ladataan piilotetusta divistä testattava orkestraatio
            orchestration_slice = []

            #targets=0
            #fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])], layout=fig_layout)
            for i in range(len(inst)):
                # Data: instrument, technique, dynamics, note, target, on/off
                orchestration_slice.append([inst[i], tech[i], dyn[i], note[i], target[i], onoff[i]])
                #targets=targets+int(target[i]) #Check if there's any targets
            #if targets == 0:
            #    return "Define at least one intrument as target"
            #else:
            return new_masking_slice.get_slice(orchestration_slice, orchestra, custom_id)#[dcc.Graph(id='masking-graph',figure=fig, config=fig_config)] #html.Div(''.join(kaikki)),
        else:
            return ""

    @app.callback(Output({'type': 'note{}'.format(custom_id), 'index': MATCH}, 'value'),
                  [Input({'type': 'octave-down{}'.format(custom_id), 'index': MATCH}, 'n_clicks'),
                  Input({'type': 'octave-up{}'.format(custom_id), 'index': MATCH}, 'n_clicks'),
                   ],
                  [State({'type': 'note{}'.format(custom_id), 'index': MATCH}, 'value'),])
    def octave_shift(octaved, octaveu, curr_note):
        ctx = dash.callback_context  # Callback context to recognize which input has been triggered
        if not ctx.triggered:
            raise PreventUpdate
        else:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        input_id = json.loads(input_id)
        if input_id['type'] == 'octave-up{}'.format(custom_id):
            #print(curr_note)
            curr_note+=12
        if input_id['type'] == 'octave-down{}'.format(custom_id):
            curr_note-=12
        return curr_note

    #Prepare instrumentation for download
    @app.callback(Output('json-download{}'.format(custom_id), 'href'),
                  [Input('download{}'.format(custom_id), 'n_clicks')],
                  [State('instrumentation_container{}'.format(custom_id), 'children')]
                  )
    def prepare_download(c, storage):
        if c > 0:
            return '/downloadChord{}?value={}'.format(custom_id,storage)
            # media_type = 'text/txt'
            # href_data_downloadable = f'data:{media_type};charset=utf-8,{storage}'
            # return href_data_downloadable
        return ''

    if custom_id:
        @app.server.route('/downloadChord{}'.format(custom_id))
        def download_file_custom():
            value = flask.request.args.get('value')
            str_io = io.StringIO()
            str_io.write(value)
            mem = io.BytesIO()
            mem.write(str_io.getvalue().encode('utf-8'))
            mem.seek(0)
            str_io.close()
            return flask.send_file(mem,
                                   mimetype='text/plain',
                                   attachment_filename='orchestration.chord',
                                   as_attachment=True)
    else:
        @app.server.route('/downloadChord{}'.format(custom_id))
        def download_file():
            value = flask.request.args.get('value')
            str_io = io.StringIO()
            str_io.write(value)
            mem = io.BytesIO()
            mem.write(str_io.getvalue().encode('utf-8'))
            mem.seek(0)
            str_io.close()
            return flask.send_file(mem,
                                   mimetype='text/plain',
                                   attachment_filename='orchestration.chord',
                                   as_attachment=True)

    #Auto-click download link with javascript after creation
    @app.callback(
        Output('javascript_chrd{}'.format(custom_id), 'run'),
        [Input('json-download{}'.format(custom_id), 'href')])
    def auto_click_download(x):
        if x:
            return "var a = document.getElementById('json-download{}'); a.click();".format(custom_id)
        return ""

    chord_layout = html.Div([html.Div(id='hidden-container{}'.format(custom_id), style={'display': 'none'}), test_orchestration_layout, orchestration_toast[0]])

    return add_instruments_box, chord_layout
