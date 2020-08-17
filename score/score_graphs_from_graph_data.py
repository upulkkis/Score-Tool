from helpers import constants
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import plotly.graph_objs as go
import score_component as sc
import numpy as np
import pretty_midi

def score_graphs_from_graph_data(graph_data):
        notenames = []
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
                      # 'rangeslider': {'visible': True},
                      # 'rangeselector': {'visible': True},
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
            # 'showscale': False,
            # 'coloraxis_showscale': False
        }
        fig_config = {
            'displayModeBar': False,
            'scrollZoom': False,
            # 'modeBarButtons':{'zoom3d':True}
        }

        trace_template = {
            "type": "heatmap",
            "zmin": 0,
            "zmax": 1,
            'showlegend': True,
            'showscale': False,
            # 'opacity': 0.5,
        }
        ##DO GRAPHS
        scale = 2 #calculated 1/scale values, i.e. 2 = 1/2 = 0.5
        score_pianoroll = sc.Pianoroll(id='pianoroll_graph', stave_list=graph_data['stave_list'], bar_offset=graph_data['bar_offset'][0], width=len(graph_data['ticks_for_bar_start'])*200*scale, height=(len(graph_data['instrument'])*70/scale)+100, scale=1/scale, stave_spacing=70)
        score_pianoroll = html.Div(children=score_pianoroll, style={'backgroundColor': '#eed', 'width':(len(graph_data['ticks_for_bar_start'])*200+100)/scale, 'height': (len(graph_data['instrument'])*70/scale)+100})
        score_pianoroll = html.Div(id='pianoroll_container', children=[html.Div('Score with the target at the top. The redness of the target means less audibility', style={'backgroundColor': '#eed', 'color':'black','fontSize': 30, 'textAlign':'center'}),
                                                                       score_pianoroll], style={'backgroundColor': '#eed', 'width':'100%', 'overflowX':'auto'})
        score_pianoroll = html.Div([
            dbc.Button('download score as PNG', id='pianoroll_png', block=True, className='downloadpng', size='sm'),
            score_pianoroll
        ])

        fig_layout['xaxis']['tickmode'] = 'array'
        fig_layout['xaxis']['tickvals'] = graph_data['ticks_for_bar_start']
        fig_layout['xaxis']['ticktext'] = np.arange(len(graph_data['downbeats'][graph_data['bar_offset'][0]:graph_data['bar_offset'][1]])) + \
                                          graph_data['bar_offset'][0] + 1  # Do the math to get the right text

        #Set 3d camera direct above:
        camera = dict(
            eye=dict(x=1*0.5, y=0., z=2.5*0.5)  #Lower coefficient = bigger zoom
        )
        layout3d = {
            'plot_bgcolor': 'black',
            'paper_bgcolor': 'black',
            'font': {
                'color': 'white'
            }, #'width': '1000', 'height': '500',
            'scene': {
                "aspectratio": {"x": 1, "y": 4, "z": 0.5},
                'camera': camera,
            },

        #Layout template for 2d graphs
        }
        layout2d = {
            'height': '300',
            'plot_bgcolor': 'black',
            'paper_bgcolor': 'black',
            'font': {
                'color': 'white'
            },
        }

        tickvals_enhanced = []
        k=1
        for i in range (graph_data['score_length']):
            tickvals_enhanced.append(k)
            if i + 1 in graph_data['ticks_for_bar_start']:
                k+=1

        #Do measure numbering for 2d graphs
        layout2d['xaxis'] = dict()
        layout2d['xaxis']['tickmode'] = 'array'
        layout2d['xaxis']['tickvals'] = graph_data['ticks_for_bar_start']
        layout2d['xaxis']['ticktext'] = np.arange(len(graph_data['downbeats'][graph_data['bar_offset'][0]:graph_data['bar_offset'][1]])) + graph_data['bar_offset'][0] + 1  # Do the math to get the right text

        #Do measure numbering for 3d graph
        layout3d['scene']['yaxis'] = dict()
        layout3d['scene']['yaxis']['title'] = 'Bar number'
        layout3d['scene']['yaxis']['tickmode'] = 'array'
        layout3d['scene']['yaxis']['tickvals'] = np.arange(graph_data['score_length']) #ticks_for_bar_start
        layout3d['scene']['yaxis']['ticktext'] = tickvals_enhanced #np.arange(len(midi_data.get_downbeats()[bar_offset[0]:bar_offset[1]])) + bar_offset[0] + 1  # Do the math to get the right text
        layout3d['scene']['yaxis']['showgrid'] = True
        layout3d['scene']['xaxis'] = dict()
        layout3d['scene']['xaxis']['title'] = 'Critical band'
        layout3d['scene']['xaxis']['tickvals'] = np.arange(107)
        layout3d['scene']['xaxis']['ticktext'] = np.flip(constants.threshold[:, 0])
        layout3d['scene']['xaxis']['title'] = 'Masking threshold in dB'
        #layout3d['scene']['xaxis']['fixedrange'] = True

        zoom_enable = dbc.FormGroup([dbc.Checkbox(checked=False, id='zoom_enable'), dbc.Label(' enable mouse scroll wheel zoom', html_for='zoom_enable')], style={'textAlign':'center'})
        graph3d = dcc.Graph(id='3d_graph',figure = {'data':[go.Surface(z=graph_data['orchestration_masking_curves'], opacity=1,
                                                                        reversescale=True,
                                                                        colorscale= 'Spectral', showscale=False,
                                                                        name='Orchestration',hovertemplate='Bar number: %{y}, Critical band: %{x}, Masking threshold %{z} dB'),
                                           go.Surface(z=graph_data['target_peaks_over_masking'], opacity=1,
                                                      colorscale= 'blugrn', showscale=False,name='Target',
                                                      hovertemplate='Bar number: %{y}, Critical band: %{x}, Excitation %{z} dB')], 'layout': layout3d}, config=fig_config)
        graph3d=html.Div([zoom_enable, graph3d])
        x_axis=np.arange(graph_data['score_length'])

        def set_id(number):
            return {
                'type': 'a_graph',
                'index': number
            }
        layoutA =layout2d.copy()
        layoutA['title'] = 'Target spectral peaks masked, in %'
        masking_threshold_graph = dcc.Graph(id=set_id(1),figure={'data': [go.Scatter(x=x_axis, y=graph_data['target_masking_percent_array'],
                                                                                     fill='tozeroy',name='Target audibility',
                                                                                     line={'color':'olive'},
                                                                                     hovertemplate='%{y} percent of target peaks masked by orchestration')],
                                                                 'layout': layoutA}, config=fig_config)
        masking_threshold_graph = html.Div([html.Div('Click anywhere in the graph to show orchestration at current point', style={'textAlign':'center'}), masking_threshold_graph])

        orchestration_var_coeffs=np.array(graph_data['orchestration_var_coeffs'])
        orchestration_var_coeffs[orchestration_var_coeffs>5]=5 #Delete anomalies in var_coeff
        layoutB=layout2d.copy()
        layoutB['title'] = 'Orchestration variation coefficient (homogenuity of the orchestration)'
        variation_coefficient_graph = dcc.Graph(id=set_id(2), figure={'data': [go.Scatter(x=x_axis, y=orchestration_var_coeffs,
                                                                                          line={'color':'sienna'}, fill='tozeroy',
                                                                                          name='Variation coefficient', hovertemplate='Homogenuity coefficient: %{y}')], 'layout': layoutB}, config=fig_config)
        variation_coefficient_graph = html.Div([html.Div('Click anywhere in the graph to show orchestration at current point', style={'textAlign':'center'}), variation_coefficient_graph])
        layoutC=layout2d.copy()
        layoutC['title'] = 'Orchestration and target centroid comparison'
        centroid_graph = dcc.Graph(id=set_id(3), figure={'data': [go.Scatter(x=x_axis, y=graph_data['orchestration_centroids'], name='Orchestration', hovertemplate='Centroid: %{y}Hz'), go.Scatter(x=x_axis, y=graph_data['target_centroids'], name='Target', hovertemplate='Centroid: %{y}Hz')], 'layout': layoutC}, config=fig_config)
        centroid_graph = html.Div([html.Div(
            'Click anywhere in the graph to show orchestration at current point', style={'textAlign': 'center'}),
            centroid_graph])

        layoutD=layout2d.copy()
        layoutD['title'] = 'Orchestration and target color distance'
        distance_graph = dcc.Graph(id=set_id(4), figure={'data': [go.Scatter(x=x_axis, y=graph_data['mfcc_distance_vector'],
                                                                             fill='tozeroy', line={'color':'moccasin'},
                                                                             name='Color distance', hovertemplate='Target distance from orchestration: %{y}')], 'layout': layoutD}, config=fig_config)
        distance_graph = html.Div([html.Div(
            'Click anywhere in the graph to show orchestration at current point', style={'textAlign': 'center'}),
            distance_graph])

        #masking3d=do3dgraph(midi_data, tgt, orchestration_pianoroll)

        #Disable unnecessary graph for now
        graph = dcc.Graph(id='midi_graph', figure={'data': graph_data['all_traces'],
                                              'layout': fig_layout
                                              }, config=fig_config,)

        analyzed_material = graph_data['analyzed_material']


        return [score_pianoroll, masking_threshold_graph, variation_coefficient_graph, centroid_graph, distance_graph, graph3d, graph,  analyzed_material]