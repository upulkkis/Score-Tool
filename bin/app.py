## Orchestration Analyzer by Uljas Pulkkis 2020

## Wether to use production server or not
Production = False

if Production:
	import os
	from random import randint
	import flask

import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_admin_components as dac
from dash.exceptions import PreventUpdate
import visdcc
import base64
from help import get_help
import pickle

with open('./database/no_data_orchestra.pickle', 'rb') as handle:
    orchestra = pickle.load(handle)

if Production:
	server = flask.Flask(__name__)
	server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
	app = dash.Dash(__name__, server=server)
else:
	app = dash.Dash(__name__)
	server = app.server


##LOAD IMAGES
image_filename = './bin/assets/score.jpg'  # Test score png
score_image = base64.b64encode(open(image_filename, 'rb').read())
image_filename = './bin/assets/logo.png'  # Orchestration Analyzer logo
logo_image = base64.b64encode(open(image_filename, 'rb').read())

## Create Navbar right hand menu

right_ui = dac.NavbarDropdown(
	menu_icon='question-circle',
	header_text="Help",
	footer_text='',
    children= [
		dbc.DropdownMenuItem(
			id='start_help',
			children=" Getting started",
		),
		dbc.DropdownMenuItem(
			id='chord_help',
			children = " Chord",
		),
		dbc.DropdownMenuItem(
			id='score_help',
			children = " Score",
		),
		dbc.DropdownMenuItem(
			id='compare_help',
			children=" Compare",
		),
	],
	className='whiteText',
)

## Create the Navbar

navbar = dac.Navbar(id='navbar',color = '#afaf88',
                    text='\xa0 \xa0 \xa0 \xa0 \xa0 \xa0 Orchestration Analyzer - an artificial intelligence in music orchestration',
                    skin='light',
                    fixed= True,
                    sidebar_icon='bars',
                    controlbar_icon = 'clipboard',
					border=False,
                    children=[html.Div('© Uljas Pulkkis 2020'), right_ui],
					)

## Create Sidebar menus

sidebar = dac.Sidebar(
	dac.SidebarMenu(
		[
			dac.SidebarHeader(children="Apps", style={'color': 'black'}),
			dac.SidebarMenuItem(id= 'Int_APP', label='Tutorial', icon='mouse-pointer', children='', style={'color': '#eed'}),
			dac.SidebarMenuItem(id='Chord_APP', label='Chord', icon='edit', style={'color': '#eed'}),
            dac.SidebarMenuItem(id='Score_APP', label='Score', icon='music', style={'color': '#eed'}),
            dac.SidebarMenuItem(id='Comp_APP', label='Compare', icon='chart-bar', style={'color': '#eed'}),
			dac.SidebarHeader(children="AI", style={'color': 'black'}),
			dac.SidebarMenuItem(id='Search_AI', label='Search', icon='microchip', style={'color': '#eed'}),
			dac.SidebarMenuItem(id='Match_AI', label='Match', icon='server', style={'color': '#eed'}),
			dac.SidebarHeader(children="Dissertation", style={'color': 'black'}),
			dac.SidebarMenuItem(id='Diss_APP', label='Orchestration', icon='list', children='', style={'color': '#eed'}),
		]
	),
    title='Analyzer App',
	skin="light",
    color="black",
	brand_color="#afaf88",
    url=None,
    src='data:image/png;base64,{}'.format(logo_image.decode()),
	style={'color': 'black'},

)

## Control bar is for help files

controlbar = dac.Controlbar(
	[
		html.Br(),
		html.P("Instrumentation here"),
	],
	id = 'control_bar',
	title = "Edit orchestration",
	skin = "dark",
	style = {'color': 'white', 'backgroundColor':'#eed', 'position': 'fixed', 'overflow':'scroll'}
)

from chord import chord_testing

instument_box, chord_analyze_box = chord_testing.chord_testing(app, orchestra)
chord_page = dac.Page([html.Br(),
	dbc.Fade([instument_box, chord_analyze_box], id='chord', is_in=False,
			 )
])

from tutorial import masking_example

interactive_page = dbc.Row([
	dbc.Fade(children=[
		html.Br(),
		dac.SimpleBox(title='Try it for yourself', children=['Move the slider to increase volume on middle sinewave and see one of the adjacent sounds get masked',
															 masking_example.masking_example_slide(app)], width=12), #style={'width':'800px'}),
			  ], id='masking_example', is_in=False,
			 )
], justify='center')

import dissertation.dissertation_report
dissertation_page = dbc.Fade(children=[html.Br(),
	dac.Box([
		dac.BoxHeader(title='Uljas Pulkkis´s dissertation', collapsible=False),
		dac.BoxBody([dissertation.dissertation_report.dissertation(app)])
	], width=12)
], id='dissertation', is_in=False,
			 )

from score import score_testing

score_page=dbc.Fade(score_testing.score(app, orchestra), id='score_main', is_in=False, )

import compare.compare
compare_page=dbc.Fade(compare.compare.compare(app, orchestra), id='compare_main', is_in=False,)

@app.callback([
	Output('chord', 'is_in'),
	Output('chord', 'style'),
	Output('masking_example', 'is_in'),
	Output('masking_example', 'style'),
	Output('dissertation', 'is_in'),
	Output('dissertation', 'style'),
	Output('score_main', 'is_in'),
	Output('score_main', 'style'),
	Output('compare_main', 'is_in'),
	Output('compare_main', 'style'),
	],
	[Input('Chord_APP', 'n_clicks'),
	 Input('Score_APP', 'n_clicks'),
	Input('Int_APP', 'n_clicks'),
Input('Diss_APP', 'n_clicks'),
Input('Comp_APP', 'n_clicks'),
	 ],
)
def set_content(chord_c, score_c, Inter_c, diss_c, comp_c):
	fd = {'display':'none'}
	f = False
	td = {'display':'block'}
	t=True
	ctx = dash.callback_context  # Callback context to recognize which input has been triggered
	if not ctx.triggered:
		raise PreventUpdate
	else:
		input_id = ctx.triggered[0]['prop_id'].split('.')[0]
	#print(input_id)
	if input_id == 'Chord_APP':
		return [t, td, f, fd, f, fd, f, fd, f, fd]
	if input_id == 'Score_APP':
		return [f, fd, f, fd, f, fd, t, td, f, fd]
	if input_id == 'Int_APP':
		return [f, fd, t, td, f, fd, f, fd, f, fd]
	if input_id == 'Diss_APP':
		return [f, fd, f, fd, t, td, f, fd, f, fd]
	if input_id == 'Comp_APP':
		return [f, fd, f, fd, f, fd, f, fd, t, td]
	return [f, fd, f, fd, f, fd, f, fd]

help_toast = dbc.Toast("Help content here",
                id="help_toast",
                header="Help",
                is_open=False,
                dismissable=True,
                icon="success",
                # top: 66 positions the toast below the navbar
                style={"position": "fixed", "top": 66, "right": 50, "width": 350,},
				body_style=	{'color':'black',
					   'backgroundColor':'secondary',
					   },
				header_style={'backgroundColor':'secondary',
							  'color':'green',
							  }
            ),

start_toast = dbc.Toast([html.H3("First visit?"), html.Br(), html.H5('Click'), dac.Icon(icon='question-circle', size='2x'), html.H5('on top right corner and select:'), dbc.DropdownMenuItem(children=" Getting started", style={'backgroundColor':'#343a40'})
						 ],
						header="Welcome to Orchestration Analyzer!",
					style={"position": "fixed", "top": 66, "right": 50, "width": 350, 'backgroundColor':'#bbe'},
body_style=	{'color':'black'},
						dismissable=True,
						is_open=False,
						icon='danger',
						duration=5000,
						id='start_toast',)

tip_toast = dbc.Toast([html.Br(), html.H5('Click'), dac.Icon(icon='bars', size='2x'), html.H5('to minimize the menu and get room for your analysis!')],
style={"position": "fixed", "top": 66, "left": 250, "width": 350, 'backgroundColor': '#bbe'},
header="Tip!",
dismissable=True,
body_style=	{'color':'black'},
						is_open=False,
						icon='danger',
						duration=5000,
						id='tip_toast',)

@app.callback([Output('help_toast', 'is_open'),
				Output('help_toast', 'children'),],
			  [
				  Input('start_help', 'n_clicks'),]
			  )
def open_help(start):
	#print(start)
	ctx = dash.callback_context  # Callback context to recognize which input has been triggered
	if not ctx.triggered:
		raise PreventUpdate
	else:
		input_id = ctx.triggered[0]['prop_id'].split('.')[0]
	if input_id == 'start_help':
		return [True, get_help.help('general')]
	return [False, '']

import time
@app.callback([Output('start_toast', 'is_open'),
			  Output('javascript', 'run')],
			  [Input('navbar', 'loading_state')])
def open_first(is_loading):
	time.sleep(3)
	#visdcc.Run_js(run='''document.getElementById('nav-item').click()''')
	js = '''
	var doc = document.querySelectorAll("a[data-widget='pushmenu']")[0].click(); 
	'''
	return [False, js]

@app.callback(Output('tip_toast', 'is_open'),
			  [Input('navbar', 'loading_state')])
def open_tip(is_loading):
	#time.sleep(10)
	return False



body = dac.Body([
				 chord_page,
				 interactive_page,
				dissertation_page,
				 score_page,
				 compare_page,
				 help_toast[0],
				start_toast,
				 tip_toast,
visdcc.Run_js(id='javascript')
				 ], style={
'backgroundImage': '''url("./assets/orch_anal_logo.svg")''',  # old '''url("./assets/score.jpg")'''
'backgroundRepeat': 'no-repeat',
'backgroundPosition': 'center top',
'backgroundSize': 'cover',
'backgroundAttachment': 'fixed',
'backgroundColor': '#eed',
})

app.title = 'Orchestration_Analyzer'

main_content=dac.Page([navbar, sidebar, controlbar, body])

app.layout = html.Div([main_content], style={
'backgroundColor':'#eed',
})

# =============================================================================
# Run app
# =============================================================================
def w_s():
	return app

if Production:
	if __name__ == '__main__':
		app.run_server(debug=False, threaded=True)
else:
	PORT = 8050
	ADDRESS = '0.0.0.0'
	if __name__ == '__main__':
		app.run_server(port=PORT, host=ADDRESS, debug=True)
