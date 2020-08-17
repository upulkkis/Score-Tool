import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_admin_components as dac
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from helpers import constants, hertz_to_microtone


def compare(app, orchestra):
    import score_component as sc
    from compare import test_instrument_input

    start_box= dac.Box(
            [dac.BoxHeader(title='Compare the properties of two instrument sounds'),
             dac.BoxBody([
               dbc.Row([
                dbc.Col(test_instrument_input. new_instrument_input(app, orchestra, 'one', False), width=6, style={'borderRight':'6px solid grey'}),
                dbc.Col(test_instrument_input. new_instrument_input(app, orchestra, 'two', False), width=6)
               ]),
        dbc.Button(id='compare_button', n_clicks=0, children='Click to compare', block=True, style={'marginTop':20}),
               ])
             ],
        width=12)

    result_box=dac.Box([dac.BoxHeader(title='Comparison'),
                         dac.BoxBody(html.Div(id='compare'))],width=12, )

    def compare_maskings(data, mfcc, peaks, i1, i2):
        fig_config = {
            'displayModeBar': False
        }
        fig_layout = {
            #'width': '29%',
            'plot_bgcolor': 'black',
            'paper_bgcolor': 'black',
            'font': {
                'color': 'white'
            },
            'xaxis': {'title': ''},
            "title": "Mfcc vectors",
            'yaxis': {'title': 'mfcc values'},
        }

        layout2d = {
            #'width': '70%',
            #'height': '400',
            'plot_bgcolor': 'black',
            'paper_bgcolor': 'black',
            'font': {
                'color': 'white'
            },
            "title": "Spectral features",
            'xaxis': {'title': 'Frequency in Hz', 'type': 'log'},
            'yaxis': {'title': 'dB (SPL)', 'showgrid': False, 'zeroline': False},
        }
        mfcc_vector1_trace = {
            "mode": "lines",
            "type": "scatter",
            "y": mfcc[0][1:],
            "name": "mfcc vector of {}".format(i1),
            "line": {'color': 'yellow'},
        }
        mfcc_vector2_trace = {
            "mode": "lines",
            "type": "scatter",
            "y": mfcc[1][1:],
            "name": "mfcc vector of {}".format(i2),
            "line": {'color': 'purple'},
        }
        trace1 = {
            "mode": "markers",
            "type": "scatter",
            "x": peaks[0][0],
            "y": peaks[0][1],
            "name": "{} peaks".format(i1),
            "marker": {'symbol': 'x', 'size': 12, 'color': 'green'}, #'colorscale': colorscale, 'line': {'width': 0}},
        }
        trace2 = {
            "mode": "markers",
            "type": "scatter",
            "x": peaks[1][0],
            "y": peaks[1][1],
            "name": "{} peaks".format(i2),
            "marker": {'symbol': 'o', 'size': 12, 'color': 'olive'},  # 'colorscale': colorscale, 'line': {'width': 0}},
        }
        x_axis= constants.threshold[:, 0]
        gra = dcc.Graph(figure={'data': [
            go.Scatter(x=x_axis, mode='lines', y=data[0], name='{} curve'.format(i1), line={'color':'sienna'},
                       #hovertemplate='%{y} percent of target peaks masked by orchestration',
                       fill='tozeroy',),
                       #fillcolor='sienna'),
            go.Scatter(x=x_axis, mode='lines', y=data[1], name='{} curve'.format(i2), line={'color': 'moccasin'},
                       # hovertemplate='%{y} percent of target peaks masked by orchestration',
                       fill='tozeroy',),
                       #fillcolor='moccasin'),
            trace1, trace2], 'layout': layout2d}, config=fig_config,)  # , config=fig_config)
        #gra =html.Div(['Peaks and masking graph comparison', gra], )
        mfcc_fig = go.Figure(data=[mfcc_vector1_trace, mfcc_vector2_trace], layout=fig_layout)
        mfcc_fig = dcc.Graph(figure=mfcc_fig, config=fig_config)
        return [gra, mfcc_fig]
    def truncate(peaks, partials):
        new_peaks=[[],[]]
        if len(peaks[0])>partials:
            new_peaks[0]=peaks[0][:partials]
            new_peaks[1] = peaks[1][:partials]
            return new_peaks
        return peaks
    @app.callback(
        [Output("compare", "children"),
         ],
        [Input("compare_button", "n_clicks"),
         ],
        [State("instrument-input{}".format('one'), 'value'),
    State("dynamics-input{}".format('one'), 'value'),
    State("techs-input{}".format('one'), 'value'),
    State("notes-input{}".format('one'), 'value'),
    State("instrument-input{}".format('two'), 'value'),
    State("dynamics-input{}".format('two'), 'value'),
    State("techs-input{}".format('two'), 'value'),
    State("notes-input{}".format('two'), 'value'),
         ])
    def do_comparison(n, i1, d1, t1, n1, i2, d2, t2, n2):
        if n>0:
            #try:
                i1_peaks = orchestra[i1][t1][d1][n1]['peaks']
                i1_masks = orchestra[i1][t1][d1][n1]['masking_curve']
                i1_mfcc = orchestra[i1][t1][d1][n1]['mfcc']
                i1_cent = orchestra[i1][t1][d1][n1]['centroid']

                i2_peaks = orchestra[i2][t2][d2][n2]['peaks']
                i2_masks = orchestra[i2][t2][d2][n2]['masking_curve']
                i2_mfcc = orchestra[i2][t2][d2][n2]['mfcc']
                i2_cent = orchestra[i2][t2][d2][n2]['centroid']

                i1_p = truncate(i1_peaks, 20)
                i2_p = truncate(i2_peaks, 20)

                i1_notes = [hertz_to_microtone.convert(val) for val in i1_p[0]]
                i2_notes = [hertz_to_microtone.convert(val) for val in i2_p[0]]

                i1_cent = hertz_to_microtone.convert(i1_cent)
                i2_cent = hertz_to_microtone.convert(i2_cent)

                #Find the loudest partial in each peak list
                loudest={'one_db':0, 'one_idx':0, 'two_db':0, 'two_idx':0}
                for i in range(len(i1_p[1])):
                    if i1_p[1][i]>loudest['one_db']:
                        loudest['one_db']=i1_p[1][i]
                        loudest['one_idx'] = i
                for i in range(len(i2_p[1])):
                    if i2_p[1][i]>loudest['two_db']:
                        loudest['two_db'] = i2_p[1][i]
                        loudest['two_idx'] = i

                #Make the db-readings look comparable
                # for i in range(len(i1_p[1])):
                #     print(i1_p[1][i])
                #     i1_p[1][i] = int(i1_p[1][i]-loudest['one_db'])
                # for i in range(len(i2_p[1])):
                #     i2_p[1][i] = int(i2_p[1][i] - loudest['two_db'])

                i1_ann = [str(int(i-loudest['one_db'])) + " db" for i in i1_p[1]]
                i2_ann = [str(int(i-loudest['two_db'])) + " db" for i in i2_p[1]]
                i1_ann[loudest['one_idx']] = 'loudest'
                i2_ann[loudest['two_idx']] = 'loudest'

                i1_score = html.Div([html.Div('Overtones of {}, loudest partial = red'.format(i1), style={'color':'black', 'height':20}),
                    sc.Orchestration(notes=i1_notes, instruments=i1_ann, target=[loudest['one_idx']], width=200)], style={'backgroundColor':'#eed',
                                                                                                        'display':'inline-block'})
                i2_score = html.Div([html.Div('Overtones of {}, loudest partial = red'.format(i2), style={'color':'black', 'height':20}),
                    sc.Orchestration(notes=i2_notes, instruments=i2_ann, target=[loudest['two_idx']], width=200)], style={'backgroundColor':'#eed',
                                                                                                        'display': 'inline-block'})
                score_centroids = html.Div([html.Div('Spectral centroids of {} and {}'.format(i1, i2), style={'color':'black', 'height':20}),
                    sc.Orchestration(notes=[i1_cent, i2_cent], instruments=[i1, i2], target=[], width=100)], style={'backgroundColor':'#eed',
                                                                                                        'display': 'inline-block'})
                mgraph = compare_maskings([i1_masks, i2_masks], [i1_mfcc, i2_mfcc], [i1_peaks, i2_peaks], i1, i2)
                row=dbc.Row([dbc.Col(i1_score, width=3), dbc.Col(i2_score, width=3), dbc.Col(score_centroids, width=2), dbc.Col(mgraph[1], width=4)])
                #i2_mgraph = compare_maskings(i2_masks, i2_mfcc, i2_peaks, 'instrument 2')
            #except:
            #    i1_score = 'Check notes, dynamics or techniques'
                #i2_score = 'Check notes, dynamics or techniques'
            #    print('out of range')

                return [html.Div([row, mgraph[0]])]
        return ['']
    return html.Div([start_box, result_box])
