import dash_daq as daq
import dash_html_components as html
import dash_core_components as dcc
import dash_admin_components as dac
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import numpy as np
from score import combine_peaks
from help import get_help
import heapq

plot_color='black'
paper_color=  'rgba(0,0,0,.2)'

def get_slice(lista, orchestra, custom_id='', initial_chord=''):
    dummy_fft_size = 22048

    def help(topic):
        return html.Div(html.Details([html.Summary('?', className='button'), html.Div(get_help.help(topic))]))

    def target_and_orchestration(list_of_instruments):
        # list_of_instruments: instrument, technique, dynamics, note, target, on/off
        S = np.ones(dummy_fft_size) + 70
        orchestration_sum=np.zeros(44100)
        target_sum=np.zeros(44100)
        peaks_o = []
        peaks_t = []
        masking_curves_o = []
        masking_curves_t = []
        orch_mfcc_array=np.array(np.zeros(12))
        targ_mfcc_array = np.array(np.zeros(12))
        min_orch_note=120
        min_target_note=120
        t_cents=[]
        o_cents=[]
        inst_idx_number=0
        orchestration_indexes=[]
        for instrument in list_of_instruments:
            if instrument[-1]==1: #If instrument is set "on"
                if instrument[-2]==0: #if orchestration
                    #odata=orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['data']
                    #orchestration_sum = orchestration_sum+orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['data']
                    orch_mfcc_array=np.vstack([orch_mfcc_array, orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['mfcc']])
                    o_cents.append(orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['centroid'])
                    pks = orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['peaks']
                    peaks_o = combine_peaks.combine_peaks(peaks_o, [pks[0], pks[1]])#orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['peaks'])
                    masking_curves_o.append(maskingCurve_peakInput.maskingCurve(S, pks))

                    #Make a list of orchestration instrument indexes for masking calculation:
                    orchestration_indexes.append(inst_idx_number)

                    if instrument[3]<min_orch_note:
                         min_orch_note=instrument[3]
                if instrument[-2] == 1: #if target
                    #tdata=orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['data']
                    #target_sum = target_sum+orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['data']
                    t_cents.append(orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['centroid'])
                    targ_mfcc_array = np.vstack([targ_mfcc_array,orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['mfcc']])
                    pks = orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['peaks']
                    peaks_t = combine_peaks.combine_peaks(peaks_t, [pks[0], pks[1]])#orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['peaks'])
                    masking_curves_t.append(maskingCurve_peakInput.maskingCurve(S, pks))
                    if instrument[3]<min_target_note:
                         min_target_note=instrument[3]
            inst_idx_number += 1
        sums=[orchestration_sum+70, target_sum+70]
        #print(masking_curves_o)
        tgt=True
        if peaks_t == []:tgt=False
        orch_mfcc_array=np.delete(orch_mfcc_array, 0, axis=0) #Poistetaan nollat alusta häiritsemästä
        orch_mfcc= np.mean(orch_mfcc_array, axis=0)
        o_cents = np.mean(o_cents)
        min_notes = [min_orch_note, 0]
        targ_mfcc=[]
        if tgt:
            min_notes=[min_orch_note, min_target_note]
            targ_mfcc_array=np.delete(targ_mfcc_array, 0, axis=0)
            targ_mfcc=np.mean(targ_mfcc_array, axis=0)
            t_cents = np.mean(t_cents)

        return sums, min_notes, orch_mfcc_array, [peaks_o, peaks_t], [orch_mfcc, targ_mfcc], [o_cents, t_cents], [masking_curves_o, masking_curves_t], orchestration_indexes

    from chord import maskingCurve_peakInput
    from chord import maskingCurve
    from helpers import constants
    from helpers import get_fft

    def get_features(data, peaks, min_note, mfccs, cents):
            result=dict()
            S=np.ones(dummy_fft_size)+70
            result["spectrum"]=S
            try:
                masking_threshold = maskingCurve_peakInput.maskingCurve(S, peaks) #Calculate the masking curve
            except:
                print("Masking calculation fail, using flat masking curve")
                masking_threshold = np.ones(106)
            result['masking_locs']= constants.threshold[:, 0]
            result['masking_threshold']=masking_threshold
            #print("masking calculated")
            #mfcc_data, centroid = MFCC.custom_mfcc(data) #Calculate mfcc and spectral centroid
            result['mfcc']= mfccs#mfcc_data
            result['centroid']= cents#centroid
            #print("mfcc calculated")
            #LpcLocs, LpcFreqs = lpc_coeffs.lpc_coeffs(data) #calculate LPC-frequency response
            #result['lpc_locs']=LpcLocs
            #result['lpc_threshold']=LpcFreqs
            #locs, peaks = findPeaks.peaks(S, min_note)
            result['peak_locs']=peaks[0]
            result['peaks']=peaks[1]
            #print("lpc calculated")
            return result

    sums, min_notes, orch_mfcc_array, peaks, mean_mffcs, mean_cents, masking_lists, orchestration_indexes = target_and_orchestration(lista) #Returns sums list with 2 elements: [orchestration target], peaks [orch, tar]
    orchestration = get_features(sums[0], peaks[0], min_notes[0], mean_mffcs[0], mean_cents[0])
    tgt=True
    if mean_cents[1] == []: tgt = False
    if tgt:
        target = get_features(sums[1], peaks[1], min_notes[1], mean_mffcs[1], mean_cents[1])
    else:
        result = dict()
        result['masking_locs']= constants.threshold[:, 0]
        result['masking_threshold']=np.ones(106)
        #print("masking calculated")
        #mfcc_data, centroid = MFCC.custom_mfcc(data) #Calculate mfcc and spectral centroid
        result['mfcc']= orchestration['mfcc']
        result['spectrum'] = np.ones(44100)
        result['centroid']= 0
        #print("mfcc calculated")
        #LpcLocs, LpcFreqs = lpc_coeffs.lpc_coeffs(data) #calculate LPC-frequency response
        #result['lpc_locs']=LpcLocs
        #result['lpc_threshold']=LpcFreqs
        #locs, peaks = findPeaks.peaks(S, min_note)
        result['peak_locs']=[]
        result['peaks']=[]
        target=result


    fig_layout = {
        'plot_bgcolor': plot_color,
        'paper_bgcolor': paper_color,
        'font': {
            'color': 'white'
        },
        'xaxis': {'title': 'Frequency in Hz', 'type': 'log',
                  'rangeslider': {'visible': True},
                  'rangeselector': {'visible':True,
                                    'buttons':[{'step':'all'}, {'step':'day'}, {'step':'hour'}]},
                  'showgrid': False,
                  #'range': [1, 1.5],
                  },
        "title": "Masking curve",
        'yaxis': {'title':  'dB (SPL)', 'showgrid': False, 'zeroline': False},
        'dragmode': 'pan',
        #'grid': {'rows': 1, 'columns': 2},
        #"height": '99vh',  # view height
    }
    fig_layout2 = {
        'plot_bgcolor': plot_color,
        'paper_bgcolor': paper_color,
        'font': {
            'color': 'white'
        },
        "title": "Centroids",
        'yaxis': {'title':  'Frequency in Hz'},
    }
    fig_layout3 = {
        'plot_bgcolor': plot_color,
        'paper_bgcolor': paper_color,
        'font': {
            'color': 'white'
        },
        "title": "Orchestration and target mfcc:s",
        'yaxis': {'title':  'MFCCs'},
    }
    fig_layout4 = {
        'plot_bgcolor': plot_color,
        'paper_bgcolor': paper_color,
        'font': {
            'color': 'white'
        },
        'xaxis': {'title': ''},
        "title": "Mfcc vectors",
        'yaxis': {'title':  'mfcc values'},
    }
    audibility_layout = {
        'plot_bgcolor': plot_color,
        'paper_bgcolor': paper_color,
        'font': {
            'color': 'white'
        },
        "title": "Audibility of the target",
    }
    dark_layout = {
        'plot_bgcolor': plot_color,
        'paper_bgcolor': paper_color,
        'font': {
            'color': 'white'
        },
    }
    fig_config = {
        'displayModeBar': False
    }

    #fig = go.Figure().add_trace(go.Scatter(x=orchestration['masking_locs'], y=orchestration['masking_threshold']), layout=fig_layout, xaxis_type="log")

    color=[]
    #Tässä interpoloidaan maskauskäyrän välit vastaamaan targetin huippuja:
    hearing_target_list = target['peaks'] - np.interp(target['peak_locs'], orchestration['masking_locs'], orchestration['masking_threshold'])
    #print(hearing_target_list)
    idx_above = target['peaks'] > np.interp(target['peak_locs'], orchestration['masking_locs'], orchestration['masking_threshold'])
    indexes_above=0;
    for i in range(len(idx_above)):
        if idx_above[i]:
            color.append(1)
            indexes_above+=1
        else: color.append(0)
    #Käyrän alla punainen rasti, käyrän yllä vihreä rasti:
    colorscale = [[0, 'red'], [1.0, 'green']]
    output_masking_order_idx=[]
    if tgt and indexes_above < len(target['peaks']/2):
        for i in range(len(masking_lists[0])):
            #!! Find the 15 loudest peaks for target, subtract them from orchestration:
            tgt_peaks = heapq.nlargest(15, range(len(target['masking_threshold'])), key=target['masking_threshold'].__getitem__)
            masking_lists[0][i] = np.subtract(masking_lists[0][i][tgt_peaks], np.array(target['masking_threshold'])[tgt_peaks])
            masking_lists[0][i] = np.sum(masking_lists[0][i][0:40])

        masking_order_idx = heapq.nlargest(len(masking_lists[0]), range(len(masking_lists[0])), key=masking_lists[0].__getitem__)
        masking_order=[]
        output_masking_order_idx=[]
        for id in masking_order_idx:
            masking_order.append(lista[orchestration_indexes[id]])
            output_masking_order_idx.append(orchestration_indexes[id])

    trace1 = {
        "mode": "markers",
        "type": "scatter",
        "x": target['peak_locs'],
        "y": target['peaks'],
        "name": "Audible peaks",
        "marker": {'symbol': 'x', 'size': 12, 'color': color, 'colorscale': colorscale, 'line':{'width': 0}}, #Tässä laitetaan eri väriset rastit kuuluvuuden mukaan
        "line": {'color': 'Green', 'width': 5},
    }

    #Build stems for peaks
    peak_stems_x = []
    peak_stems_y = []
    for i in range(len(target['peak_locs'])):
        peak_stems_x.append(target['peak_locs'][i]-10)
        peak_stems_y.append(-30)
        peak_stems_x.append(target['peak_locs'][i])
        peak_stems_y.append(target['peaks'][i])
        peak_stems_x.append(target['peak_locs'][i] + 10)
        peak_stems_y.append(-30)
        peak_stems_x.append(None)
        peak_stems_y.append(None)

    stem_trace = {
        "mode": "lines",
        "type": "scatter",
        "x": peak_stems_x,
        "y": peak_stems_y,
        "line": {'color': 'Grey', 'width': 4},
        "opacity": 0.7,
        "showlegend": False,
    }

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
        "y": np.zeros(106)-30,
        'line': {'width': 0}
    }

    trace4 = {
        "type": "bar",
        "x": ['orchestration', 'target'],
        "y": [orchestration['centroid'], target['centroid']]
    }


    cv = lambda x: np.std(x) / np.mean(x)
    var = np.apply_along_axis(cv, axis=0, arr=orch_mfcc_array)
    var_coeff = np.mean(abs(var))
    trace5 = {
        "type": "bar",
        "x": ['Target mfcc distance to orch.', 'Orchestration variation coefficient'],
        "y": [np.linalg.norm(orchestration['mfcc'][1:]-target['mfcc'][1:]), var_coeff]
    }
    mfcc_distance=np.linalg.norm(orchestration['mfcc'][1:]-target['mfcc'][1:])
    distance = {
        'mode': "gauge+number",
        "type": "indicator",
        'value': mfcc_distance,
        'domain': {'x': [0, 1], 'y': [0, 1]},
        'title': {'text': "Target mfcc distance"}
    }

    mfcc_vector_trace1 = {
        "mode": "lines",
        "type": "scatter",
        "y": orchestration['mfcc'][1:],
        "name": "orchestration mfcc vector",
        "line": {'color': 'yellow'},
    }

    mfcc_vector_trace2 = {
        "mode": "lines",
        "type": "scatter",
        "y": target['mfcc'][1:],
        "name": "target mfcc vector",
        "line": {'color': 'purple'},
        "fill": "tonexty",
        "fillcolor": "grey"
    }

    def generate_barks():
        xx=[]
        yy=[]
        for f in constants.barks:
            xx = [*xx, *[f, f, None]]
            yy = [*yy, *[100, -20, None]]
        xx[-1]=[]
        yy[-1]=[]
        return xx, yy
    xx, yy = generate_barks()
    vertical_line = {
        "mode": "lines",
        "type": "scatter",
        "x": xx,
        "y": yy,
        "opacity": 0.3,
        "name": "Critical bands"
    }

    hearing_threshold = {
        "mode": "lines",
        "type": "scatter",
        "x": constants.threshold[:, 0],
        "y": constants.threshold[:, 2],
        "opacity": 0.7,
        "name": "Hearing threshold",
        "line": {"dash": "dash", "color": "red"},
    }

    spect=target['spectrum']
    spect[spect<-30]=-30
    spec_trace = {
        "mode": "lines",
        "type": "scatter",
        "x": np.arange(19919)[86:],
        "y": target['spectrum'][86:19919],
        "opacity": 0.1,
        "name": "spectrum"
    }

    audibility = {
        'mode': "gauge+number",
        "type": "indicator",
        'value': 270,
        'domain': {'x': [0, 1], 'y': [0, 1]},
        'title': {'text': "Audibility"}

    }
    if np.count_nonzero(idx_above == True)==0:
        masking_percent=100
    else:
        masking_percent=100-100*(np.count_nonzero(idx_above == True)/len(idx_above))
    #print(masking_percent)
    def inline(graph):
        return html.Div(graph, style={'display':'inline-block'})

    if orchestration['centroid']>(target['centroid']+200):
        brightness="The orchestration is brighter than target."
    elif (target['centroid']-200)<=orchestration['centroid']<=(target['centroid']+200):
        brightness="The orchestration and target are about equal bright."
    elif orchestration['centroid']<(target['centroid']-200):
        brightness="The target is brighter than orchestration."

    if mfcc_distance<20:
        color_distance="The orchestration and the target have about same sound color."
    elif 20<=mfcc_distance<=70:
        color_distance="The target sound color differs from orchestration slightly."
    elif mfcc_distance>=70:
        color_distance="The target sound has differrent sound color than orchestration."

    masker=''
    if tgt and indexes_above < len(target['peaks']/2):
        masker = "The heaviest masker is {} playing {}.".format(masking_order[0][0], masking_order[0][2])
        if masking_order[0][2]=='p':
            masker += ' Concider changing the register of {}, or revise the orchestration.'.format(masking_order[0][0])
        else:
            masker += ' Concider lowering dynamics of {}, or increase dynamics of target.'.format(masking_order[0][0])
        if len(masking_order)>1:
            masker += " The second heaviest masker is {} playing {}.".format(masking_order[1][0], masking_order[1][2])
        if len(masking_order)>2:
            masker += " The third heaviest masker is {} playing {}.".format(masking_order[2][0], masking_order[2][2])

    fig1 = go.Figure(data=[trace1, trace3, trace2, vertical_line, hearing_threshold, stem_trace], layout=fig_layout)     #Removing spectrum increase screen update, so, this is out: spec_trace
    fig2 = go.Figure(data=[trace4], layout=fig_layout2)
    fig3 = go.Figure(data=[trace5], layout=fig_layout3)
    distance= go.Figure(data=[distance], layout=dark_layout)
    #print(mfcc_vector_trace1)
    mfcc_fig = go.Figure(data=[mfcc_vector_trace1, mfcc_vector_trace2], layout=fig_layout4)
    audibility= go.Figure(data=audibility, layout=audibility_layout)
    #fig = go.Figure(data=[go.Scatter(x=orchestration['masking_locs'], y=orchestration['masking_threshold'])], layout=fig_layout)

    def make_box(content, width):
        return dac.Box([dac.BoxBody(content)],width=width)

    masking_graph = make_box(html.Div(className='masking', children=[
                     html.Div(dcc.Graph(id='masking-graph{}'.format(custom_id),figure=fig1, config=fig_config),
                              )]),12),
    gauge_graph = html.Div(className='gauge', children=[
                         #dcc.Graph(id='audibility', figure=audibility, config=fig_config),
                         daq.GraduatedBar(vertical=True, value=masking_percent, max=100, step=1,
                                          style={'color': 'black'}, showCurrentValue=True,
                                          color={"gradient": True, "ranges": {"green": [0, 50], "yellow": [50, 90], "red": [90, 100]}},
                                          label={'label': '% of target peaks masked',
                                                 'style': {'color': 'white'}})
                     ]),
    summary_graph = dac.Box([dac.BoxHeader(title='Summary:', collapsible=False, style={'height':50}),dac.BoxBody(html.Div(className='teksti', children=[
                             html.Div("There are {} target peaks above the masking threshold.".format(np.count_nonzero(idx_above == True))+" "+brightness+" "+color_distance+" "+masker
                                      ),
                              ], style={'textAlign':'center'}))], width=12),
    mfcc_graph = html.Div(className='mfcc', children=[
                              html.Div(dcc.Graph(id='mfcc-vector{}'.format(custom_id), figure=mfcc_fig, config=fig_config, style={'height':300})),
                              html.Div(id='place{}'.format(custom_id))
                              ]),
    centroid_graph = make_box(html.Div(className='bar1', children=[
        html.Div([dcc.Graph(id='centroid-graph{}'.format(custom_id), figure=fig2, config=fig_config, style={'height':240})]),
    ]),12),

    #This is made-up value, distances are approx up to 250
    mfcc_distance_value = mfcc_distance / 250 * 100

    distance_graph = html.Div(className='bar2', children=[
         #html.Div([dcc.Graph(id='distance-graph', figure=distance, config=fig_config)]),
         daq.GraduatedBar(vertical=True, value=mfcc_distance_value, max=100, step=1, id='distance-graph{}'.format(custom_id),
                         style={'color': 'black'}, #showCurrentValue=True,
                         color={"gradient": True, "ranges": {"green": [0, 50], "yellow": [50, 90], "red": [90, 100]}},
                         label={'label': 'Target color distance from orchestration',
                                'style': {'color': 'white'}})
     ]),

    hom_val = (2-var_coeff)/2*100
    var_coeff_graph = html.Div(className='bar3', children=[
                             #html.Div([dcc.Graph(id='varcoeff-graph', figure=fig3, config=fig_config)]),
                            daq.GraduatedBar(vertical=True, value=hom_val, max=100, step=1, style={'color':'black', 'textAlign':'center'},showCurrentValue=True, color={"gradient":True,"ranges":{"grey":[0,50], "green":[50,100]}},label={'label':'Homogenuity % of orchestration', 'style':{'color':'white'}})
                    ]),

    Analyze_graph = html.Div([
        dbc.Row([
            #dbc.Col([summary_graph[0], centroid_graph[0]], width=3),
            dbc.Col(masking_graph, width=12)
        ]),
        dbc.Row([
            dbc.Col(make_box(dbc.Row([
                dbc.Col(gauge_graph[0]),
                dbc.Col(distance_graph[0]),
                dbc.Col(var_coeff_graph[0]),
            ]), 12), width=6),
        dbc.Col(make_box(mfcc_graph[0],12), width=6),
                    ])])

    return orchestration, target, Analyze_graph, summary_graph[0], output_masking_order_idx



