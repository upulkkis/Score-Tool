import dash_core_components as dcc
import base64
import dash_html_components as html

def imageload(img_path):
    img_l = img_path
    img_l = base64.b64encode(open(img_l, 'rb').read())
    return img_l
im1 = imageload('./dissertation/image1.png')
im2 = imageload('./dissertation/image2.png')
im3 = imageload('./dissertation/image3.png')
im4 = imageload('./dissertation/image4.png')
im5 = imageload('./dissertation/image5.png')
im6 = imageload('./dissertation/image6.png')
im7 = imageload('./dissertation/image7.png')
im8 = imageload('./dissertation/image8.png')
im9 = imageload('./dissertation/image9.png')

def field_test_text():
    return html.Div([dcc.Markdown(children='''
Field test, Thu 30th Jan 2020
===================================
---
Subject\
An experienced composer with a new work for chamber orchestra.

Motivation\
To check a few orchestration excerpts with possible masking problems.

Meeting\
At composer's studio with me and my laptop. Program running on my
computer.

General remarks\
The usage of the program was not at all clear for the first-timer. My
presence was essential for the test to work. Even the score navigation
according to the piano-roll view appeared to be difficult for myself,
when the musical score was not familiar. The composer was familiar with
the basic concepts of sound spectrum, masking and critical bands, but
the meaning of the graphs in my program were not clear for the composer
at the first glance. When I pronounced out loud what one could see on
graphs and what is the significance of the numbers, the composer seemed
to understand the parameters.

Checked excerpts\
The composer selected five discrete passages from the score with
unchanging orchestration. From these passages we decided together to
take moment under special investigation. From these passages two were
more or less self-explanatory (like oboe solo with thin orchestration),
but three were interesting test cases for my program.

First passage\
The passage included colorful orchestration with wide spread on
register. There was a slight mismatch on orchestration and the database.
The composer used Bartok pizzicato, which we replaced with ordinary
pizzicato, and flatterzunge was replaced by tremolo. The composer wanted
to know if the bassoon could be heard. In the passage the bassoons play
a triton on low register. Currently my program doesn't support multiple
targets, so I decided that we set the bassoon 1 as target and turn the
bassoon 2 off. In the rehearsals the other bassoonist was absent, so
luckily our choice was spot on. The score can be seen on example 3.

The masking graph (example 1) of the score showed some green spots for
the bassoon sound, and clicking the mouse indicated good target
audibility on a few of the 106 used bands. Note that low bands are on
top and high bands are on bottom.
'''), html.Div([
            html.Img(src='data:image/png;base64,{}'.format(im1.decode()), style={'height': '40vw'})
        ], style={'textAlign': 'center'}), dcc.Markdown(children='''

The expert view (example 2) on the same spot as previous mouse click
shows that some components of the bassoon sound are indeed over the
masking curve, but some of the louder overtones are heavily masked by
the orchestration. The orchestration variation coefficient showed the
number 0.516772, indicating that the orchestration sound color would be
on the homogenous side. According to the data I assumed that the low
sound can be heard, but the bassoon would blend in.
'''),
html.Div([
            html.Img(src='data:image/png;base64,{}'.format(im2.decode()), style={'height': '40vw'})
        ], style={'textAlign': 'center'}), html.Div([
            html.Img(src='data:image/png;base64,{}'.format(im3.decode()), style={'height': '40vw'})
        ], style={'textAlign': 'center'}), dcc.Markdown(children='''

After the rehearsals the composer reported to me on first passage as
follows:

> "Matalien fagottien sulautuminen: Tässä haittasi toisen fagotin
> puuttuminen, joten homma meni hiukan "laimeaksi\" jo tästäkin syystä.
> Matala fagotti kuului aika hiljaisena ja pyöreänä (ei fagottina),
> mutta kuului. Meni aika tavalla ennustuksen mukaisesti. Mainittu
> "laimeus\" johtuu toki myös matalan tritonuksen puuttumisesta."
>
> "The blending of the low bassoons: Here disturbed the absence of the
> other bassoon, so the thing went slightly "mild" already for that. The
> low bassoon could be heard quiet and round (not as bassoon), but could
> be heard. Went more or less like suspected. The "mildness" I mentioned
> is caused, of course, by the absence of the tritone." (Translation by
> the writed)

Second passage
--------------

In this passage, the composer wanted to investigate the possible masking
of flutes with low dynamics. Here I found an unfortunate glitch in my
program. Even though the dynamics on score are marked at low levels, my
program assumed them as mf. Therefore, the general graph showed wrong
results and was useless. We switched right away to expert view, and
investigated the middle of the last bar in example 4.
'''),
html.Div([
            html.Img(src='data:image/png;base64,{}'.format(im4.decode()), style={'height': '40vw'})
        ], style={'textAlign': 'center'}), dcc.Markdown(children='''

In the expert view I turned the dynamics of all instruments to piano, as
it is the lowest dynamic setting on the database. This doesn't represent
the score excerpt well, as the dynamic markings on the score vary from
ppp to mp. This required some explanation from my side about the graphs
in this situation; we are not investigating the actual orchestration,
but a simulation which might or not match the actual performance. The
spectral content of an instrument sound may not vary much when played
ppp vs. p, but the perceived loudness may vary several decibels, and
thus the graph here is a very coarse approximation.

The masking graph shows a strong peak for the notated pitch of the
flute. The overtones are masked by the orchestration, although something
from the overtones around 1kHz could be heard. The orchestration
variation coefficient shows a quite high number, 1.76251, at this
orchestration, indicating non-homogenous color. The program estimated
that the strongest masker would be the 1^st^ violin. According to the
data I assumed that the "fluteness" of the sound could be hard to
perceive, but the notated tone could probably be heard.

'''),
html.Div([
            html.Img(src='data:image/png;base64,{}'.format(im5.decode()), style={'height': '40vw'})
        ], style={'textAlign': 'center'}), dcc.Markdown(children='''

After the rehearsals the composer reported to me on second passage as
follows:

> "Huilut väliäänissä: Aluksi huilujen komppi (paisutukset) erottuivat,
> mutta ne jäivät myöhemmin jousien ja oboen alle. Muistiinpanoissani
> lukee, että välillä viulut peittävät, joten kyllä. Jotain toki kuului,
> mutta säestyskomppia ei oikein erottanut jousien ja oboen alta.
> Ennustuksen lupaama "huilumaisuuden" katoaminen mielestäni toteutui:
> Neutraali pyöreä ääni, joka lähestyi hiljaista käyrätorvea."
>
> "Flutes on middle voices: At first the riff of the flutes (swells)
> could be heard, but they remained later under strings and oboe. My
> notes say, that sometimes violins mask, so yes. Something could be
> heard, but accompaniment riff could not be clearly heard under strings
> and oboe. The suspected disappearance of "fluteness" came true from my
> point of view: A neutral round tone, which came close to quiet French
> horn." (Translated by the writer)

Third passage
-------------

The third passage was an orchestral tutti. The score can be seen on
example 9. The dynamic marking for all instruments is ff, and the
composer wanted to know if the melodic line of the french horn could be
heard.

In the program the dynamic marking of f was automatically assigned for
each instrument. This might give reliable result for other instruments
except brass, which emphasize the overtone content at high dynamic
levels.

I noticed immediately the problem with the target instruments with
unison. In future versions there is a need for a "unison" switch, which
raises the curves by 3dB if there's a second instrument, similar to
target, playing in unison. In this situation I was unsure how to correct
the graph, so we used the results as if there were only one french horn
in the orchestra.

In this passage we first noticed that the overall masking graph of the
passage showed green (example 6), but in 3d-view the green peaks
appeared to be just a bit over the masking threshold of the
orchestration. Clicking by mouse on the green area (example 7) showed
that the spectral peaks are just 1dB over the masking threshold, which
indicates that it is hard to tell if the target sound is audible.

'''),
html.Div([
            html.Img(src='data:image/png;base64,{}'.format(im6.decode()), style={'height': '40vw'})
        ], style={'textAlign': 'center'}), dcc.Markdown(children='''
'''),
html.Div([
            html.Img(src='data:image/png;base64,{}'.format(im7.decode()), style={'width': '40vw'})
        ], style={'textAlign': 'center'}), dcc.Markdown(children='''

The expert view on the point of mouse click on example 7 confirms the
masking situation on 3d-graph. There are some french horn peaks over the
masking threshold, but the most of the sound should be inaudible. To
support this opinion, the spectral centroid of the orchestration seems
to be much greater than the spectral centroid of the target. French horn
seems therefore have a darker tone compared to the orchestration, and
thus be even harder to hear in this passage (see example 8). The
variation coefficient is 0.506133, indicating a homogenous
orchestration. According to the data, I assumed that he French horn
would be masked, and the program suggests that the strongest masker
would be the trumpet.

'''),
html.Div([
            html.Img(src='data:image/png;base64,{}'.format(im8.decode()), style={'height': '40vw'})
        ], style={'textAlign': 'center'}), dcc.Markdown(children='''
'''),
html.Div([
            html.Img(src='data:image/png;base64,{}'.format(im9.decode()), style={'height': '40vw'})
        ], style={'textAlign': 'center'}), dcc.Markdown(children='''

There was a slight misconception from what I told the composer and what
the composer's notes from the meeting were. After the rehearsals the
composer reported to me on third passage as follows:

> "Alun tutti. Se yksi trumpetti, joka oli paikalla tuli komeasti läpi,
> mutta käyrätorvet kyllä erotti mainiosti trumpetista huolimatta. kuten
> ohjelmasi arvioi. Ohjelma ennusti myös, että käyrätorvien väri olisi
> tummempi. Kenties, mutta kyllä soitin oli selkeästi edelleen
> tunnistettavissa."
>
> "Tutti at the beginning. The one trumpet present at the rehearsals
> came through gracefully, but the french horns could be heard fine
> despite the trumpet. Like your program estimated \[sic\]. The program
> estimated also, that the sound color of the french horns would be
> darker. Probably so, but the instrument was clearly still
> recognizable."

This was an interesting case, as even though the dB rating of the french
horn would rise by 3 because of the unison, the most of the graph would
still be under the masking threshold. I suspect the reason for the
failed estimation could be the extra brassy kick for the sound that
comes from moving from forte to fortissimo. The interesting test would
be to play the same passage with only forte, and hear if the result
matches the estimated masking.

Afterthoughts
-------------

The first field test showed that, as much as there is room for
improvement, the program gives rational results. The biggest drawback is
the user interface, which needs to be improved in order to be
understandable by a common musician. The composer of the field test was
interested of the program, but did not directly use the results to
improve the orchestration. The feedback from the rehearsals was still
valuable, and revealed where the program needs to be improved.

The experience made me think, that maybe the optimal score for the
program would be a solo concerto, where the audibility of the target
instrument would be highly desirable, and the unisons would not be such
a problem. Still, out of the described passages, 2 out of 3 predictions
correlated with the hearing experience.

    ''')])