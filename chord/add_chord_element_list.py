import dash_bootstrap_components as dbc
import dash_daq as daq
import dash_html_components as html
import pretty_midi

dropdown_color = 'black'
dropdown_backgroundColor = 'lightgray'

def add(orchestra, instrument_list, custom_id):

    def set_id(index, set_type):
        return {
            'type': set_type,
            'index': index
        }

    children = []

    for i in range(len(instrument_list)):
        instrument = instrument_list[i]['inst']
        techs = instrument_list[i]['tech']
        notes = instrument_list[i]['note']
        dynamics = instrument_list[i]['dynamic']
        tgt = instrument_list[i]['target']
        onoff = instrument_list[i]['onoff']

        if techs in list(orchestra[instrument].keys()):
            if dynamics in list(orchestra[instrument][techs].keys()):
                if notes in list(orchestra[instrument][techs][dynamics].keys()):
                    children.append(html.Div([html.Div('{}: {} {}'.format(str(len(children)+1), instrument, pretty_midi.note_number_to_name(notes)), style={'display':'inline-block', 'marginRight':'4px', 'textShadow':'2px 2px 2px black'}),
                                                  dbc.Button(
                                                      "Octave up", id=set_id(i, "octave-up{}".format(custom_id)),
                                                      size='sm', color="sienna",
                                                      style={'border': 'none', 'display': 'inline-block', 'width':'100px'}
                                                  ),
                                                  dbc.Button(
                                                      "Octave down", id=set_id(i, "octave-down{}".format(custom_id)),
                                                      size='sm', color="sienna",
                                                      style={'border': 'none', 'display': 'inline-block', 'width':'100px'}
                                                  ),
                                                      dbc.Select(
                                                          options=[{'label': val, 'value': val} for val in list(orchestra.keys())],
                                                          value=instrument,
                                                          style={'backgroundColor':dropdown_backgroundColor, 'width':100, 'color': dropdown_color, 'display':'inline-block'},
                                                          bs_size='sm',
                                                          id=set_id(i, 'inst{}'.format(custom_id)),
                                                      ),
                                                      dbc.Select(
                                                          options=[{'label': val, 'value': val} for val in list(orchestra[instrument].keys())],
                                                          value=techs,
                                                          style={'backgroundColor': dropdown_backgroundColor, 'width':100, 'color': dropdown_color, 'display':'inline-block'},
                                                          bs_size='sm',
                                                          id=set_id(i, 'tech{}'.format(custom_id)),
                                                      ),
                                                      dbc.Select(
                                                          options=[{'label': val, 'value': val} for val in
                                                                   list(orchestra[instrument][techs].keys())],
                                                          value=dynamics,
                                                          style={'backgroundColor': dropdown_backgroundColor, 'width': 60,
                                                                 'color': dropdown_color,},
                                                          bs_size='sm',
                                                          id=set_id(i, 'dyn{}'.format(custom_id)),
                                                      ),
                                                      dbc.Select(
                                                          options=[{'label': pretty_midi.note_number_to_name(val), 'value': val} for val in
                                                                   list(orchestra[instrument][techs][dynamics].keys())],
                                                          value=notes,
                                                          style={'backgroundColor': dropdown_backgroundColor, 'width': 60,
                                                                 'color': dropdown_color, 'display': 'inline-block'},
                                                          bs_size='sm',
                                                          id=set_id(i, 'note{}'.format(custom_id)),
                                                      ),
                                                      daq.ToggleSwitch(
                                                          label='target',
                                                          color='red',
                                                          size=15,
                                                          value=tgt,
                                                          vertical=True,
                                                          id=set_id(i, 'target{}'.format(custom_id)),
                                                          style={'display': 'inline-block', 'textShadow':'2px 2px 2px black'}
                                                      ),html.Div('\xa0 \xa0', style={'display': 'inline-block'}),
                                                      daq.ToggleSwitch(
                                                          label='on/off',
                                                          color='green',
                                                          size=15,
                                                          value=onoff,
                                                          vertical=True,
                                                          id=set_id(i, 'onoff{}'.format(custom_id)),
                                                          style={'display': 'inline-block', 'textShadow':'2px 2px 2px black'}
                                                      ),
                                                  html.Hr(style={'borderTop': '1px solid #bbb'}),
                                                      ], id=set_id(i, 'orch_outer{}'.format(custom_id)), style={'backgroundColor':'primary'}))
    return children