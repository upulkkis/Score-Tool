import dash_core_components as dcc

def history_text():
    return dcc.Markdown(children='''
**About history of orchestration**
==================================
---

Before approximately the year 1600, music was not written for specific
instruments. The only specification was either "vocal" or
"instrumental".[^1] When music was performed, the conductor assigned the
parts for available instruments. Thus, instrumentation and sound color
were not parameters in the art of music composition. In those days, if a
melodic line couldn't be heard because it was masked by the
instrumentation, it was perhaps fixed on the fly by changing the
melody's register or the assignment of the parts.

The main focus back then was on vocal music, which was written precisely
for certain registers, certain pitches and certain note durations.
Instrumental parts, however, were improvised according to harmonic key
notes, a system called *basso generale*, the "general bass".[^2] If an
instrumentalist played, for example, a top part of the orchestration,
the player would choose what to play according to the notated bass line.
This skill was part of a musician's training, and the best musicians
would even improvise ornaments in their parts. In other words, the piece
is identity was not as strong as today, as the piece would change from
one performance to another.

The first composition to include instrumentation was, according to
Richard Truskin, a piece titled *In ecclesiis benedicite Domino* ("Bless
the Lord in the congregations") by Giovanni Gabrieli, written around the
year 1605.[^3] The piece is written for four-part choir, four-part
soloists and a seven-part instrumental group. This time the instrumental
parts were also labeled for specific instruments. The instrumentation
included three cornetti, a violino and two trombones, of which the
violino was a brand new type of instrument resembling somewhat a modern
viola in its range.

In Gabrieli's piece there are hints that the composer was aware of some
timbral aspects of his orchestration. There are, for example, several
general pauses which were most likely added to avoid the sonic overload
when the piece was performed in a cathedral with a long reverberation
time. The pauses let the echo clear before the next phrase. Although
most of the time Gabrieli used the full instrumentation, there are
several sections where only cornetti are playing in turns with the
soprani.

In Gabrieli's later years new kinds of compositional genres emerged,
namely *canzona per sonare*, literally "a song for playing", and
*canzona sonata*, "a played song".[^4] These purely instrumental works
-- as the genre names indicate -- tried first to mimic vocal music. As
the number of pieces written for these new genres grew, composers began
to take advantage of the unique possibilities of each instrument.
Especially the violino gained a special role due to its ability of
virtuoso playing. For works written for violino, it was thus crucial to
indicate the instrument's name in the score, as the virtuosic part would
be unplayable with any other available instrument.

These examples of Gabrieli's music are already a primal form of
orchestration, which would then in centuries to come grow to take more
important roles as a compositional parameter. Even though the core
concepts of my thesis, masking and blending, were certainly not on the
table back in Gabrieli's time, the importance of the audibility of the
desired target instrument was undoubtedly as important for Gabrieli as
it is for composers of today.

[^1]: Richard Taruskin, *Oxford History of Western Music*,
    <https://www-oxfordwesternmusic-com.ezproxy.uniarts.fi/view/Volume1/actrade-9780195384819-div1-018006.xml?rskey=q8obLK&result=1>,
    accessed 26 Oct. 2019

[^2]: Ibid.

[^3]: Ibid.

[^4]: Richard Taruskin, *Oxford History of Western Music*,
    <https://www-oxfordwesternmusic-com.ezproxy.uniarts.fi/view/Volume1/actrade-9780195384819-div1-018007.xml>,
    accessed 26 Oct. 2019

 ''')