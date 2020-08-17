import dash_core_components as dcc
from textwrap import dedent

def masking_text():
    return dcc.Markdown(children=dedent('''
**About masking in orchestration**
==================================
---

In orchestral music, especially in passages for many simultaneous
instrumental parts, certain soft-sounding instrument sounds can be hard
to detect from the rest of the orchestration. The inaudibility of soft
instrument sounds in the presence of louder sounds is strong when
multiple instruments are playing in the same register. Inaudibility
affects not only to the listener's hearing experience, but also the
musician, the instrumentalist who plays the inaudible part. Usually an
experienced composer can avoid these kinds of situations and orchestrate
the music in such way that every part has its purpose. In my experience
however, an instruments sound can be inaudible even though the register
of that instruments part should be free. These kinds of -- surprising --
orchestration fails can be investigated in terms of psychoacoustics,
more closely in the field of *auditory masking*.

*Auditory masking* is a phenomenon where a soft sound in inaudible in
the presence of louder sound.[^1] Inaudibility of weaker sound happens
especially when the two sounds have roughly similar spectral content. A
situation where a loud sound masks a soft sound with different spectral
content is called *spectral masking*. Spectral masking can occur even
though the spectra of two sounds don't overlap. If the soft sound is
still audible in the presence of loud sound, but the perceived loudness
of the soft sound is reduced, *partial masking* occurs.

Auditory masking in orchestral music is mostly partial- or spectral
masking, but there might be cases of *informational masking*, which will
be discussed later. We might even assume that partial masking happens
nearly every time when two or more orchestral instruments play
simultaneously, unless the instrument's spectra doesn't overlap at all.

Spectral masking thresholds have been widely tested with pure sinewave
tone (test tone) and noise. In the presence of white noise, masked
threshold of the test tone is constant at low frequencies, up to about
500 Hz. Above that threshold rise with increasing frequency. At 10 kHz
the masked threshold is about 10dB higher than at 500 Hz.[^2] Although
white noise has very little in common with orchestral sound, the 500 Hz
turning point is important, since the average distribution of energy in
the sound of orchestral music peaks at 300Hz.[^3] Thus the frequency
region with constant masked threshold, the area under 500 Hz, is of high
importance for orchestral music.

Listening tests conducted with narrow band noise show that the masking
effect is strong when the masking noise and masked tone are at the same
critical band. Masking effect spreads, however, to adjacent critical
bands by a frequency slope, which is narrow at frequencies over 500 Hz,
and gets wider at frequencies under 500 Hz. The amount of spread depends
also by the loudness of the masker, louder masking noise generates wider
spread. [^4]

Tests with a noise masking a tone are popular since our ear is much more
sensitive to tones than noise. Noise is often considered as a disturbing
element and tone as something that contains information. Orchestral
music, and also music in general, consists mainly of tones with pitches
and noise element is present mostly on percussion instruments.
Situations where an instrument sound is masking another instrument sound
are therefore far from noise-masking-tone listening tests.

Masking experiments of a sine wave tone masking another sine wave tone
have proven to have many difficulties.[^5] In a presence of a tone, any
sensation which alters the tone have an effect. If the masker and masked
tones are at the same critical band, we hear beating or roughness when
another tone is present. This happens even when another tone is masked
inaudible. In listening tests, the subject responds in this kind of
situation, although the criterion is different from hearing an
additional tone.[^6]

Additionally, difference tone produced by two adjacent tones disturb the
hearing experience. The difference tone is produced through nonlinear
distortions that originate in our own hearing system.[^7] In listening
tests the subject often hears the difference tone, even though the
original tone is masked. Audible difference tones occur especially at
the frequencies between 1 an 2kHz.

As with the narrow band masker, the tone masker produces also spread to
adjacent critical bands. Interestingly the frequency slope of the spread
is greater towards the low frequencies at low loudness levels. At high
levels, this behavior is reversed, so that a greater spread of masking
is found towards higher frequencies. The effect at low levels is rather
unexpected. At a 20dB masker level, more spread of masking towards lower
frequencies occur, at 40dB masking is symmetrical and at 60dB there is
more spread towards higher frequencies. [^8] The relation of the masker
level and masked threshold is nonlinear; an increment in masker level of
1dB can produce an increment in the masked threshold up to 6dB.[^9]

In orchestral music pure sine wave tones does not occur. Instrument
sounds are composed of a fundamental tone, harmonics and low-level noise
and non-harmonic components. For complex tones, the masking threshold is
determined by combining the masking thresholds of each sinusoidal
component with their spreading frequency slopes. Therefore, the masking
effect of an orchestral instrument depends of its spectrum. For example,
a flute produces a strong single component and faint spectrum, but for
example a trumpet produces many harmonics. Thus, a trumpet creates
broader masking effect than a flute. Tests show that when there are at
least five sinusoidal components at the same critical band, the masking
effect is like the narrow band noise. At levels below 50dB even three
components are enough for the same effect.[^10]

When masking curve of complex tones are determined, it is important to
remember that also difference tones produce masking. It can however be
assumed that the frequency selectivity of the ear remains the same,
irrespective of whether a complex tone or narrow-band noise is used as
the masker. The difference is that complex tones, due to differential
tones, produce more masking at the low-frequency side than narrow band
noise.[^11]

The sound of an acoustical instrument also varies in time. The high
partials fade relatively quick in comparison with the fundamental and
low partials. The onset of an instrument sound contains also a short
burst of noise and non-harmonic components, which decay in milliseconds.
It is then logical to assume that the masking effect of an orchestral
instrument is strong at onset time and fades along with the higher
partials. In orchestral music, the amount of reverb also affects the
masking threshold, as to onset components sound longer in reverberant
space than in dry space.

The widely accepted masking threshold of music was estimated for the
mp3-compression algorithm. The masking threshold was set by listening
tests to a secure level, where no subject could hear the masked test
tone. The safe level is 13dB below the sound energy on critical band. In
mp3-industry this is called the 13dB miracle.[^12]

When multiple orchestral instruments play at the same time and the
masking level of single instrument is to be estimated, the question of
addition of masking thresholds comes up. It is important to remember
that addition of masking does not follow the rules of the addition of
intensity. The presence of two maskers does not automatically result 6dB
gain in masking threshold. Tests show that the strongest masker seem to
be dominant and additional maskers add only little to the masking
threshold. In an example, when four maskers produce the same masked
threshold, 20dB above threshold in quiet, an increment only to 21dB can
be achieved when the four maskers are presented simultaneously.[^13]

In orchestral music there is currently only little research of the
masking phenomena. According to a study, when two instruments playing in
same range, the one will not cover the other unless the level difference
is between 20-25 dB.[^14] This conclusion, however, is made according to
root notes and doesn't take the spectral content into account. The
author of the study also points out that the audibility of instruments
formant areas is essential for the discrimination of instrument from the
orchestration. In order to determine the audibility, the masking
threshold at the formant areas weigh more than the masking threshold in
general.

The special case of masking is informational masking. According to the
definition of the term, a sound could be masked even if there are no
other stimuli within the same critical band. Informational masking
occurs when a harmonic sound with simple spectral content appears with
sound with rich spectral content, even with non-overlapping spectra.
Listening tests were made by single sinusoid against complex harmonic
sound. Informational masking was strongest, masking even 50dB sinusoids,
when the spectral content of the masker was fewer than 20 partials[^15],
which applies to most of the orchestral instruments.

Interestingly, when sound of the informational masker has a high number
of partials, over 20 that is, our hearing system treats it as noise,
resulting the normal rules of auditory masking to apply. In orchestral
music, the informational masking is thus as its strongest when a
sinusoid-like instrument, for example a recorder, plays against a small
ensemble, for example a wind quartet.

[^1]: Ville Pulkki and Matti Karjalainen, *Communication acoustics: an
    introduction to speech, audio and psychoacoustics*, p.156, John
    Wiley & Sons., U.K., 2015.

[^2]: Hugo Fastl, Eberhard Zwicker, *Psychoacoustics - Facts and
    Models*, p.63, Springer, New York, 2007.

[^3]: Johan Sundberg, *The Acoustics of the Singing Voice*, Scientific
    American, p.89, New York, 1977

[^4]: Hugo Fastl, Eberhard Zwicker, *Psychoacoustics - Facts and
    Models*, p.64, Springer, New York, 2007.

[^5]: Ibid. p.67

[^6]: Hugo Fastl, Eberhard Zwicker, *Psychoacoustics - Facts and
    Models*, p.67, Springer, New York, 2007.

[^7]: Ibid.

[^8]: Ibid. p.69.

[^9]: Ibid. p.70.

[^10]: Hugo Fastl, Eberhard Zwicker, *Psychoacoustics - Facts and
    Models*, p.72, Springer, New York, 2007.

[^11]: Ibid. p.74.

[^12]: Karlheintz Brandenburg and G. Stoll. *ISO-MPEG-1 Audio: a generic
    standard for coding of high quality digital audio*. In N. Gilchrist
    and Ch. Grewin, editors, Collected Papers on Digial Audio Bit-Rate
    Reduction. AES, 1996.

[^13]: Hugo Fastl, Eberhard Zwicker, *Psychoacoustics - Facts and
    Models*, p.104, Springer, New York, 2007.

[^14]: Christoph Reuter. *Die auditive Diskrimination von
    Orchesterinstrumenten*. Germany, Frankfurt, Lang. 1996.

[^15]: Stanley A Gelfand. *Hearing: An Introduction to Psychological and
    Physiological Acoustics*. U.K., Chippenham, Wiltshire, 2010.

'''))