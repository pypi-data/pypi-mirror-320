"""Note module."""

from functools import singledispatch
from typing import List, Literal, Tuple, Union

from ._require import require

CHROMATIC_NOTES: List[str] = require('Root').CHROMATIC_NOTES
_Note = require('Root').Note
Scale = require('Scale').Scale
TimeVar = require('TimeVar').TimeVar
modi = require('Utils').modi


@singledispatch
def parse_note(note):
    """ """
    raise TypeError(f"Could not convert string '{note}' to Note")


@parse_note.register
def _(note: str):
    char = note.title()

    if len(char) == 1:
        mod = 0
    elif len(char) > 1 and (sharp := char[1:].count('#')):
        mod = sharp
    elif len(char) > 1 and (flat := char[1:].count('b')):
        mod = -flat
    else:
        raise TypeError("Could not convert string '%s' to Note" % note)

    return char, (CHROMATIC_NOTES.index(char[0]) + mod) % len(CHROMATIC_NOTES)


@parse_note.register
def _(note: int) -> Tuple[int, str]:
    return note, modi(CHROMATIC_NOTES, note)


@parse_note.register
def _(note: float) -> Tuple[TimeVar, Literal['<Micro-Tuned>']]:
    return note, '<Micro-Tuned>'


@parse_note.register
def _(note: TimeVar) -> Tuple[TimeVar, Literal['<Time-Varying>']]:
    return note, '<Time-Varying>'


class Note(_Note):
    def set(self, note: Union[str, int, float, TimeVar]):
        self.char, self.num = parse_note(note)


major = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3.5,  # G#³ | Ab³
    4,  # A³
    4.5,  # A#³ | Bb³
    5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6.5,  # D#⁴ | Eb⁴
    7,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7.5,  # F#⁴ | Gb⁴
    8,  # G⁴
    8.5,  # G#⁴ | Ab⁴
    9,  # A⁴.05
    9.5,  # A#⁴ | Bb⁴
    10,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11.5,  # D#⁵ | Eb⁵
    12,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12.5,  # F#⁵ | Gb⁵
    13,  # G⁵
    13.5,  # G#⁵ | Ab⁵
    14,  # A⁵
    14.5,  # A#⁵ | Bb⁵
    15,  # B⁵ | Cb⁶
]
major_pentatonic = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2.7,  # E#³ | F³
    3.33,  # F#³ | Gb³
    4,  # G³
    4.5,  # G#³ | Ab³
    5,  # A³
    5.66,  # A#³ | Bb³
    6.33,  # B³ | Cb⁴
    7,  # B#³ | C⁴
    7.5,  # C#⁴ | Db⁴
    8,  # D⁴
    8.5,  # D#⁴ | Eb⁴
    9,  # E⁴ | Fb⁴
    9.7,  # E#⁴ | F⁴
    10.3,  # F#⁴ | Gb⁴
    11,  # G⁴
    11.5,  # G#⁴ | Ab⁴
    12,  # A⁴.05
    12.7,  # A#⁴ | Bb⁴
    13.3,  # B⁴ | Cb⁵
    14,  # B#⁴ | C⁵
    14.5,  # C#⁵ | Db⁵
    15,  # D⁵
    15.5,  # D#⁵ | Eb⁵
    16,  # E⁵ | Fb⁵
    16.7,  # E#⁵ | F⁵
    17.3,  # F#⁵ | Gb⁵
    18,  # G⁵
    18.5,  # G#⁵ | Ab⁵
    19,  # A⁵
    19.7,  # A#⁵ | Bb⁵
    20.3,  # B⁵ | Cb⁶
]
minor = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1,  # D#³ | Eb³
    1.5,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3,  # G#³ | Ab³
    3.5,  # A³
    4,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6,  # D#⁴ | Eb⁴
    6.5,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7.5,  # F#⁴ | Gb⁴
    8,  # G⁴
    8,  # G#⁴ | Ab⁴
    8.5,  # A⁴.05
    9,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11,  # D#⁵ | Eb⁵
    11.5,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12.5,  # F#⁵ | Gb⁵
    13,  # G⁵
    13,  # G#⁵ | Ab⁵
    13.5,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]
minor_pentatonic = [
    0,  # C³
    0.68,  # C#³ | Db³
    1.33,  # D³
    2,  # D#³ | Eb³
    2.5,  # E³ | Fb³
    3,  # E#³ | F³
    3.5,  # F#³ | Gb³
    4,  # G³
    4.67,  # G#³ | Ab³
    5.33,  # A³
    6,  # A#³ | Bb³
    6.5,  # B³ | Cb⁴
    7,  # B#³ | C⁴
    7.67,  # C#⁴ | Db⁴
    8.33,  # D⁴
    9,  # D#⁴ | Eb⁴
    9.5,  # E⁴ | Fb⁴
    10,  # E#⁴ | F⁴
    10.5,  # F#⁴ | Gb⁴
    11,  # G⁴
    11.67,  # G#⁴ | Ab⁴
    12.33,  # A⁴.05
    13,  # A#⁴ | Bb⁴
    13.5,  # B⁴ | Cb⁵
    14,  # B#⁴ | C⁵
    14.67,  # C#⁵ | Db⁵
    15.33,  # D⁵
    16,  # D#⁵ | Eb⁵
    16.5,  # E⁵ | Fb⁵
    17,  # E#⁵ | F⁵
    17.5,  # F#⁵ | Gb⁵
    18,  # G⁵
    18.66,  # G#⁵ | Ab⁵
    19.33,  # A⁵
    20,  # A#⁵ | Bb⁵
    20.5,  # B⁵ | Cb⁶
]
mixolydian = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3.5,  # G#³ | Ab³
    4,  # A³
    4,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6.5,  # D#⁴ | Eb⁴
    7,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7.5,  # F#⁴ | Gb⁴
    8,  # G⁴
    8.5,  # G#⁴ | Ab⁴
    9,  # A⁴.05
    9,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11.5,  # D#⁵ | Eb⁵
    12,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12.5,  # F#⁵ | Gb⁵
    13,  # G⁵
    13.5,  # G#⁵ | Ab⁵
    14,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]
melodic_minor = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1,  # D#³ | Eb³
    1.5,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3.5,  # G#³ | Ab³
    4,  # A³
    4.5,  # A#³ | Bb³
    5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6,  # D#⁴ | Eb⁴
    6.5,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7.5,  # F#⁴ | Gb⁴
    8,  # G⁴
    8.5,  # G#⁴ | Ab⁴
    9,  # A⁴.05
    9.5,  # A#⁴ | Bb⁴
    10,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11,  # D#⁵ | Eb⁵
    11.5,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12.5,  # F#⁵ | Gb⁵
    13,  # G⁵
    13.5,  # G#⁵ | Ab⁵
    14,  # A⁵
    14.5,  # A#⁵ | Bb⁵
    15,  # B⁵ | Cb⁶
]
melodic_major = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3,  # G#³ | Ab³
    3.66,  # A³
    4.33,  # A#³ | Bb³
    5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6.5,  # D#⁴ | Eb⁴
    7,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7.5,  # F#⁴ | Gb⁴
    8,  # G⁴
    8,  # G#⁴ | Ab⁴
    8.66,  # A⁴.05
    9.33,  # A#⁴ | Bb⁴
    10,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11.5,  # D#⁵ | Eb⁵
    12,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12.5,  # F#⁵ | Gb⁵
    13,  # G⁵
    13,  # G#⁵ | Ab⁵
    13.66,  # A⁵
    14.33,  # A#⁵ | Bb⁵
    15,  # B⁵ | Cb⁶
]
harmonic_minor = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1,  # D#³ | Eb³
    1.5,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3,  # G#³ | Ab³
    3.66,  # A³
    4.33,  # A#³ | Bb³
    5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6,  # D#⁴ | Eb⁴
    6.5,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7.5,  # F#⁴ | Gb⁴
    8,  # G⁴
    8,  # G#⁴ | Ab⁴
    8.66,  # A⁴.05
    9.33,  # A#⁴ | Bb⁴
    10,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11,  # D#⁵ | Eb⁵
    11.5,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12.5,  # F#⁵ | Gb⁵
    13,  # G⁵
    13,  # G#⁵ | Ab⁵
    13.66,  # A⁵
    14.33,  # A#⁵ | Bb⁵
    15,  # B⁵ | Cb⁶
]
harmonic_major = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3,  # G#³ | Ab³
    3.66,  # A³
    4.33,  # A#³ | Bb³
    5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6.5,  # D#⁴ | Eb⁴
    7,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7.5,  # F#⁴ | Gb⁴
    8,  # G⁴
    8,  # G#⁴ | Ab⁴
    8.66,  # A⁴.05
    9.33,  # A#⁴ | Bb⁴
    10,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11.5,  # D#⁵ | Eb⁵
    12,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12.5,  # F#⁵ | Gb⁵
    13,  # G⁵
    13,  # G#⁵ | Ab⁵
    13.66,  # A⁵
    14.33,  # A#⁵ | Bb⁵
    15,  # B⁵ | Cb⁶
]
just_major = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3.5,  # G#³ | Ab³
    3.9,  # A³
    4.4,  # A#³ | Bb³
    4.9,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6.5,  # D#⁴ | Eb⁴
    6.85,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7.5,  # F#⁴ | Gb⁴
    8,  # G⁴
    8.5,  # G#⁴ | Ab⁴
    8.9,  # A⁴.05
    9.45,  # A#⁴ | Bb⁴
    9.9,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11.5,  # D#⁵ | Eb⁵
    11.85,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12.5,  # F#⁵ | Gb⁵
    13,  # G⁵
    13.5,  # G#⁵ | Ab⁵
    13.91,  # A⁵
    14.4,  # A#⁵ | Bb⁵
    14.9,  # B⁵ | Cb⁶
]
just_minor = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.05,  # D#³ | Eb³
    1.57,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3.005,  # G#³ | Ab³
    3.55,  # A³
    4.05,  # A#³ | Bb³
    4.6,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6.05,  # D#⁴ | Eb⁴
    6.56,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7.5,  # F#⁴ | Gb⁴
    8,  # G⁴
    8.005,  # G#⁴ | Ab⁴
    8.56,  # A⁴.05
    9.05,  # A#⁴ | Bb⁴
    9.56,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11.05,  # D#⁵ | Eb⁵
    11.57,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12.5,  # F#⁵ | Gb⁵
    13,  # G⁵
    13.04,  # G#⁵ | Ab⁵
    13.57,  # A⁵
    14.04,  # A#⁵ | Bb⁵
    14.57,  # B⁵ | Cb⁶
]
dorian = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1,  # D#³ | Eb³
    1.5,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3.5,  # G#³ | Ab³
    4,  # A³
    4,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6,  # D#⁴ | Eb⁴
    6.5,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7.5,  # F#⁴ | Gb⁴
    8,  # G⁴
    8.5,  # G#⁴ | Ab⁴
    9,  # A⁴.05
    9,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11,  # D#⁵ | Eb⁵
    11.5,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12.5,  # F#⁵ | Gb⁵
    13,  # G⁵
    13.5,  # G#⁵ | Ab⁵
    14,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]
dorian2 = [
    0,  # C³
    0,  # C#³ | Db³
    0.5,  # D³
    1,  # D#³ | Eb³
    1.5,  # E³ | Fb³
    2,  # E#³ | F³
    2,  # F#³ | Gb³
    2.5,  # G³
    3,  # G#³ | Ab³
    3,  # A³
    3.5,  # A#³ | Bb³
    4,  # B³ | Cb⁴
    4,  # B#³ | C⁴
    4,  # C#⁴ | Db⁴
    4.5,  # D⁴
    5,  # D#⁴ | Eb⁴
    5.5,  # E⁴ | Fb⁴
    6,  # E#⁴ | F⁴
    6,  # F#⁴ | Gb⁴
    6.5,  # G⁴
    7,  # G#⁴ | Ab⁴
    7,  # A⁴.05
    7.5,  # A#⁴ | Bb⁴
    8,  # B⁴ | Cb⁵
    8,  # B#⁴ | C⁵
    8,  # C#⁵ | Db⁵
    8.5,  # D⁵
    9,  # D#⁵ | Eb⁵
    9.5,  # E⁵ | Fb⁵
    10,  # E#⁵ | F⁵
    10,  # F#⁵ | Gb⁵
    10.5,  # G⁵
    11,  # G#⁵ | Ab⁵
    11,  # A⁵
    11.5,  # A#⁵ | Bb⁵
    12,  # B⁵ | Cb⁶
]
diminished = [
    0,  # C³
    0,  # C#³ | Db³
    0.5,  # D³
    1,  # D#³ | Eb³
    1,  # E³ | Fb³
    1.5,  # E#³ | F³
    2,  # F#³ | Gb³
    2,  # G³
    2.5,  # G#³ | Ab³
    3,  # A³
    3,  # A#³ | Bb³
    3.5,  # B³ | Cb⁴
    4,  # B#³ | C⁴
    4,  # C#⁴ | Db⁴
    4.5,  # D⁴
    5,  # D#⁴ | Eb⁴
    5,  # E⁴ | Fb⁴
    5.5,  # E#⁴ | F⁴
    6,  # F#⁴ | Gb⁴
    6,  # G⁴
    6.5,  # G#⁴ | Ab⁴
    7,  # A⁴.05
    7,  # A#⁴ | Bb⁴
    7.5,  # B⁴ | Cb⁵
    8,  # B#⁴ | C⁵
    8,  # C#⁵ | Db⁵
    8.5,  # D⁵
    9,  # D#⁵ | Eb⁵
    9,  # E⁵ | Fb⁵
    9.5,  # E#⁵ | F⁵
    10,  # F#⁵ | Gb⁵
    10,  # G⁵
    10.5,  # G#⁵ | Ab⁵
    11,  # A⁵
    11,  # A#⁵ | Bb⁵
    11.5,  # B⁵ | Cb⁶
]
egyptian = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.66,  # D#³ | Eb³
    2.33,  # E³ | Fb³
    3,  # E#³ | F³
    3.5,  # F#³ | Gb³
    4,  # G³
    4.66,  # G#³ | Ab³
    5.33,  # A³
    6,  # A#³ | Bb³
    6.5,  # B³ | Cb⁴
    7,  # B#³ | C⁴
    7.5,  # C#⁴ | Db⁴
    8,  # D⁴
    8.66,  # D#⁴ | Eb⁴
    9.33,  # E⁴ | Fb⁴
    10,  # E#⁴ | F⁴
    10.5,  # F#⁴ | Gb⁴
    11,  # G⁴
    11.66,  # G#⁴ | Ab⁴
    12.33,  # A⁴.05
    13,  # A#⁴ | Bb⁴
    13.5,  # B⁴ | Cb⁵
    14,  # B#⁴ | C⁵
    14.5,  # C#⁵ | Db⁵
    15,  # D⁵
    15.66,  # D#⁵ | Eb⁵
    16.33,  # E⁵ | Fb⁵
    17,  # E#⁵ | F⁵
    17.5,  # F#⁵ | Gb⁵
    18,  # G⁵
    18.66,  # G#⁵ | Ab⁵
    19.33,  # A⁵
    20,  # A#⁵ | Bb⁵
    20.5,  # B⁵ | Cb⁶
]
yu = [
    0,  # C³
    0.66,  # C#³ | Db³
    1.33,  # D³
    2,  # D#³ | Eb³
    2.5,  # E³ | Fb³
    3,  # E#³ | F³
    3.5,  # F#³ | Gb³
    4,  # G³
    4.66,  # G#³ | Ab³
    5.33,  # A³
    6,  # A#³ | Bb³
    6.5,  # B³ | Cb⁴
    7,  # B#³ | C⁴
    7.66,  # C#⁴ | Db⁴
    8.33,  # D⁴
    9,  # D#⁴ | Eb⁴
    9.5,  # E⁴ | Fb⁴
    10,  # E#⁴ | F⁴
    10.5,  # F#⁴ | Gb⁴
    11,  # G⁴
    11.66,  # G#⁴ | Ab⁴
    12.33,  # A⁴.05
    13,  # A#⁴ | Bb⁴
    13.5,  # B⁴ | Cb⁵
    14,  # B#⁴ | C⁵
    14.66,  # C#⁵ | Db⁵
    15.33,  # D⁵
    16,  # D#⁵ | Eb⁵
    16.5,  # E⁵ | Fb⁵
    17,  # E#⁵ | F⁵
    17.5,  # F#⁵ | Gb⁵
    18,  # G⁵
    18.66,  # G#⁵ | Ab⁵
    19.33,  # A⁵
    20,  # A#⁵ | Bb⁵
    20.5,  # B⁵ | Cb⁶
]
zhi = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.66,  # D#³ | Eb³
    2.33,  # E³ | Fb³
    3,  # E#³ | F³
    3.5,  # F#³ | Gb³
    4,  # G³
    4.5,  # G#³ | Ab³
    5,  # A³
    5.66,  # A#³ | Bb³
    6.33,  # B³ | Cb⁴
    7,  # B#³ | C⁴
    7.5,  # C#⁴ | Db⁴
    8,  # D⁴
    8.66,  # D#⁴ | Eb⁴
    9.33,  # E⁴ | Fb⁴
    10,  # E#⁴ | F⁴
    10.5,  # F#⁴ | Gb⁴
    11,  # G⁴
    11.5,  # G#⁴ | Ab⁴
    12,  # A⁴.05
    12.66,  # A#⁴ | Bb⁴
    13.33,  # B⁴ | Cb⁵
    14,  # B#⁴ | C⁵
    14.5,  # C#⁵ | Db⁵
    15,  # D⁵
    15.66,  # D#⁵ | Eb⁵
    16.33,  # E⁵ | Fb⁵
    17,  # E#⁵ | F⁵
    17.5,  # F#⁵ | Gb⁵
    18,  # G⁵
    18.5,  # G#⁵ | Ab⁵
    19,  # A⁵
    19.66,  # A#⁵ | Bb⁵
    20.33,  # B⁵ | Cb⁶
]
phrygian = [
    0,  # C³
    0,  # C#³ | Db³
    0.5,  # D³
    1,  # D#³ | Eb³
    1.5,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3,  # G#³ | Ab³
    3.5,  # A³
    4,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5,  # C#⁴ | Db⁴
    5.5,  # D⁴
    6,  # D#⁴ | Eb⁴
    6.5,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7.5,  # F#⁴ | Gb⁴
    8,  # G⁴
    8,  # G#⁴ | Ab⁴
    8.5,  # A⁴.05
    9,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10,  # C#⁵ | Db⁵
    10.5,  # D⁵
    11,  # D#⁵ | Eb⁵
    11.5,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12.5,  # F#⁵ | Gb⁵
    13,  # G⁵
    13,  # G#⁵ | Ab⁵
    13.5,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]
prometheus = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2.5,  # E#³ | F³
    3,  # F#³ | Gb³
    3.8,  # G³
    4.6,  # G#³ | Ab³
    5.4,  # A³
    6.2,  # A#³ | Bb³
    7,  # B³ | Cb⁴
    7,  # B#³ | C⁴
    7.5,  # C#⁴ | Db⁴
    8,  # D⁴
    8.5,  # D#⁴ | Eb⁴
    9,  # E⁴ | Fb⁴
    9.5,  # E#⁴ | F⁴
    10,  # F#⁴ | Gb⁴
    10.8,  # G⁴
    11.6,  # G#⁴ | Ab⁴
    12.4,  # A⁴.05
    13.2,  # A#⁴ | Bb⁴
    14,  # B⁴ | Cb⁵
    14,  # B#⁴ | C⁵
    14.5,  # C#⁵ | Db⁵
    15,  # D⁵
    15.5,  # D#⁵ | Eb⁵
    16,  # E⁵ | Fb⁵
    16.5,  # E#⁵ | F⁵
    17,  # F#⁵ | Gb⁵
    17.8,  # G⁵
    18.6,  # G#⁵ | Ab⁵
    19.4,  # A⁵
    20.2,  # A#⁵ | Bb⁵
    21,  # B⁵ | Cb⁶
]
indian = [
    0,  # C³
    0.75,  # C#³ | Db³
    1.5,  # D³
    2.25,  # D#³ | Eb³
    3,  # E³ | Fb³
    3,  # E#³ | F³
    3.5,  # F#³ | Gb³
    4,  # G³
    4.66,  # G#³ | Ab³
    5.33,  # A³
    6,  # A#³ | Bb³
    6.5,  # B³ | Cb⁴
    7,  # B#³ | C⁴
    7.75,  # C#⁴ | Db⁴
    8.5,  # D⁴
    9.25,  # D#⁴ | Eb⁴
    10,  # E⁴ | Fb⁴
    10,  # E#⁴ | F⁴
    10.5,  # F#⁴ | Gb⁴
    11,  # G⁴
    11.66,  # G#⁴ | Ab⁴
    12.33,  # A⁴.05
    13,  # A#⁴ | Bb⁴
    13.5,  # B⁴ | Cb⁵
    14,  # B#⁴ | C⁵
    14.75,  # C#⁵ | Db⁵
    15.5,  # D⁵
    16.25,  # D#⁵ | Eb⁵
    17,  # E⁵ | Fb⁵
    17,  # E#⁵ | F⁵
    17.5,  # F#⁵ | Gb⁵
    18,  # G⁵
    18.66,  # G#⁵ | Ab⁵
    19.33,  # A⁵
    20,  # A#⁵ | Bb⁵
    20.5,  # B⁵ | Cb⁶
]
locrian = [
    0,  # C³
    1,  # C#³ | Db³
    0.5,  # D³
    1,  # D#³ | Eb³
    1.5,  # E³ | Fb³
    2,  # E#³ | F³
    2,  # F#³ | Gb³
    2.5,  # G³
    3,  # G#³ | Ab³
    3.5,  # A³
    4,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5,  # C#⁴ | Db⁴
    5.5,  # D⁴
    6,  # D#⁴ | Eb⁴
    6.5,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7,  # F#⁴ | Gb⁴
    7.5,  # G⁴
    8,  # G#⁴ | Ab⁴
    8.5,  # A⁴.05
    9,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10,  # C#⁵ | Db⁵
    10.5,  # D⁵
    11,  # D#⁵ | Eb⁵
    11.5,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12,  # F#⁵ | Gb⁵
    12.5,  # G⁵
    13,  # G#⁵ | Ab⁵
    13.5,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]
locrian_major = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2,  # E#³ | F³
    2,  # F#³ | Gb³
    2.5,  # G³
    3,  # G#³ | Ab³
    3.5,  # A³
    4,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6.5,  # D#⁴ | Eb⁴
    7,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7,  # F#⁴ | Gb⁴
    7.5,  # G⁴
    8,  # G#⁴ | Ab⁴
    8.5,  # A⁴.05
    9,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11.5,  # D#⁵ | Eb⁵
    12,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12,  # F#⁵ | Gb⁵
    12.5,  # G⁵
    13,  # G#⁵ | Ab⁵
    13.5,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]
lydian = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2.5,  # E#³ | F³
    3,  # F#³ | Gb³
    3,  # G³
    3.5,  # G#³ | Ab³
    4,  # A³
    4.5,  # A#³ | Bb³
    5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6.5,  # D#⁴ | Eb⁴
    7,  # E⁴ | Fb⁴
    7.5,  # E#⁴ | F⁴
    8,  # F#⁴ | Gb⁴
    8,  # G⁴
    8.5,  # G#⁴ | Ab⁴
    9,  # A⁴.05
    9.5,  # A#⁴ | Bb⁴
    10,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11.5,  # D#⁵ | Eb⁵
    12,  # E⁵ | Fb⁵
    12.5,  # E#⁵ | F⁵
    13,  # F#⁵ | Gb⁵
    13,  # G⁵
    13.5,  # G#⁵ | Ab⁵
    14,  # A⁵
    14.5,  # A#⁵ | Bb⁵
    15,  # B⁵ | Cb⁶
]
lydian_minor = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2.5,  # E#³ | F³
    3,  # F#³ | Gb³
    3,  # G³
    3,  # G#³ | Ab³
    3.5,  # A³
    4,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6.5,  # D#⁴ | Eb⁴
    7,  # E⁴ | Fb⁴
    7.5,  # E#⁴ | F⁴
    8,  # F#⁴ | Gb⁴
    8,  # G⁴
    8,  # G#⁴ | Ab⁴
    8.5,  # A⁴.05
    9,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11.5,  # D#⁵ | Eb⁵
    12,  # E⁵ | Fb⁵
    12.5,  # E#⁵ | F⁵
    13,  # F#⁵ | Gb⁵
    13,  # G⁵
    13,  # G#⁵ | Ab⁵
    13.5,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]
custom = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1,  # D#³ | Eb³
    1.5,  # E³ | Fb³
    2,  # E#³ | F³
    2,  # F#³ | Gb³
    2.66,  # G³
    3.33,  # G#³ | Ab³
    4,  # A³
    4,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6,  # D#⁴ | Eb⁴
    6.5,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7,  # F#⁴ | Gb⁴
    7.66,  # G⁴
    8.33,  # G#⁴ | Ab⁴
    9,  # A⁴.05
    9,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11,  # D#⁵ | Eb⁵
    11.5,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12,  # F#⁵ | Gb⁵
    12.66,  # G⁵
    13.33,  # G#⁵ | Ab⁵
    14,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]
hungarian_minor = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1,  # D#³ | Eb³
    1.66,  # E³ | Fb³
    2.33,  # E#³ | F³
    3,  # F#³ | Gb³
    3,  # G³
    3,  # G#³ | Ab³
    3.66,  # A³
    4.33,  # A#³ | Bb³
    5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6,  # D#⁴ | Eb⁴
    6.66,  # E⁴ | Fb⁴
    7.33,  # E#⁴ | F⁴
    8,  # F#⁴ | Gb⁴
    8,  # G⁴
    8,  # G#⁴ | Ab⁴
    8.66,  # A⁴.05
    9.33,  # A#⁴ | Bb⁴
    10,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11,  # D#⁵ | Eb⁵
    11.66,  # E⁵ | Fb⁵
    12.33,  # E#⁵ | F⁵
    13,  # F#⁵ | Gb⁵
    13,  # G⁵
    13,  # G#⁵ | Ab⁵
    13.66,  # A⁵
    14.33,  # A#⁵ | Bb⁵
    15,  # B⁵ | Cb⁶
]
romanian_minor = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1,  # D#³ | Eb³
    1.66,  # E³ | Fb³
    2.33,  # E#³ | F³
    3,  # F#³ | Gb³
    3,  # G³
    3.5,  # G#³ | Ab³
    4,  # A³
    4.05,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6,  # D#⁴ | Eb⁴
    6.66,  # E⁴ | Fb⁴
    7.33,  # E#⁴ | F⁴
    8,  # F#⁴ | Gb⁴
    8,  # G⁴
    8.5,  # G#⁴ | Ab⁴
    9,  # A⁴
    9.05,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11,  # D#⁵ | Eb⁵
    11.66,  # E⁵ | Fb⁵
    12.33,  # E#⁵ | F⁵
    13,  # F#⁵ | Gb⁵
    13,  # G⁵
    13.5,  # G#⁵ | Ab⁵
    14,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]
chinese = [
    0,  # C³
    0.75,  # C#³ | Db³
    1.5,  # D³
    2.25,  # D#³ | Eb³
    3,  # E³ | Fb³
    3.5,  # E#³ | F³
    4,  # F#³ | Gb³
    4,  # G³
    4.75,  # G#³ | Ab³
    5.5,  # A³
    6.25,  # A#³ | Bb³
    7,  # B³ | Cb⁴
    7,  # B#³ | C⁴
    7.75,  # C#⁴ | Db⁴
    8.5,  # D⁴
    9.25,  # D#⁴ | Eb⁴
    10,  # E⁴ | Fb⁴
    10.5,  # E#⁴ | F⁴
    11,  # F#⁴ | Gb⁴
    11,  # G⁴
    11.75,  # G#⁴ | Ab⁴
    12.5,  # A⁴
    13.25,  # A#⁴ | Bb⁴
    14,  # B⁴ | Cb⁵
    14,  # B#⁴ | C⁵
    14.75,  # C#⁵ | Db⁵
    15.5,  # D⁵
    16.25,  # D#⁵ | Eb⁵
    17,  # E⁵ | Fb⁵
    17.5,  # E#⁵ | F⁵
    18,  # F#⁵ | Gb⁵
    18,  # G⁵
    18.75,  # G#⁵ | Ab⁵
    19.5,  # A⁵
    20.25,  # A#⁵ | Bb⁵
    21,  # B⁵ | Cb⁶
]
whole_tone = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2.5,  # E#³ | F³
    3,  # F#³ | Gb³
    3.5,  # G³
    4,  # G#³ | Ab³
    4.5,  # A³
    5,  # A#³ | Bb³
    5.5,  # B³ | Cb⁴
    6,  # B#³ | C⁴
    6.5,  # C#⁴ | Db⁴
    7,  # D⁴
    7.5,  # D#⁴ | Eb⁴
    8,  # E⁴ | Fb⁴
    8.5,  # E#⁴ | F⁴
    9,  # F#⁴ | Gb⁴
    9.5,  # G⁴
    10,  # G#⁴ | Ab⁴
    10.5,  # A⁴
    11,  # A#⁴ | Bb⁴
    11.5,  # B⁴ | Cb⁵
    12,  # B#⁴ | C⁵
    12.5,  # C#⁵ | Db⁵
    13,  # D⁵
    13.5,  # D#⁵ | Eb⁵
    14,  # E⁵ | Fb⁵
    14.5,  # E#⁵ | F⁵
    15,  # F#⁵ | Gb⁵
    15.5,  # G⁵
    16,  # G#⁵ | Ab⁵
    16.5,  # A⁵
    17,  # A#⁵ | Bb⁵
    17.5,  # B⁵ | Cb⁶
]
whole_half = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1,  # D#³ | Eb³
    1.5,  # E³ | Fb³
    2,  # E#³ | F³
    2,  # F#³ | Gb³
    2.5,  # G³
    3,  # G#³ | Ab³
    3,  # A³
    3.5,  # A#³ | Bb³
    4,  # B³ | Cb⁴
    4,  # B#³ | C⁴
    4.5,  # C#⁴ | Db⁴
    5,  # D⁴
    5,  # D#⁴ | Eb⁴
    5.5,  # E⁴ | Fb⁴
    6,  # E#⁴ | F⁴
    6,  # F#⁴ | Gb⁴
    6.5,  # G⁴
    7,  # G#⁴ | Ab⁴
    7,  # A⁴
    7.5,  # A#⁴ | Bb⁴
    8,  # B⁴ | Cb⁵
    8,  # B#⁴ | C⁵
    8.5,  # C#⁵ | Db⁵
    9,  # D⁵
    9,  # D#⁵ | Eb⁵
    9.5,  # E⁵ | Fb⁵
    10,  # E#⁵ | F⁵
    10,  # F#⁵ | Gb⁵
    10.5,  # G⁵
    11,  # G#⁵ | Ab⁵
    11,  # A⁵
    11.5,  # A#⁵ | Bb⁵
    12,  # B⁵ | Cb⁶
]
bebop_major = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3,  # G#³ | Ab³
    3,  # A³
    3.5,  # A#³ | Bb³
    4,  # B³ | Cb⁴
    4,  # B#³ | C⁴
    4.5,  # C#⁴ | Db⁴
    5,  # D⁴
    5.5,  # D#⁴ | Eb⁴
    6,  # E⁴ | Fb⁴
    6,  # E#⁴ | F⁴
    6.5,  # F#⁴ | Gb⁴
    7,  # G⁴
    7,  # G#⁴ | Ab⁴
    7,  # A⁴
    7.5,  # A#⁴ | Bb⁴
    8,  # B⁴ | Cb⁵
    8,  # B#⁴ | C⁵
    8.5,  # C#⁵ | Db⁵
    9,  # D⁵
    9.5,  # D#⁵ | Eb⁵
    10,  # E⁵ | Fb⁵
    10,  # E#⁵ | F⁵
    10.5,  # F#⁵ | Gb⁵
    11,  # G⁵
    11,  # G#⁵ | Ab⁵
    11,  # A⁵
    11.5,  # A#⁵ | Bb⁵
    12,  # B⁵ | Cb⁶
]
bebop_minor = [  # aka Bebop Minor
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1,  # D#³ | Eb³
    1,  # E³ | Fb³
    1,  # E#³ | F³
    1.75,  # F#³ | Gb³
    2.5,  # G³
    3.25,  # G#³ | Ab³
    4,  # A³
    4,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6,  # D#⁴ | Eb⁴
    6,  # E⁴ | Fb⁴
    6,  # E#⁴ | F⁴
    6.75,  # F#⁴ | Gb⁴
    7.5,  # G⁴
    8.25,  # G#⁴ | Ab⁴
    9,  # A⁴
    9,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11,  # D#⁵ | Eb⁵
    11,  # E⁵ | Fb⁵
    11,  # E#⁵ | F⁵
    11.75,  # F#⁵ | Gb⁵
    12.5,  # G⁵
    13.25,  # G#⁵ | Ab⁵
    14,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]
bebop_dominant = [  # Bebop Dominant/Mixolydian
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3.5,  # G#³ | Ab³
    4,  # A³
    4,  # A#³ | Bb³
    4,  # B³ | Cb⁴
    4,  # B#³ | C⁴
    4.5,  # C#⁴ | Db⁴
    5,  # D⁴
    5.5,  # D#⁴ | Eb⁴
    6,  # E⁴ | Fb⁴
    6,  # E#⁴ | F⁴
    6.5,  # F#⁴ | Gb⁴
    7,  # G⁴
    7.5,  # G#⁴ | Ab⁴
    8,  # A⁴
    8,  # A#⁴ | Bb⁴
    8,  # B⁴ | Cb⁵
    8,  # B#⁴ | C⁵
    8.5,  # C#⁵ | Db⁵
    9,  # D⁵
    9.5,  # D#⁵ | Eb⁵
    10,  # E⁵ | Fb⁵
    10,  # E#⁵ | F⁵
    10.5,  # F#⁵ | Gb⁵
    11,  # G⁵
    11.5,  # G#⁵ | Ab⁵
    12,  # A⁵
    12,  # A#⁵ | Bb⁵
    12,  # B⁵ | Cb⁶
]
bebop_melodic_minor = [  # Bebop Melodic Minor
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1,  # D#³ | Eb³
    1.5,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3,  # G#³ | Ab³
    3,  # A³
    3.5,  # A#³ | Bb³
    4,  # B³ | Cb⁴
    4,  # B#³ | C⁴
    4.5,  # C#⁴ | Db⁴
    5,  # D⁴
    5,  # D#⁴ | Eb⁴
    5.5,  # E⁴ | Fb⁴
    6,  # E#⁴ | F⁴
    6.5,  # F#⁴ | Gb⁴
    7,  # G⁴
    7,  # G#⁴ | Ab⁴
    7,  # A⁴
    7.5,  # A#⁴ | Bb⁴
    8,  # B⁴ | Cb⁵
    8,  # B#⁴ | C⁵
    8.5,  # C#⁵ | Db⁵
    9,  # D⁵
    9,  # D#⁵ | Eb⁵
    9.5,  # E⁵ | Fb⁵
    10,  # E#⁵ | F⁵
    10.5,  # F#⁵ | Gb⁵
    11,  # G⁵
    11,  # G#⁵ | Ab⁵
    11,  # A⁵
    11.5,  # A#⁵ | Bb⁵
    12,  # B⁵ | Cb⁶
]
blues = [
    0,  # C³
    0.66,  # C#³ | Db³
    1.33,  # D³
    2,  # D#³ | Eb³
    2.5,  # E³ | Fb³
    3,  # E#³ | F³
    3,  # F#³ | Gb³
    3,  # G³
    3.66,  # G#³ | Ab³
    4.33,  # A³
    5,  # A#³ | Bb³
    5.5,  # B³ | Cb⁴
    6,  # B#³ | C⁴
    6.66,  # C#⁴ | Db⁴
    7.33,  # D⁴
    8,  # D#⁴ | Eb⁴
    8.5,  # E⁴ | Fb⁴
    9,  # E#⁴ | F⁴
    9,  # F#⁴ | Gb⁴
    9,  # G⁴
    9.66,  # G#⁴ | Ab⁴
    10.33,  # A⁴
    11,  # A#⁴ | Bb⁴
    11.5,  # B⁴ | Cb⁵
    12,  # B#⁴ | C⁵
    12.66,  # C#⁵ | Db⁵
    13.33,  # D⁵
    14,  # D#⁵ | Eb⁵
    14.5,  # E⁵ | Fb⁵
    15,  # E#⁵ | F⁵
    15,  # F#⁵ | Gb⁵
    15,  # G⁵
    15.66,  # G#⁵ | Ab⁵
    16.33,  # A⁵
    17,  # A#⁵ | Bb⁵
    17.5,  # B⁵ | Cb⁶
]
min_maj = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1,  # D#³ | Eb³
    1.5,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3.5,  # G#³ | Ab³
    4,  # A³
    4.5,  # A#³ | Bb³
    5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6,  # D#⁴ | Eb⁴
    6.5,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7.5,  # F#⁴ | Gb⁴
    8,  # G⁴
    8.5,  # G#⁴ | Ab⁴
    9,  # A⁴
    9.5,  # A#⁴ | Bb⁴
    10,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11,  # D#⁵ | Eb⁵
    11.5,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12.5,  # F#⁵ | Gb⁵
    13,  # G⁵
    13.5,  # G#⁵ | Ab⁵
    14,  # A⁵
    14.5,  # A#⁵ | Bb⁵
    15,  # B⁵ | Cb⁶
]
susb9 = [
    0,  # C³
    0,  # C#³ | Db³
    0.5,  # D³
    1,  # D#³ | Eb³
    1.5,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3.5,  # G#³ | Ab³
    4,  # A³
    4,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5,  # C#⁴ | Db⁴
    5.5,  # D⁴
    6,  # D#⁴ | Eb⁴
    6.5,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7.5,  # F#⁴ | Gb⁴
    8,  # G⁴
    8.5,  # G#⁴ | Ab⁴
    9,  # A⁴
    9,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10,  # C#⁵ | Db⁵
    10.5,  # D⁵
    11,  # D#⁵ | Eb⁵
    11.5,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12.5,  # F#⁵ | Gb⁵
    13,  # G⁵
    13.5,  # G#⁵ | Ab⁵
    14,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]
lydian_aug = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2.5,  # E#³ | F³
    3,  # F#³ | Gb³
    3.5,  # G³
    4,  # G#³ | Ab³
    4,  # A³
    4.5,  # A#³ | Bb³
    5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6.5,  # D#⁴ | Eb⁴
    7,  # E⁴ | Fb⁴
    7.5,  # E#⁴ | F⁴
    8,  # F#⁴ | Gb⁴
    8.5,  # G⁴
    9,  # G#⁴ | Ab⁴
    9,  # A⁴
    9.5,  # A#⁴ | Bb⁴
    10,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11.5,  # D#⁵ | Eb⁵
    12,  # E⁵ | Fb⁵
    12.5,  # E#⁵ | F⁵
    13,  # F#⁵ | Gb⁵
    13.5,  # G⁵
    14,  # G#⁵ | Ab⁵
    14,  # A⁵
    14.5,  # A#⁵ | Bb⁵
    15,  # B⁵ | Cb⁶
]
lydian_dom = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2.5,  # E#³ | F³
    3,  # F#³ | Gb³
    3,  # G³
    3.5,  # G#³ | Ab³
    4,  # A³
    4,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6.5,  # D#⁴ | Eb⁴
    7,  # E⁴ | Fb⁴
    7.5,  # E#⁴ | F⁴
    8,  # F#⁴ | Gb⁴
    8,  # G⁴
    8.5,  # G#⁴ | Ab⁴
    9,  # A⁴
    9,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11.5,  # D#⁵ | Eb⁵
    12,  # E⁵ | Fb⁵
    12.5,  # E#⁵ | F⁵
    13,  # F#⁵ | Gb⁵
    13,  # G⁵
    13.5,  # G#⁵ | Ab⁵
    14,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]

mel_min_5th = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1.5,  # D#³ | Eb³
    2,  # E³ | Fb³
    2,  # E#³ | F³
    2.5,  # F#³ | Gb³
    3,  # G³
    3,  # G#³ | Ab³
    3.5,  # A³
    4,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6.5,  # D#⁴ | Eb⁴
    7,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7.5,  # F#⁴ | Gb⁴
    8,  # G⁴
    8,  # G#⁴ | Ab⁴
    8.5,  # A⁴
    9,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11.5,  # D#⁵ | Eb⁵
    12,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12.5,  # F#⁵ | Gb⁵
    13,  # G⁵
    13,  # G#⁵ | Ab⁵
    13.5,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]
half_dim = [
    0,  # C³
    0.5,  # C#³ | Db³
    1,  # D³
    1,  # D#³ | Eb³
    1.5,  # E³ | Fb³
    2,  # E#³ | F³
    2,  # F#³ | Gb³
    2.5,  # G³
    3,  # G#³ | Ab³
    3.5,  # A³
    4,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5.5,  # C#⁴ | Db⁴
    6,  # D⁴
    6,  # D#⁴ | Eb⁴
    6.5,  # E⁴ | Fb⁴
    7,  # E#⁴ | F⁴
    7,  # F#⁴ | Gb⁴
    7.5,  # G⁴
    8,  # G#⁴ | Ab⁴
    8.5,  # A⁴
    9,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10.5,  # C#⁵ | Db⁵
    11,  # D⁵
    11,  # D#⁵ | Eb⁵
    11.5,  # E⁵ | Fb⁵
    12,  # E#⁵ | F⁵
    12,  # F#⁵ | Gb⁵
    12.5,  # G⁵
    13,  # G#⁵ | Ab⁵
    13.5,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]
altered = [
    0,  # C³
    0,  # C#³ | Db³
    0.5,  # D³
    1,  # D#³ | Eb³
    1,  # E³ | Fb³
    1.5,  # E#³ | F³
    2,  # F#³ | Gb³
    2.5,  # G³
    3,  # G#³ | Ab³
    3.5,  # A³
    4,  # A#³ | Bb³
    4.5,  # B³ | Cb⁴
    5,  # B#³ | C⁴
    5,  # C#⁴ | Db⁴
    5.5,  # D⁴
    6,  # D#⁴ | Eb⁴
    6,  # E⁴ | Fb⁴
    6.5,  # E#⁴ | F⁴
    7,  # F#⁴ | Gb⁴
    7.5,  # G⁴
    8,  # G#⁴ | Ab⁴
    8.5,  # A⁴
    9,  # A#⁴ | Bb⁴
    9.5,  # B⁴ | Cb⁵
    10,  # B#⁴ | C⁵
    10,  # C#⁵ | Db⁵
    10.5,  # D⁵
    11,  # D#⁵ | Eb⁵
    11,  # E⁵ | Fb⁵
    11.5,  # E#⁵ | F⁵
    12,  # F#⁵ | Gb⁵
    12.5,  # G⁵
    13,  # G#⁵ | Ab⁵
    13.5,  # A⁵
    14,  # A#⁵ | Bb⁵
    14.5,  # B⁵ | Cb⁶
]

_scales = {
    'major': major,
    'majorPentatonic': major_pentatonic,
    'minor': minor,
    'aeolian': minor,
    'minorPentatonic': minor_pentatonic,
    'mixolydian': mixolydian,
    'melodicMinor': melodic_minor,
    'melodicMajor': melodic_major,
    'harmonicMinor': harmonic_minor,
    'harmonicMajor': harmonic_major,
    'justMajor': just_major,
    'justMinor': just_minor,
    'dorian': dorian,
    'dorian2': dorian2,
    'diminished': diminished,
    'egyptian': egyptian,
    'yu': yu,
    'zhi': zhi,
    'phrygian': phrygian,
    'prometheus': prometheus,
    'indian': indian,
    'locrian': locrian,
    'locrianMajor': locrian_major,
    'lydian': lydian,
    'lydianMinor': lydian_minor,
    'custom': custom,
    'hungarianMinor': hungarian_minor,
    'romanianMinor': romanian_minor,
    'chinese': chinese,
    'wholeTone': whole_tone,
    'halfWhole': diminished,
    'wholeHalf': whole_half,
    'bebopMaj': bebop_major,
    'bebopMin': bebop_minor,
    'bebopDorian': bebop_minor,
    'bebopDom': bebop_dominant,
    'bebopMelMin': bebop_melodic_minor,
    'blues': blues,
    'minMaj': min_maj,
    'susb9': susb9,
    'lydianAug': lydian_aug,
    'lydianDom': lydian_dom,
    'melMin5th': mel_min_5th,
    'halfDim': half_dim,
    'altered': altered,
}


def from_chromatic(note: int) -> int:
    """Get note from chromatic.

    Parameters
    ----------
    note : int
        Note on the chromatic scale.

    Returns
    -------
    int
        Chromatic scale note converted to current scale.

    Raises
    ------
    ValueError
        Scale not supported.
    """
    scale = Scale.default.name

    if scale == 'chromatic':
        return note
    if scale not in _scales:
        raise ValueError(
            f'Scale {scale} does not support, '
            f'the supported scales are: chromatic, {", ".join(_scales.keys())}'
        )
    return note - _scales[Scale.default.name][note]
