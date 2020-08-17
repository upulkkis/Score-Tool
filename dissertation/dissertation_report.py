import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import visdcc
import json

def dissertation(app):

    #Set lists about available menus:
    node_list = ['theory', 'testing', 'about']
    about_list = ['about me', 'about project']
    program_list = ['chord', 'score']
    testing_list = ['field test 1', 'opera']
    math_list = ['fourier', 'mfcc', 'critical band', 'spreading function']
    theory_list = ['mathematics', 'masking', 'blending', 'orchestration']
    initial = ['Orchestration Analyzer']

    theory_list_without_math = theory_list.copy()
    theory_list_without_math.remove('mathematics') #Pop out math from theory list, because it has subnodes
    #initial_data = {'nodes':[{'id': initial[0], 'label': initial[0], 'shape': 'box', 'font':{'size':100}}], 'edges':[]}

    #List of pages with text in them:
    def flatten_list(l): return [item for sublist in l for item in sublist]
    text_pages = flatten_list([about_list, testing_list, theory_list_without_math])

    #Define function to add menu elements
    def add_nodes(label):
        return {'id': label,'label': label, 'shape': 'text', 'font':{'size':20, 'color':'grey', 'face': 'Arial Black'}, 'color':{'background':'black', 'border':'grey'},}
    def add_edges(parent, child):
        return {'id': parent + "-" + child, 'from': parent, 'to': child}

    #The starting data for menus:
    initial_data = {'nodes':[{'id': initial[0], 'label': 'Click here', 'shape': 'text', 'font':{'size':24, 'color':'grey', 'face': 'Arial Black'}}], 'edges':[]}

    #Unusable function, don't have energy to debug:
    def not_exist(data, id, nodeid):
        for val in data:
            if val[id] == nodeid:
                return False
            else:
                return True

    #Add menuitems and connect them to clicked node:
    def append_nodes(data, nodelist, parent):
        for i in range(len(nodelist)):
            val = nodelist[i]
            data['nodes'].append(add_nodes(val))
            data['edges'].append(add_edges(val, parent))
        return data

    #When items are clicked, this is the function
    def act_on_click(data, node_id):
        text=''
        if node_id=='about':
            data=append_nodes(data, about_list, node_id)
        if node_id==initial[0]:
            data = append_nodes(data, node_list, node_id)
        if node_id=='program':
            data = append_nodes(data, program_list, node_id)
        if node_id=='testing':
            data = append_nodes(data, testing_list, node_id)
        if node_id == 'theory':
            data = append_nodes(data, theory_list, node_id)
        if node_id == 'mathematics':
            data = append_nodes(data, math_list, node_id)
        return data, text

    #This function strips the nodes if node is clicked again
    def strip_on_click(node_data, node_id):
        new_nodelist=node_data['nodes'].copy()
        new_edgelist=node_data['edges'].copy()
        if node_id=='about': lista=about_list
        if node_id=='testing': lista=testing_list
        if node_id==initial[0]: return initial_data# If logo is clicked, back to squeare one :)
        if node_id=='program':lista=program_list
        if node_id == 'theory': lista=theory_list
        if node_id == 'mathematics': lista=math_list
        for nod in lista:
            for val in node_data['nodes']:
                if val['id'] == nod:
                    new_nodelist.remove(val)
            for val in node_data['edges']:
                if val['to'] == nod:
                    new_edgelist.remove(val)

        node_data['nodes'] =[]
        node_data['edges'] =[]
        node_data['nodes']=new_nodelist
        node_data['edges']=new_edgelist

        return node_data

    import dissertation.about_text
    import dissertation.field_test_text
    import dissertation.masking_text
    import dissertation.history_of_orchestration
    def text_on_click(node_id):
        text=html.Div('Sorry, not yet implemented')
        if node_id=='about me':
            text = dissertation.about_text.aboutText()
        if node_id=='field test 1':
            text = dissertation.field_test_text.field_test_text()
        if node_id=='masking':
            text = dissertation.masking_text.masking_text()
        if node_id=='orchestration':
            text = dissertation.history_of_orchestration.history_text()

        text = dbc.Modal([
            dbc.ModalBody(html.Div(children=[html.Div(text, style={'height': '100vh'})], className='fadein'))
        ], scrollable=True, is_open=True, autoFocus=True, size='xl')
        return text


    ##############################
    # Disseration menu callbacks #
    ##############################

    @app.callback(
        [Output('testing', 'children'), #The main container for content
        Output('net', 'data'), #Menu items data
         Output('nodestore', 'children'),  #Hidden place to store data
         Output('hidden4', 'style'), #To show/hide menuitems
         Output('back', 'style'),
         Output('net', 'focus'), #To focus a node, not really working :(
         Output('hidden2', 'style'), #To show/hide program
         Output('hidden3', 'style'),
         ],
        [Input('net', 'selection'), #Selected nodes
         Input('back', 'n_clicks')], #Backbutton
         [State('net', 'data'),
          State('nodestore', 'children'),
          ])
    def node_function(sel, back_button, data, nodestore):
        chord={'display': 'none'}
        score={'display': 'none'}
        nodestore=json.loads(nodestore) #Load things from data store
        hideshow = {'display': 'block'}
        back = {'display': 'none'}
        focus=True;
        # Intro when page loads:
        intro = html.Div([html.Div('Orchestration Analyzer', className='fadein',
                                   style={'fontSize': 80, 'fontFace': 'Arial', 'color': 'grey', 'textAlign': 'center'}),
                          html.Div('Artificial intelligence in orchestration by Uljas Pulkkis', className='fadein',
                                   style={'fontSize': 20, 'fontFace': 'Arial', 'color': 'grey', 'textAlign': 'center',
                                          'margin': '0px'})], style={'marginBottom': -120})
        intro=''
        #Launch back button and set it to none

        if back_button >0 and nodestore['back']: #Back button to switch views
            nodestore['back'] = False
            score = chord = {'display': 'none'}
            chord = chord = {'display': 'none'}
            return [intro, data, json.dumps(nodestore), {'display': 'block'}, {'display': 'none'}, focus, chord, score]
        nodestore['back'] = False

        #data = dict()
        #data, fit, focus, id, moveTo, options, selection, style
        if sel!=None and 'nodes' in sel:  #If clicked for the first time
            if sel['nodes']==[]: #If empty screen is clicked
                return [intro, data, json.dumps(nodestore), hideshow, back, focus, chord, score]
            node_id = sel['nodes'][0]
            focus=node_id #Set focus on clicked node
            if node_id in text_pages:#node_id == 'about me': #About me text will be shown
                text=text_on_click(node_id)
                nodestore['back']=True
                hideshow={'display': 'none'}
                back = {'display': 'none', 'color':'#404040'}
                intro = text
                return [text, data, json.dumps(nodestore), hideshow, back, focus, chord, score]
            if node_id in program_list:
                nodestore['back'] = True
                if node_id=='chord':
                    hideshow = {'display': 'none'}
                    back = {'display': 'none', 'color': '#404040'}
                    score = chord = {'display': 'none'}
                    chord = chord={'display': 'block'}
                if node_id=='score':
                    hideshow = {'display': 'none'}
                    back = {'display': 'none', 'color': '#404040'}
                    score = chord = {'display': 'block'}
                    chord = chord={'display': 'none'}
                return ['', data, json.dumps(nodestore), hideshow, back, focus, chord, score]
            elif not node_id in nodestore: #If node is never clicked
                nodestore[node_id]=True
            if nodestore[node_id]: #If certain node is selected
                # data['nodes'][0] ={'id': initial[0], 'label': '', 'shape': 'image', 'size': 100,
                #             'image': 'data:image/png;base64,{}'.format(encoded_image.decode()), 'font': {'size': 100}}
                data, msg = act_on_click(data, node_id)
                nodestore[node_id]=False
                intro = ''
                #return [msg, data, json.dumps(nodestore), hideshow, back]
            elif not nodestore[node_id]: #If node is clicked for the second time
                data = strip_on_click(data, node_id)
                nodestore[node_id] = True
                intro = ''
                #return ['', data, json.dumps(nodestore), hideshow, back]

            #node_index=data['nodes'].index({'id': node_number})
                #return json.dumps(data['nodes'][node_index]) #[sel['nodes']] ##[sel['nodes'][0]]

        #When program starts, this is returned:
        return [intro, data, json.dumps(nodestore), hideshow, back, focus, chord, score]


    net_nodes = html.Div([html.Div(id='nodestore', children=json.dumps({initial[0]: True}), style={'display': 'none'}),
                            html.Button(id='back', n_clicks=0, children='BACK TO MASKING SKULL', className='button',style={'display': 'none'}),
                           html.Div(id='testing'),
                           html .Div(id='nethide', children=visdcc.Network(id='net',
                                          options=dict(minHeight='900px', animation=True, height='900px', width='100%',
                                                       clickToUse=False,
                                                       physics={'solver': 'repulsion', 'repulsion': {'nodeDistance': 150}}),
                                          data=initial_data),  # data=append_nodes(data, node_list, initial[0])),
                                     style={'width': '100vw', 'display': 'block'}),
                           html.Div(id='diss-hidden-container', style={'display': 'none'}),
                           html.Div(id='hidden2', style={'display': 'none'}),
                           html.Div(id='hidden3', style={'display': 'none'}),
                           html.Div(id='hidden4', style={'display': 'none'}),
                           ])
    return net_nodes


