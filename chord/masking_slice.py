def get_slice(lista, orchestra):
    import dash_html_components as html
    import dash_core_components as dcc
    import plotly.graph_objs as go
    import pickle
    import numpy as np
    import maskingCurve
	from helpers import constants
	#import MFCC
    #import lpc_coeffs

from score import combine_peaks

from help import get_help


def help(topic):
        return html.Div(html.Details([html.Summary('?', className='button'), html.Div(get_help.help(topic))]))

    def target_and_orchestration(list_of_instruments):
        # list_of_instruments: instrument, technique, dynamics, note, target, on/off
        orchestration_sum=np.zeros(44100)
        target_sum=np.zeros(44100)
        peaks_o = []
        peaks_t = []
        orch_mfcc_array=np.array(np.zeros(12))
        targ_mfcc_array = np.array(np.zeros(12))
        min_orch_note=120
        min_target_note=120
        t_cents=[]
        o_cents=[]
        for instrument in list_of_instruments:
            if instrument[-1]==1: #If instrument is set "on"
                if instrument[-2]==0: #if orchestration
                    odata=orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['data']
                    orchestration_sum = orchestration_sum+orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['data']
                    orch_mfcc_array=np.vstack([orch_mfcc_array, orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['mfcc']])
                    o_cents.append(orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['centroid'])
                    pl, pf = findPeaks.peaks(get_fft.get_fft(odata), instrument[3])
                    peaks_o = combine_peaks.combine_peaks(peaks_o, [pl, pf])#orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['peaks'])
                    if instrument[3]<min_orch_note:
                         min_orch_note=instrument[3]
                if instrument[-2] == 1: #if target
                    tdata=orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['data']
                    target_sum = target_sum+orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['data']
                    t_cents.append(orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['centroid'])
                    targ_mfcc_array = np.vstack([targ_mfcc_array,orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['mfcc']])
                    pl, pf = findPeaks.peaks(get_fft.get_fft(tdata), instrument[3])
                    peaks_t = combine_peaks.combine_peaks(peaks_t, [pl, pf])#orchestra[instrument[0]][instrument[1]][instrument[2]][instrument[3]]['peaks'])
                    if instrument[3]<min_target_note:
                         min_target_note=instrument[3]
        sums=[orchestration_sum, target_sum]
        min_notes=[]
        min_notes=[min_orch_note, min_target_note]
        orch_mfcc_array=np.delete(orch_mfcc_array, 0, axis=0) #Poistetaan nollat alusta häiritsemästä
        targ_mfcc_array=np.delete(targ_mfcc_array, 0, axis=0)
        orch_mfcc= np.mean(orch_mfcc_array, axis=0)
        targ_mfcc=np.mean(targ_mfcc_array, axis=0)
        t_cents = np.mean(t_cents)
        o_cents = np.mean(o_cents)
        return sums, min_notes, orch_mfcc_array, [peaks_o, peaks_t], [orch_mfcc, targ_mfcc], [o_cents, t_cents]

    import maskingCurve_peakInput
    import maskingCurve
	from helpers import constants, get_fft, findPeaks
import helpers.get_fft
    def get_features(data, peaks, min_note, mfccs, cents):
        result=dict()

        S= get_fft.get_fft(data)
        result["spectrum"]=S
        try:
            masking_threshold = maskingCurve_peakInput.maskingCurve(S, peaks) #Calculate the masking curve
            ## l, masking_threshold = maskingCurve.maskingCurve(S, min_note)
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

    sums, min_notes, orch_mfcc_array, peaks, mean_mffcs, mean_cents = target_and_orchestration(lista) #Returns sums list with 2 elements: [orchestration target], peaks [orch, tar]
    orchestration = get_features(sums[0], peaks[0], min_notes[0], mean_mffcs[0], mean_cents[0])
    target = get_features(sums[1], peaks[1], min_notes[1], mean_mffcs[1], mean_cents[1])


    fig_layout = {
        'plot_bgcolor': "rgba(0,0,0,0)",
        'paper_bgcolor': "rgba(0,0,0,0)",
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
        "height": 700,  # px
    }
    fig_layout2 = {
        'plot_bgcolor': "rgba(0,0,0,0)",
        'paper_bgcolor': "rgba(0,0,0,0)",
        'font': {
            'color': 'white'
        },
        "title": "Orchestration and target centroids",
        'yaxis': {'title':  'Frequency in Hz'},
    }
    fig_layout3 = {
        'plot_bgcolor': "rgba(0,0,0,0)",
        'paper_bgcolor': "rgba(0,0,0,0)",
        'font': {
            'color': 'white'
        },
        "title": "Orchestration and target mfcc:s",
        'yaxis': {'title':  'MFCCs'},
    }
    fig_layout4 = {
        'plot_bgcolor': "rgba(0,0,0,0)",
        'paper_bgcolor': "rgba(0,0,0,0)",
        'font': {
            'color': 'white'
        },
        'xaxis': {'title': ''},
        "title": "Mfcc vectors",
        'yaxis': {'title':  'mfcc values'},
    }
    fig_config = {
        'displayModeBar': False
    }

    #fig = go.Figure().add_trace(go.Scatter(x=orchestration['masking_locs'], y=orchestration['masking_threshold']), layout=fig_layout, xaxis_type="log")

    color=[]
    #Tässä interpoloidaan maskauskäyrän välit vastaamaan targetin huippuja:
    idx_above = target['peaks'] > np.interp(target['peak_locs'], orchestration['masking_locs'], orchestration['masking_threshold'])
    for i in range(len(idx_above)):
        if idx_above[i]:
            color.append(1)
        else: color.append(0)
    #Käyrän alla punainen rasti, käyrän yllä vihreä rasti:
    colorscale = [[0, 'red'], [1.0, 'green']]

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
        "x": ['orchestration centroid', 'target centroid'],
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
    fig1 = go.Figure(data=[trace1, trace3, trace2, vertical_line, hearing_threshold, stem_trace, spec_trace], layout=fig_layout)
    fig2 = go.Figure(data=[trace4], layout=fig_layout2)
    fig3 = go.Figure(data=[trace5], layout=fig_layout3)
    mfcc_fig = go.Figure(data=[mfcc_vector_trace1, mfcc_vector_trace2], layout=fig_layout4)
    #fig = go.Figure(data=[go.Scatter(x=orchestration['masking_locs'], y=orchestration['masking_threshold'])], layout=fig_layout)

    return html.Div([help('single_masking'),
                     html.Div(dcc.Graph(id='masking-graph',figure=fig1, config=fig_config)),
                             html.Div("There are {} target peaks above the masking threshold".format(np.count_nonzero(idx_above == True))),
                     help('single_features'),
                             html.Div([dcc.Graph(id='centroid-graph', figure=fig2, config=fig_config)],
                                      style={'width': '48%', 'display': 'inline-block'}),
                             html.Div([dcc.Graph(id='mfcc-graph', figure=fig3, config=fig_config)],
                                      style={'width': '48%', 'display': 'inline-block'}),
                     help('mfcc_vector'),
                             html.Div(dcc.Graph(id='mfcc-vector',figure=mfcc_fig, config=fig_config)),
                             html.Div(id='place'),
                             ], className='waiting')

# # Tällä saadaan graafista näkyvä alue, sekä klikkauskohta
# @app.callback(
#     dash.dependencies.Output('place', 'children'),
#     [dash.dependencies.Input('masking-graph', 'relayoutData'),
#      dash.dependencies.Input('masking-graph', 'clickData'),
#     dash.dependencies.Input('masking-graph', 'hoverData'),
#     dash.dependencies.Input('masking-graph', 'selectedData'),
#      ])
# def range_values(ranges, clicks, hovers, selects):
#     print('tuosta: ')
#     if ranges != None and 'xaxis.range' in ranges:
#         left = 10 ** ranges['xaxis.range'][0] #Näillä saadaan logaritmisesta asteikosta hertsit
#         right = 10 ** ranges['xaxis.range'][1]
#         print(left) #Vasen ja oikea raja hertseinä
#         print(right)
#     if clicks != None: #Vältetään error katsomalla että klikkauskohdassa on tietoa
#         print(clicks['points'][0]['x'])
#         print(clicks)
#     #print(hovers) #tällä saadaan kursorin alla oleva data ilman klikkiä
#     #print(selects) #graafin valintadata, ei kantsi käyttää
#     return 'x'
