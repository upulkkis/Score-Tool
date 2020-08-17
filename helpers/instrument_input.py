#### Initial constants and imports:
HEROKU = False

if HEROKU:
    import os
    from random import randint
    import flask

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_admin_components as dac
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
else:
    app = dash.Dash(__name__)#, external_stylesheets=[dbc.themes.CYBORG])

app.css.config.serve_locally = True
#print(dbc.themes.CYBORG)
#app.css.append_css({"external_url": dbc.themes.CYBORG})
#app.script.config.serve_locally = True

with open('no_data_orchestra.pickle', 'rb') as handle:
    orchestra = pickle.load(handle)
### Initial ends

#dynamic_group = dbc.InputGroup(
#    [dbc.Button("p"), dbc.Button("mf"), dbc.Button("f")],
#    id='dyn',
#)

def instrument_input(app, id):
    instruments=list(orchestra.keys())
    dynamics = ['p', 'mf', 'f']
    techs =['normal']
    notes = list(orchestra['violin']['normal']['mf'].keys())

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
        html.Div([dynamic_group, html.Hr(style={'width':'20px', 'display':'inline-block'}), tech_group, html.Hr(style={'width':'20px', 'display':'inline-block'}),],),


    ])

    @app.callback([Output('techs-input{}'.format(id),'options'),
                   Output('notes-input{}'.format(id),'options'),
                   Output('dynamics-input{}'.format(id), 'options')],
                  ([Input('instrument-input{}'.format(id), 'value'),
                    Input('techs-input{}'.format(id), 'value')])
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





app.layout=html.Div([
    instrument_input(app, 'jopo'),
])

#### Start the app:
app.title = 'Orchestration_Analyzer'
if HEROKU:
    if __name__ == '__main__':
        app.run_server(debug=False, threaded=True)
else:
    PORT = 8050
    ADDRESS = '0.0.0.0' #'127.0.0.1'

    if __name__ == '__main__':
        app.run_server(port=PORT, host=ADDRESS, debug=True)


