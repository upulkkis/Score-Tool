import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import dash_admin_components as dac
from helpers import constants
import numpy as np

def masking_example_slide(app):
    color_palette=dict()
    color_palette['font']='lightgray'
    color_palette['plot']="rgba(0,0,0,0)"
    color_palette['paper']= 'black' #"rgba(0,0,0,0)"
    color_palette['stem']='#e1b382'  # /* SAND COLOR */
    color_palette['c_bands']="rgba(0.2,0.5,0.0,3)"
    color_palette['background']= '#363636'; #Same as in CSS

    fig_layout = {
        'plot_bgcolor': color_palette['plot'],
        'paper_bgcolor': color_palette['paper'],

        'font': {
            'color': color_palette['font']
        },
        'xaxis': {'title': 'Frequency in Hz', 'type': 'log',
                  #'rangeslider': {'visible': True},
                  #'rangeselector': {'visible': True,
                  #                  'buttons': [{'step': 'all'}, {'step': 'day'}, {'step': 'hour'}]},
                  'showgrid': False,
                  # 'range': [1, 1.5],
                  },
        "title": "Masking example",
        'yaxis': {'title': 'dB (SPL)', 'showgrid': False, 'zeroline': False, 'range': [0, 50]},
        'dragmode': 'pan',
        'transition': {'duration': 300}
    }

    fig_config = {
        'displayModeBar': False
    }

    target=dict()
    target['peak_locs']=[300, 1000, 3500]
    target['peaks']=[12, 40, 20]
    trace1 = {

        "mode": "markers+text",
        "type": "scatter",
        "x": target['peak_locs'],
        "y": target['peaks'],
        "text": ['sinewave sound 300Hz', 'sinewave sound 1kHz', 'sinewave sound 3.5kHz'],
        'textposition': 'top center',
        "name": "Audible peaks",
        "marker": {'symbol': 'x', 'size': 12, 'line': {'width': 0}, 'colorscale' : [[0, 'red'], [1., 'green']], 'color': [1., 1., 1.]},
    # Tässä laitetaan eri väriset rastit kuuluvuuden mukaan
        "line": {'color': 'Green', 'width': 5},
    }
    # Build stems for peaks
    peak_stems_x = []
    peak_stems_y = []
    for i in range(len(target['peak_locs'])):
        peak_stems_x.append(target['peak_locs'][i] - 10)
        peak_stems_y.append(0)
        peak_stems_x.append(target['peak_locs'][i])
        peak_stems_y.append(target['peaks'][i])
        peak_stems_x.append(target['peak_locs'][i] + 10)
        peak_stems_y.append(0)
        peak_stems_x.append(None)
        peak_stems_y.append(None)

    stem_trace = {
        "mode": "lines",
        "type": "scatter",
        "x": peak_stems_x,
        "y": peak_stems_y,
        "line": {'color': color_palette['stem'], 'width': 4},
        "opacity": 0.7,
        "showlegend": False,
    }

    orchestration=dict()
    orchestration['masking_locs']=[500, 1000, 1500]
    orchestration['masking_threshold']=[0, 0, 0]
    trace2 = {
        "mode": "lines",
        "type": "scatter",
        "x": orchestration['masking_locs'],
        "y": orchestration['masking_threshold'],
        "name": "masked area",
        "line": {'color': 'orange', 'width': 0},
        "fill": "tonexty"
    }

    trace3 = {
        "showlegend": False,
        "mode": "lines",
        "type": "scatter",
        "x": orchestration['masking_locs'],
        "y": np.zeros(106),
        'line': {'width': 0}
    }


    def generate_barks():
        xx = []
        yy = []
        for f in constants.barks:
            xx = [*xx, *[f, f, None]]
            yy = [*yy, *[100, -20, None]]
        xx[-1] = []
        yy[-1] = []
        return xx, yy


    xx, yy = generate_barks()
    vertical_line = {
        "mode": "lines",
        "type": "scatter",
        "x": xx,
        "y": yy,
        "opacity": 0.3,
        "name": "Critical bands",
        "line": {"color": color_palette['c_bands']},
    }
    # vertical_line = {'x':[0], 'y':[0]} #For debug
    hearing_threshold = {
        "mode": "lines",
        "type": "scatter",
        "x": constants.threshold[:, 0],
        "y": constants.threshold[:, 2],
        "opacity": 0.7,
        "name": "Hearing threshold",
        "line": {"dash": "dash", "color": "red"},
    }

    fig1 = go.Figure(data=[trace1, trace3, trace2, vertical_line, stem_trace], layout=fig_layout)

    sound_volume = dcc.Slider(
        id='Sound_loudness',
        updatemode='drag',
        min=0,
        max=100,
        step=1,
        value=10,
        vertical=True,
        #className='vol-slider',
        #dots= True,
        tooltip={
            'always_visible': False,
            'placement': 'bottom'
        },
    marks={0:'0dB', 10:'10dB', 20:'20dB',30:'30dB',40:'40dB',50:'50dB',60:'60dB',70:'70dB',80:'80dB',90:'90dB',100:'100dB',
             },
    ),

    masking_example_layout = html.Div([html.Div(dcc.Graph(id='masking-example',figure=fig1, config=fig_config),
                              style = {'display': 'inline-block'}), html.Div(sound_volume, style={'display': 'inline-block'}),
                           ], style={'whiteSpace':'nowrap', 'overflowX': 'none','backgroundColor': 'black','borderWidth':'5px', 'borderColor':'darkgray', 'borderStyle': 'solid'})


    @app.callback(Output('masking-example', 'figure'),
                  [Input('Sound_loudness', 'value'), ],
                  [State('masking-example', 'figure'), ])
    def display_value(value, figure):
        figure['data'][0]['y'][1] = value  # Update spectral peak
        figure['data'][4]['y'][5] = value  # Update stem
        figure['data'][2]['y'] = [0, value * 1.2 - 15, 0]  # Update masking spread
        if value < 30:
            coeff = 13; exp = 1.7
        elif value < 35:
            coeff = 8; exp = 1.6
        elif value < 40:
            coeff = 6; exp = 1.8
        elif value < 50:
            coeff = 4; exp = 2
        elif value < 70:
            coeff = 2; exp = 2.2
        elif value < 120:
            coeff = 1; exp = 2.4
        figure['data'][2]['x'] = [500 - (coeff * value), 1000, 1500 + (value ** exp)]  # Update masking spread
        figure['layout']['transition'] = {'duration': 300}
        if value > 70:
            figure['layout']['yaxis']['range'] = [0, 100]
        else:
            figure['layout']['yaxis']['range'] = [0, 70]

        if value > 53:
            figure['data'][0]['marker']['color'][2] = 0
            figure['data'][0]['text'][2] = 'INAUDIBLE!'
        else:
            figure['data'][0]['marker']['color'] = [2, 2, 2]
            figure['data'][0]['text'][2] = 'sinewave sound 3.5kHz'
        return figure

    return masking_example_layout
