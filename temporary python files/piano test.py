from datetime import datetime

from dash import dash

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_dangerously_set_inner_html as di


app = dash.Dash(__name__)
app.scripts.config.serve_locally = True
app.config.suppress_callback_exceptions = True


pianokeys=html.Div([
html.Div( className="key white c"      ),
html.Div( className="key black c_sharp"),
html.Div( className="key white d"      ),
html.Div( className="black d_sharp"),
html.Div( className="key white e"      ),
html.Div( className="key white f"      ),
html.Div( className="key black f_sharp"),
html.Div( className="key white g"      ),
html.Div( className="key black g_sharp"),
html.Div( className="key white a"      ),
html.Div( className="key black a_sharp"),
html.Div( className="key white b"      )],
    id='keyboard')

pianokeys=di.DangerouslySetInnerHTML('''
<div id="keyboard">
  <div class="key white c" data-note="C3"></div>
  <div class="key black c_sharp" data-note="C#3"></div>
  <div class="key white d" data-note="D3"></div>
  <div class="key black d_sharp" data-note="D#3"></div>
  <div class="key white e" data-note="E3"></div>
  <div class="key white f" data-note="F3"></div>
  <div class="key black f_sharp" data-note="F#3"></div>
  <div class="key white g" data-note="G3"></div>
  <div class="key black g_sharp" data-note="G#3"></div>
  <div class="key white a" data-note="A3"></div>
  <div class="key black a_sharp" data-note="A#3"></div>
  <div class="key white b" data-note="B3"></div>
  <div class="key white c" data-note="C4"></div>
  <div class="key black c_sharp" data-note="C#4"></div>
  <div class="key white d" data-note="D4"></div>
  <div class="key black d_sharp" data-note="D#4"></div>
  <div class="key white e" data-note="E4"></div>
  <div class="key white f" data-note="F4"></div>
  <div class="key black f_sharp" data-note="F#4"></div>
  <div class="key white g" data-note="G4"></div>
  <div class="key black g_sharp" data-note="G#4"></div>
  <div class="key white a" data-note="A4"></div>
  <div class="key black a_sharp" data-note="A#4"></div>
  <div class="key white b" data-note="B4"></div>
  <div class="key white c" data-note="C5"></div>
  <div class="key black c_sharp" data-note="C#5"></div>
  <div class="key white d" data-note="D5"></div>
  <div class="key black d_sharp" data-note="D#5"></div>
  <div class="key white e" data-note="E5"></div>
  <div class="key white f" data-note="F5"></div>
  <div class="key black f_sharp" data-note="F#5"></div>
  <div class="key white g" data-note="G5"></div>
  <div class="key black g_sharp" data-note="G#5"></div>
  <div class="key white a" data-note="A5"></div>
  <div class="key black a_sharp" data-note="A#5"></div>
  <div class="key white b" data-note="B5"></div>
</div>
''')
layout = [html.Div(id='piano', children=pianokeys, style={'background':'white', 'width': 300, 'height':100}), html.Div(id='testi')]

app.layout = html.Div(children=html.Div(layout))


@app.callback(Output('testi', 'children'),
            [Input('piano', 'children')])#.format(delete(model_id))])
def callbacki(data):

    return data





if __name__ == '__main__':
    app.run_server(debug=True)