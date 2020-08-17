# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import visdcc
import json
import base64
app = dash.Dash()
app.config['suppress_callback_exceptions'] = True
app.config.suppress_callback_exceptions = True


#Set lists about available menus:
node_list = ['program', 'theory', 'testing', 'about']
about_list = ['about me', 'about project']
program_list = ['chord', 'score']
testing_list = ['field test 1', 'opera']
theory_list = ['matemathics', 'masking', 'blending', 'orchestration']
initial = ['Orchestration Analyzer']
#initial_data = {'nodes':[{'id': initial[0], 'label': initial[0], 'shape': 'box', 'font':{'size':100}}], 'edges':[]}

#List of pages with text in them:
def flatten_list(l): return [item for sublist in l for item in sublist]
text_pages = flatten_list([about_list, testing_list, theory_list])

#Load the logo for main page
image_filename = 'logo.png' # Orchestration Analyzer logo
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#Define function to add menu elements
def add_nodes(label):
    return {'id': label,'label': label, 'shape': 'text', 'font':{'size':50, 'color':'grey', 'face': 'Arial Black'}, 'color':{'background':'black', 'border':'grey'}}
def add_edges(parent, child):
    return {'id': parent + "-" + child, 'from': parent, 'to': child}

#The starting data for menus:
initial_data = {'nodes':[{'id': initial[0], 'label': '', 'shape': 'image', 'size':80,'image':'data:image/png;base64,{}'.format(encoded_image.decode()), 'font':{'size':100}}], 'edges':[]}



#Unusable function, don't have energy to debug:
def not_exist(data, id, nodeid):
    for val in data:
        if val[id] == nodeid:
            return False
        else:
            return True

#Add menuitems and connect them to clicked node:
def append_nodes(data, nodelist, parent):
    #n_list=data['nodes']
    #data['nodes']=[]
    #print(n_list)
    #e_list=data['edges']
    #data['edges']=[]

    #for val in nodelist:
    for i in range(len(nodelist)):
        val = nodelist[i]
        #data['nodes'].append({'id': val, 'label': val})
        data['nodes'].append(add_nodes(val))
        #data['edges'].append({'id': parent + "-" + node_list[i], 'from': parent, 'to': nodelist[i]})
        data['edges'].append(add_edges(val, parent))
    #for i in range(len(nodelist)):
    #    data['edges'].append({'id': parent+"-"+node_list[i], 'from':parent, 'to': nodelist[i]})
    #print(n_list)
    #data['nodes']=n_list
    #data['edges']=e_list
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

    # for nds in data['nodes']:
    #     if nds['id'] == node_id:
    #         idx = data['nodes'].index(nds)
    #         label = data['nodes'][idx]['label']
    #         if label=='about':
    #             data = append_nodes(data, ['jee', 'juu'], node_id)
    #             #data['nodes'].append({'id': 'jee', 'label': 'jee'})
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
    for nod in lista:
        for val in node_data['nodes']:
            if val['id'] == nod:
                new_nodelist.remove(val)
        for val in node_data['edges']:
            if val['to'] == nod:
                new_edgelist.remove(val)
    #print(new_nodelist)
    node_data['nodes'] =[]
    node_data['edges'] =[]
    node_data['nodes']=new_nodelist
    node_data['edges']=new_edgelist
    #print(node_data)
    # for nds in data['nodes']:
    #     if nds['id'] == node_id:
    #         idx = data['nodes'].index(nds)
    #         label = data['nodes'][idx]['label']
    #         if label=='about':
    #             data = append_nodes(data, ['jee', 'juu'], node_id)
    #             #data['nodes'].append({'id': 'jee', 'label': 'jee'})
    return node_data

def text_on_click(node_id):
    text=html.Div('Sorry, not yet implemented')
    if node_id=='about me':
        text = about_text.aboutText()

    text = html.Div(children=[html.Div(text, style={'height': '100vh'})], className='fadein')
    return text


####################
#Main menu callback#
####################
import about_text
@app.callback(
    [Output('testing', 'children'), #The main container for content
    Output('net', 'data'), #Menu items data
     Output('nodestore', 'children'),  #Hidden place to store data
     Output('net', 'style'), #To show/hide menuitems
     Output('back', 'style'),
     Output('net', 'focus'), #To focus a node, not really working :(
     Output('chord', 'style'), #To show/hide program
     Output('score', 'style'),
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

    #Launch back button and set it to none
    if back_button >0 and nodestore['back']: #Back button to switch views
        nodestore['back'] = False
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
            back = {'display': 'block', 'color':'#404040'}
            intro = text
            return [text, data, json.dumps(nodestore), hideshow, back, focus, chord, score]
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


# @app.callback(
#     Output('net', 'options'),
#     [Input('color', 'value')])
# def myfun(x):
#     return {'nodes':{'color': x}}

### The main layout:
app.layout = html.Div(children=[
    html.Div(id='nodestore', children=json.dumps({initial[0]: True}), style={'display': 'none'}),
      #visdcc.Network(id = 'back', options = dict(height= '50px', width= '100%'), data={'nodes':[add_nodes('Back to the menu')], 'edges':[]}, style={'display': 'none'}),
      html.Button(id='back', n_clicks=0, children='..-- T A K E  M E  B A C K --..', className='button',style={'display': 'none'}),
      html.Div(id='chord', style={'display': 'none'}),
      html.Div(id='score', style={'display': 'none'}),
      html.Div(id='testing'),
    #html.Div(children=[
      visdcc.Network(id = 'net',
                     options = dict(minHeight='900px', animation=True,height= '900px', width= '100%', clickToUse=False, physics={'solver':'repulsion', 'repulsion':{'nodeDistance': 150}}), data=initial_data)#data=append_nodes(data, node_list, initial[0])),
    #],style={'height':'100%'}),
    # dcc.Input(id = 'label',
      #           placeholder = 'Enter a label ...',
      #           type = 'text',
      #           value = ''  ),
      # html.Br(),html.Br(),
      # dcc.RadioItems(id = 'color',
      #                options=[{'label': 'Red'  , 'value': '#ff0000'},
      #                         {'label': 'Green', 'value': '#00ff00'},
      #                         {'label': 'Blue' , 'value': '#0000ff'} ],
      #                value='Red'  ),
], )#, style={'height': '100%'})#, style={height= '100%', width= '100%'})   ###style={'backgroundImage': 'data:image/png;base64,{}'.format(encoded_image2.decode())}

if __name__ == '__main__':
    app.run_server(debug=True)