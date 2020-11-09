import dash
import math
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

def hall_test(app):
    scale=80
    stage_width=20
    stage_length=7
    stage_padding=2.5
    hall_width=25
    hall_length=30

    parent = [{
        'data': {'id':'orch', 'label': 'stage'},
        #'locked': True,
    }]

    hall = [{
        'data': {'id':'hall', 'label': 'hall'},
        'classes': 'hall',
        'locked': True
    }]

    stylesheet = [
     {
         'selector': 'node',
         'style': {
            'content': 'data(label)',
             'shape': 'rectangle',
             'font-size':40,
            "width": "mapData(size, 0, 100, 20, 60)",
            "height": "mapData(size, 0, 100, 20, 60)",
         }
     },
        {
            'selector': 'edge',
            'style':{
                'content': 'data(label)',
            'font-size':40,
            }
        },
        {
            'selector': '.dist',
            'style':{
                'line-style': 'dashed',
                'opacity': 0.5
            }
        },
        {
        'selector': '.hidden',
        'style': {
        'opacity': 0,
        }
        },
            {
                'selector': '.hall',
                'style': {
                    'background-color': 'lightGray',
                    'opacity':0.3,
                    'z-index':-100
                }
            },
        {
            'selector': '.you',
            'style': {
                'font-size': 80,
                'color': 'lightGray',
            }
        },
    ]

    stage = [
        {
            'data': {'id': short, 'label': label, 'parent': 'orch'},
            'position': {'x': x*scale, 'y': y*scale},
            'classes': 'hidden'
        }
        for short, label, x, y in (
            ('left', '', stage_padding, stage_length+stage_padding),
            ('right', '', stage_width+stage_padding, stage_length+stage_padding),
            ('right_b', '', stage_width+stage_padding, stage_padding),
            ('left_b', '', stage_padding, stage_padding),
        )
    ]

    hall_markers = [
        {
            'data': {'id': short, 'label': label, 'parent':'hall'},
            'position': {'x': x*scale, 'y': y*scale},
            'classes': 'hidden'
        }
        for short, label, x, y in (
            ('left1', '', 0, hall_length),
            ('right1', '', hall_width, hall_length),
            ('right_b1', '', hall_width, 0),
            ('left_b1', '', 0, 0),
        )
    ]

    instruments = [
        {
            'data': {'id': short, 'label': label, 'parent': 'orch'},
            'position': {'x': (x+stage_padding)*scale, 'y': (y+stage_padding)*scale},
        }
        for short, label, x, y in (
            ('vln1', 'Violin I', 9, 6),
            ('vln2', 'Violin II', 9, 5),
            ('vla', 'Viola', 11, 5),
            ('vcl', 'Cello', 11, 6),
            ('db', 'Double Bass', 18.5, 5),
            ('fl', 'Flute', 8, 4),
            ('ob', 'Oboe', 12, 4),
            ('cl', 'Clarinet', 8, 3),
            ('bsn', 'Bassoon', 12, 3),
            ('horn', 'Horn', 5, 2),
            ('tr', 'Trumpet', 10, 1),
            ('trmb', 'Trombone', 15, 2),
            ('tuba', 'Tuba', 16.5, 3),
            ('timp', 'Timpani', 2, 1),
            ('harp', 'Harp', 1, 5),
            ('solo1', 'Soloist 1', 9, 8),
            ('solo2', 'Soloist 2', 11, 8),
            ('vln1b', '', 2, 6),
            ('vln2b', '', 3.5, 3.5),
            ('vlab', '', 14.5, 3.5),
            ('cellob', '', 17, 6),
        )
    ]
    conductor = [
        {'data': {'id':'cond', 'label':'conductor', 'parent': 'orch', 'size':70},
         'position':{'x':(10+stage_padding)*scale, 'y':(7+stage_padding)*scale},
         'grabbable': False,
         }
    ]

    you = [
        {'data': {'id':'you', 'label':'you', 'size':200},
         'position':{'x':(10+stage_padding)*scale, 'y':(18+stage_padding)*scale},
         'classes':'you',
         }
    ]

    edges = [
        {'data': {'source': source, 'target': target, 'label': label}, 'classes':'dist'}
        for source, target, label in (
            ('you', 'cond', 'distance'),
            ('vln1', 'vln1b', 'section'),
            ('vln2', 'vln2b', 'section'),
            ('vla', 'vlab', 'section'),
            ('vcl', 'cellob', 'section'),
        )
    ]

    elements =  you+conductor+ instruments +hall+hall_markers+parent+stage +edges# + edges


    lay = html.Div([
        cyto.Cytoscape(
            id='cytoscape-update-layout',
            layout={'name': 'preset'},
            style={'width': '800px', 'height': '800px', 'display': 'inline-block', 'padding':0},
            stylesheet=stylesheet,
            elements=elements,
        userZoomingEnabled = False,
            #zoomingEnabled= False,
            #responsive=True,
    #autoRefreshLayout =True,
        ),
        html.Div(id='upd', style={'display': 'inline-block'})
    ], style={'height':'1000px'})

    def distance (x1, y1, x2, y2):
        return math.sqrt((x1-x2)**2+(y1-y2)**2)

    import json
    # @app.callback(Output('cytoscape-update-layout', 'layout'),
    #               [Input('dropdown-update-layout', 'value')])
    # def update_layout(layout):
    #     return {
    #         'name': layout,
    #         'animate': True
    #     }
    @app.callback(Output('upd', 'children'),
                  [
                      Input('cytoscape-update-layout', 'mouseoverNodeData')
                      #Input('cytoscape-update-layout', 'tapNode')
                   ],
                  [State('cytoscape-update-layout', 'elements')])
    def upd(tap, ly):
        you_pos = [ly[0]['position']['x'], ly[0]['position']['y']]
        dist = distance(you_pos[0], you_pos[1], ly[1]['position']['x'], ly[1]['position']['y'])
        dist = round(dist/scale, 1)
        inst_atten=[]
        for i in range(2, len(instruments)-4+2):
            inst = ly[i]['data']['label']
            v_dist = distance(you_pos[0], you_pos[1], ly[i]['position']['x'], ly[i]['position']['y'])
            v_dist = v_dist / scale
            if v_dist < 2:
                deb = 0
            else:
                deb = round(0 - (20 * math.log10(v_dist - 1)), 1)
            inst_atten.append([inst, deb])
        your_distance = 'You are listening at ' + str(dist)+'m from conductor'+'\n'
        attenuations = [str(ins)+': '+str(db)+' dB'+ '\n' for ins, db in inst_atten]
        layout={'title':'Instrument attenuations at '+str(dist)+'m from the conductor',
                'yaxis':{'title':'decibels of attenuation'},
                'plot_bgcolor': 'black',
                'paper_bgcolor': 'black',
                'font': {
                    'color': 'lightGray'
                },
                }
        graph = dcc.Graph(style={'width':'800px'}, id='attenuations', config={'displaylogo':False, 'displayModeBar': False }, figure={'layout':layout, 'data':[{'x':[x for x,y in inst_atten], 'y':[-y for x,y in inst_atten], 'type':'bar', 'marker':{'color':'sienna'}}]})
        return [graph, html.Pre(your_distance + 'Instrument attenuations: \n'+''.join(attenuations)),]#json.dumps(ly[1])]
    return lay

app.layout = hall_test(app)

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', debug=True)