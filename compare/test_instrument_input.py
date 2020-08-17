import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_admin_components as dac
import dash_daq as daq
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash.exceptions import PreventUpdate
import score_component as sc
import plotly.graph_objs as go
import visdcc
import base64
import io
import pretty_midi
from textwrap import dedent
import numpy as np
import json
import pickle

def instrument_input(app, orchestra):
    instruments=list(orchestra.keys())
    dynamics = ['p', 'mf', 'f']
    techs =['normal']
    notes = list(orchestra['violin']['normal']['mf'].keys())
    id=''
    instrument_group = dbc.FormGroup(
        [
            dbc.Label("Select instrument"),
            dbc.RadioItems(
                options=[{"label": i, "value": i} for i in instruments],
                value='violin',
                id="instrument-input{}".format(id),
                inline=True,
            ),
        ],style={'display': 'inline-block'}
    )

    dynamic_group = dbc.FormGroup(
        [
            dbc.Label("Select dynamic"),
            dbc.RadioItems(
                options=[{"label": i, "value": i} for i in dynamics],
                value='mf',
                id="dynamics-input{}".format(id),
                inline=True,

            ),
        ],style={'display': 'inline-block'}
    )

    target_group = html.Div([
        dbc.Label("Set as target", style={'display':'block'}),
        html.Div('orchestration', style={'display':'inline-block'}),
        daq.BooleanSwitch(
            id='target-input{}'.format(id),
            on=False,
            color='red',
        style = {'display': 'inline-block'},
        ),
        html.Div('target', style={'display':'inline-block'})
        ], style={'display': 'inline-block'})

    tech_group = dbc.FormGroup(
        [
            dbc.Label("Select technique"),
            dbc.RadioItems(
                options=[{"label": i, "value": i} for i in techs],
                value='normal',
                id="techs-input{}".format(id),
                inline=True,
            ),
        ],style={'display': 'inline-block'}
    )
    note_group = dbc.FormGroup([
            dbc.Label("Select note"),
            dbc.RadioItems(
                options= [{"label": pretty_midi.note_number_to_name(int(i)), "value": i} for i in notes],
                value=60,
                id="notes-input{}".format(id),
                inline=True,
            ),
    ], style = {'display': 'inline-block'},)

    user_input = html.Div([
        html.Div([instrument_group,note_group,]),
        html.Div([dynamic_group, html.Hr(style={'width':'20px', 'display':'inline-block'}), tech_group, html.Hr(style={'width':'20px', 'display':'inline-block'}), target_group,],),


    ])

    @app.callback([Output('techs-input','options'),
                   Output('notes-input','options'),
                   Output('dynamics-input', 'options')],
                  ([Input('instrument-input', 'value'),
                    Input('techs-input', 'value')])
                  )
    def update_inputs(instrument, technique):
        techs = list(orchestra[instrument].keys())
        techs = [{"label": i, "value": i} for i in techs]

        if technique in list(orchestra[instrument].keys()):
            tech = technique
        else: tech = list(orchestra[instrument].keys())[0]

        dyns = list(orchestra[instrument][tech].keys())
        dyns = [{"label": i, "value": i} for i in dyns]
        notes = list(orchestra[instrument][tech]['p'].keys())
        notes.sort()
        notes = [{"label": pretty_midi.note_number_to_name(int(i)), "value": i} for i in notes]
        return [techs,  notes, dyns]

    return user_input

def new_instrument_input(app, orchestra, id, show_target=True):
    instruments=list(orchestra.keys())
    dynamics = ['p', 'mf', 'f']
    techs =['normal', 'trem']
    notes = list(orchestra['flute']['normal']['mf'].keys())

    if show_target:
        show='block'
    else:
        show='none'

    set_target =         html.Div([
            #dbc.Label("Set as target", style={'display': 'block'}),
            html.Div('orchestration', style={'color':'black','display': 'inline-block'}),
            daq.BooleanSwitch(
                id='target-input{}'.format(id),
                on=False,
                color='red',
                style={'display': 'inline-block'},
            ),
            html.Div('target', style={'color':'black','display': 'inline-block'})
        ],
        style={'marginBottom': -20, 'display': show}
        )

    selected = [
        html.Div('current selection:', style={'color':'black', 'fontSize':24, 'textAlign':'center'}),
         dcc.Dropdown(
        options=[{"label": i, "value": i} for i in instruments],
        value='flute',
        id='instrument-input{}'.format(id),
        multi=False,
        clearable=False,
        #inline=True,
    ),
        dcc.Dropdown(
            options=[{"label": i, "value": i} for i in dynamics],
            value='mf',
            id="dynamics-input{}".format(id),
            multi=False,
            clearable=False,
            placeholder='invalid dynamic!',
            #inline=True,
        ),
        dcc.Dropdown(
            options=[{"label": i, "value": i} for i in techs],
            value='normal',
            id="techs-input{}".format(id),
            multi=False,
            clearable=False,
            placeholder='select valid tech!'
            #inline=True,
        ),
        dcc.Dropdown(
            options=[{"label": pretty_midi.note_number_to_name(int(i)), "value": i} for i in notes],
            value=60,
            id="notes-input{}".format(id),
            multi=False,
            clearable=False,
            placeholder='Out of Range!'
            #inline=True,
        ),
    ]

    pianokeys = html.Div(
        [
            dbc.Button(
                "keys on/off", id="popover-target{}".format(id), size='sm',color="sienna", style={'color':'black', 'border':'none'}
            ),
            dbc.Popover(
                [
                    #dbc.PopoverHeader("Popover header"),
                    dbc.PopoverBody(sc.Pianoinput(id='pno{}'.format(id)), style={'backgroundColor':'rgba(0,0,0,0)', 'color': 'rgba(0,0,0,0)'}),
                ],
                id="popover{}".format(id),
                is_open=False,
                target="popover-target{}".format(id),
                placement='bottom',
                #style={'backgroundColor':'rgba(0,0,0,0)'}
            ),
        ],
        #style={'display':'inline-block'}
    )

    def ddid(type, idx):
        return {'type': type, 'index':idx}

    all_instrument_list = [dbc.DropdownMenuItem(i, id=ddid('orcha_l{}'.format(id), i)) for i in instruments]
    all_instrument_list = dbc.DropdownMenu(all_instrument_list, in_navbar=True, style={'width':'200px','height': '600px', 'position':'fixed', 'overflow':'auto'})
    ww=['piccolo', 'flute', 'alto_flute', 'oboe', 'english_horn', 'clarinet', 'bass_cl', 'bassoon', 'contrabassoon']
    brass=['horn', 'trumpet', 'tenor_trombone', 'bass_trombone', 'tuba']
    percussion = ['timp', 'bass_drum', 'snare', 'piatti', 'tamtam', 'crotales', 'tuned_gongs', 'xylophone']
    strings = ['violin', 'viola', 'cello', 'double_bass', 'solo_violin', 'solo_cello']
    vocal = ['soprano_generic', 'tenor_generic', 'baritone_generic']

    instrument_list = [dbc.DropdownMenuItem('Woodwinds:', header=True)]
    instrument_list += [dbc.DropdownMenuItem(i, id=ddid('orch_l{}'.format(id), i)) for i in ww]
    instrument_list += [dbc.DropdownMenuItem('Brass:', header=True)]
    instrument_list += [dbc.DropdownMenuItem(i, id=ddid('orch_l{}'.format(id), i)) for i in brass]
    instrument_list += [dbc.DropdownMenuItem('Percussion:', header=True)]
    instrument_list += [dbc.DropdownMenuItem(i, id=ddid('orch_l{}'.format(id), i)) for i in percussion]
    instrument_list += [dbc.DropdownMenuItem('Strings:', header=True)]
    instrument_list += [dbc.DropdownMenuItem(i, id=ddid('orch_l{}'.format(id), i)) for i in strings]
    instrument_list += [dbc.DropdownMenuItem('Vocal:', header=True)]
    instrument_list += [dbc.DropdownMenuItem(i, id=ddid('orch_l{}'.format(id), i)) for i in vocal]

    instrument_select = dbc.DropdownMenu(
        instrument_list #.insert(0, dbc.DropdownMenuItem("Woodwinds", header=True),)
    , label='flute', caret=False, id='inst_sel{}'.format(id), color='rgba(0,0,0,0)',
        toggle_style={'color':'black', 'border':'none', 'fontSize':30,},
        direction="right", style={'display':'inline-block', 'marginTop':75, 'textAlign':'right'}, bs_size='m')

    avail_techs=['normal', 'pizz']
    tech_select=html.Div(dbc.DropdownMenu(
        [dbc.DropdownMenuItem(i, n_clicks=0, id=ddid('techs_l{}'.format(id), i)) for i in techs] #.insert(0, dbc.DropdownMenuItem("Woodwinds", header=True),)
    , label='normal', caret=False, id='tech_sel{}'.format(id), color='#dde',
        toggle_style={'color': 'black', 'border': 'none', 'fontSize':30},
        bs_size='sm', style={'bottom':-25, 'textAlign':'center', 'paddingLeft':15}),
    id='tech_above_score{}'.format(id))

    avail_dyns=['p', 'mf', 'f']
    dyn_select=dbc.DropdownMenu(
        [dbc.DropdownMenuItem(i, id=ddid('dyns_l{}'.format(id), i)) for i in dynamics] #.insert(0, dbc.DropdownMenuItem("Woodwinds", header=True),)
    , label='mf', caret=False, id='dyny_sel{}'.format(id), bs_size='sm', color='#dde',
        toggle_style={'color': 'black', 'border': 'none', 'fontSize':30},
        direction="up", style={'top':-25, 'textAlign':'center', 'paddingLeft':15})

    edit = html.Div(sc.Edit(id='edit{}'.format(id), note=61, accidental_margin=60,), style={'cursor':'''url("./assets/mouse_guide.svg") 0 0, crosshair'''})#style={'display':'inline-block', 'verticalAlign':'top'})

    leftmost = html.Div([pianokeys, instrument_select], style={'display':'inline-block', 'verticalAlign':'top'})
    centermost = html.Div([tech_select, edit, dyn_select], style={'display':'inline-block', 'verticalAlign':'top'})
    selection = html.Div(selected, style={'display': 'inline-block', 'marginLeft':10, 'verticalAlign':'top', 'textAlign':'left', 'transform': 'scale(.7)' })
    rightmost = html.Div([set_target, selection], style={'display': 'inline-block', 'marginTop':38,})

    lay = html.Div([leftmost, centermost, rightmost], style={'backgroundColor':'#eed'})

    @app.callback(
        [Output('inst_sel{}'.format(id), 'label'),
        Output('instrument-input{}'.format(id), 'value')],
        [Input({'type':'orch_l{}'.format(id), 'index': ALL}, 'n_clicks')]
    )
    def dd_callback(insts):
        # Check which item fired
        ctx = dash.callback_context  # Callback context to recognize which input has been triggered
        if not ctx.triggered:
            raise PreventUpdate
        else:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        input_id = json.loads(input_id)
        return [input_id['index'], input_id['index']]

    @app.callback(
        [Output('dyny_sel{}'.format(id), 'label'),
        Output('dynamics-input{}'.format(id), 'value')],
        [Input({'type':'dyns_l{}'.format(id), 'index': ALL}, 'n_clicks'),
         Input('edit{}'.format(id), 'dyn')]
    )
    def dd_callback(dyns, dyn):
        # Check which item fired
        ctx = dash.callback_context  # Callback context to recognize which input has been triggered
        if not ctx.triggered:
            raise PreventUpdate
        else:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if input_id=='edit{}'.format(id):
            return [dyn, dyn]
        input_id = json.loads(input_id)
        return [input_id['index'], input_id['index']]

    @app.callback(
        [Output('tech_sel{}'.format(id), 'label'),
         Output('techs-input{}'.format(id), 'value')],
        [Input({'type':'techs_l{}'.format(id), 'index': ALL}, 'n_clicks')]
    )
    def dd_callback(techs):
        # Check which item fired
        ctx = dash.callback_context  # Callback context to recognize which input has been triggered
        if not ctx.triggered or all(i==0 for i in techs):
            raise PreventUpdate
        else:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        input_id = json.loads(input_id)
        return [input_id['index'], input_id['index']]

    @app.callback(
        Output("popover{}".format(id), "is_open"),
        [Input("popover-target{}".format(id), "n_clicks")],
        [State("popover{}".format(id), "is_open")],
    )
    def toggle_popover(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(Output('notes-input{}'.format(id), 'value'),
                  [Input('edit{}'.format(id), 'note'),])
    def set_note_to_current(note):
        return note

    app.clientside_callback("""
    function(note) {
    if (note) {
    return note;
    }
    return 60;
    }
    """,
    Output('edit{}'.format(id), 'note'),
        [Input('pno{}'.format(id), 'note')]
     )
    # @app.callback(
    #     Output('edit', 'note'),
    #     [Input('pno', 'note')]
    # )
    # def edit(note):
    #     if note:
    #         return note
    #     return 60

    @app.callback([Output('techs-input{}'.format(id), 'options'),
                   Output('notes-input{}'.format(id), 'options'),
                   Output('dynamics-input{}'.format(id), 'options'),
                  Output('tech_above_score{}'.format(id), 'children')
                   ],
                  ([Input('instrument-input{}'.format(id), 'value'),
                    Input('techs-input{}'.format(id), 'value')])
                  )
    def update_inputs(instrument, technique):
        techsl = list(orchestra[instrument].keys())
        techs = [{"label": i, "value": i} for i in techsl]
        score_techs = dbc.DropdownMenu(
        [dbc.DropdownMenuItem(i, n_clicks=0,id=ddid('techs_l{}'.format(id), i)) for i in techsl] #.insert(0, dbc.DropdownMenuItem("Woodwinds", header=True),)
    , label=technique, caret=False, id='tech_sel{}'.format(id), color='#dde',
        toggle_style={'color': 'black', 'border': 'none', 'fontSize':30},
        bs_size='sm', style={'bottom':-25, 'textAlign':'center', 'paddingLeft':15})

        if technique in list(orchestra[instrument].keys()):
            tech = technique
        else:
            tech = list(orchestra[instrument].keys())[0]
        dyns = list(orchestra[instrument][tech].keys())
        dyns = [{"label": i, "value": i} for i in dyns]
        notes = list(orchestra[instrument][tech]['p'].keys())
        notes.sort()
        notes = [{"label": pretty_midi.note_number_to_name(int(i)), "value": i} for i in notes]
        return [techs, notes, dyns, score_techs] #score_techs

    return lay



