# Generated from txt2musicxml/grammer/Chords.g4 by ANTLR 4.13.2
import sys
from io import StringIO

from antlr4 import *

if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,
        0,
        12,
        95,
        6,
        -1,
        2,
        0,
        7,
        0,
        2,
        1,
        7,
        1,
        2,
        2,
        7,
        2,
        2,
        3,
        7,
        3,
        2,
        4,
        7,
        4,
        2,
        5,
        7,
        5,
        2,
        6,
        7,
        6,
        2,
        7,
        7,
        7,
        2,
        8,
        7,
        8,
        2,
        9,
        7,
        9,
        2,
        10,
        7,
        10,
        2,
        11,
        7,
        11,
        1,
        0,
        1,
        0,
        1,
        1,
        1,
        1,
        4,
        1,
        30,
        8,
        1,
        11,
        1,
        12,
        1,
        31,
        1,
        1,
        1,
        1,
        1,
        2,
        1,
        2,
        1,
        3,
        4,
        3,
        39,
        8,
        3,
        11,
        3,
        12,
        3,
        40,
        1,
        3,
        4,
        3,
        44,
        8,
        3,
        11,
        3,
        12,
        3,
        45,
        3,
        3,
        48,
        8,
        3,
        1,
        4,
        4,
        4,
        51,
        8,
        4,
        11,
        4,
        12,
        4,
        52,
        1,
        4,
        1,
        4,
        4,
        4,
        57,
        8,
        4,
        11,
        4,
        12,
        4,
        58,
        1,
        5,
        1,
        5,
        1,
        5,
        3,
        5,
        64,
        8,
        5,
        1,
        5,
        5,
        5,
        67,
        8,
        5,
        10,
        5,
        12,
        5,
        70,
        9,
        5,
        1,
        6,
        1,
        6,
        1,
        7,
        1,
        7,
        1,
        7,
        1,
        7,
        1,
        8,
        1,
        8,
        1,
        8,
        1,
        9,
        1,
        9,
        1,
        10,
        3,
        10,
        84,
        8,
        10,
        1,
        10,
        4,
        10,
        87,
        8,
        10,
        11,
        10,
        12,
        10,
        88,
        1,
        11,
        4,
        11,
        92,
        8,
        11,
        11,
        11,
        12,
        11,
        93,
        0,
        0,
        12,
        1,
        1,
        3,
        2,
        5,
        3,
        7,
        4,
        9,
        5,
        11,
        6,
        13,
        7,
        15,
        8,
        17,
        9,
        19,
        10,
        21,
        11,
        23,
        12,
        1,
        0,
        6,
        4,
        0,
        32,
        32,
        48,
        57,
        65,
        90,
        97,
        122,
        1,
        0,
        65,
        71,
        1,
        0,
        48,
        57,
        12,
        0,
        43,
        43,
        45,
        45,
        49,
        49,
        53,
        55,
        57,
        57,
        94,
        94,
        97,
        97,
        100,
        100,
        109,
        109,
        111,
        111,
        115,
        115,
        248,
        248,
        13,
        0,
        35,
        35,
        43,
        45,
        48,
        57,
        94,
        94,
        97,
        98,
        100,
        100,
        103,
        103,
        105,
        106,
        109,
        109,
        111,
        111,
        115,
        115,
        117,
        117,
        248,
        248,
        2,
        0,
        9,
        9,
        32,
        32,
        105,
        0,
        1,
        1,
        0,
        0,
        0,
        0,
        3,
        1,
        0,
        0,
        0,
        0,
        5,
        1,
        0,
        0,
        0,
        0,
        7,
        1,
        0,
        0,
        0,
        0,
        9,
        1,
        0,
        0,
        0,
        0,
        11,
        1,
        0,
        0,
        0,
        0,
        13,
        1,
        0,
        0,
        0,
        0,
        15,
        1,
        0,
        0,
        0,
        0,
        17,
        1,
        0,
        0,
        0,
        0,
        19,
        1,
        0,
        0,
        0,
        0,
        21,
        1,
        0,
        0,
        0,
        0,
        23,
        1,
        0,
        0,
        0,
        1,
        25,
        1,
        0,
        0,
        0,
        3,
        27,
        1,
        0,
        0,
        0,
        5,
        35,
        1,
        0,
        0,
        0,
        7,
        47,
        1,
        0,
        0,
        0,
        9,
        50,
        1,
        0,
        0,
        0,
        11,
        63,
        1,
        0,
        0,
        0,
        13,
        71,
        1,
        0,
        0,
        0,
        15,
        73,
        1,
        0,
        0,
        0,
        17,
        77,
        1,
        0,
        0,
        0,
        19,
        80,
        1,
        0,
        0,
        0,
        21,
        86,
        1,
        0,
        0,
        0,
        23,
        91,
        1,
        0,
        0,
        0,
        25,
        26,
        5,
        37,
        0,
        0,
        26,
        2,
        1,
        0,
        0,
        0,
        27,
        29,
        5,
        91,
        0,
        0,
        28,
        30,
        7,
        0,
        0,
        0,
        29,
        28,
        1,
        0,
        0,
        0,
        30,
        31,
        1,
        0,
        0,
        0,
        31,
        29,
        1,
        0,
        0,
        0,
        31,
        32,
        1,
        0,
        0,
        0,
        32,
        33,
        1,
        0,
        0,
        0,
        33,
        34,
        5,
        93,
        0,
        0,
        34,
        4,
        1,
        0,
        0,
        0,
        35,
        36,
        7,
        1,
        0,
        0,
        36,
        6,
        1,
        0,
        0,
        0,
        37,
        39,
        5,
        98,
        0,
        0,
        38,
        37,
        1,
        0,
        0,
        0,
        39,
        40,
        1,
        0,
        0,
        0,
        40,
        38,
        1,
        0,
        0,
        0,
        40,
        41,
        1,
        0,
        0,
        0,
        41,
        48,
        1,
        0,
        0,
        0,
        42,
        44,
        5,
        35,
        0,
        0,
        43,
        42,
        1,
        0,
        0,
        0,
        44,
        45,
        1,
        0,
        0,
        0,
        45,
        43,
        1,
        0,
        0,
        0,
        45,
        46,
        1,
        0,
        0,
        0,
        46,
        48,
        1,
        0,
        0,
        0,
        47,
        38,
        1,
        0,
        0,
        0,
        47,
        43,
        1,
        0,
        0,
        0,
        48,
        8,
        1,
        0,
        0,
        0,
        49,
        51,
        7,
        2,
        0,
        0,
        50,
        49,
        1,
        0,
        0,
        0,
        51,
        52,
        1,
        0,
        0,
        0,
        52,
        50,
        1,
        0,
        0,
        0,
        52,
        53,
        1,
        0,
        0,
        0,
        53,
        54,
        1,
        0,
        0,
        0,
        54,
        56,
        5,
        47,
        0,
        0,
        55,
        57,
        7,
        2,
        0,
        0,
        56,
        55,
        1,
        0,
        0,
        0,
        57,
        58,
        1,
        0,
        0,
        0,
        58,
        56,
        1,
        0,
        0,
        0,
        58,
        59,
        1,
        0,
        0,
        0,
        59,
        10,
        1,
        0,
        0,
        0,
        60,
        64,
        7,
        3,
        0,
        0,
        61,
        62,
        5,
        35,
        0,
        0,
        62,
        64,
        5,
        53,
        0,
        0,
        63,
        60,
        1,
        0,
        0,
        0,
        63,
        61,
        1,
        0,
        0,
        0,
        64,
        68,
        1,
        0,
        0,
        0,
        65,
        67,
        7,
        4,
        0,
        0,
        66,
        65,
        1,
        0,
        0,
        0,
        67,
        70,
        1,
        0,
        0,
        0,
        68,
        66,
        1,
        0,
        0,
        0,
        68,
        69,
        1,
        0,
        0,
        0,
        69,
        12,
        1,
        0,
        0,
        0,
        70,
        68,
        1,
        0,
        0,
        0,
        71,
        72,
        5,
        47,
        0,
        0,
        72,
        14,
        1,
        0,
        0,
        0,
        73,
        74,
        5,
        58,
        0,
        0,
        74,
        75,
        5,
        124,
        0,
        0,
        75,
        76,
        5,
        124,
        0,
        0,
        76,
        16,
        1,
        0,
        0,
        0,
        77,
        78,
        5,
        124,
        0,
        0,
        78,
        79,
        5,
        124,
        0,
        0,
        79,
        18,
        1,
        0,
        0,
        0,
        80,
        81,
        5,
        124,
        0,
        0,
        81,
        20,
        1,
        0,
        0,
        0,
        82,
        84,
        5,
        13,
        0,
        0,
        83,
        82,
        1,
        0,
        0,
        0,
        83,
        84,
        1,
        0,
        0,
        0,
        84,
        85,
        1,
        0,
        0,
        0,
        85,
        87,
        5,
        10,
        0,
        0,
        86,
        83,
        1,
        0,
        0,
        0,
        87,
        88,
        1,
        0,
        0,
        0,
        88,
        86,
        1,
        0,
        0,
        0,
        88,
        89,
        1,
        0,
        0,
        0,
        89,
        22,
        1,
        0,
        0,
        0,
        90,
        92,
        7,
        5,
        0,
        0,
        91,
        90,
        1,
        0,
        0,
        0,
        92,
        93,
        1,
        0,
        0,
        0,
        93,
        91,
        1,
        0,
        0,
        0,
        93,
        94,
        1,
        0,
        0,
        0,
        94,
        24,
        1,
        0,
        0,
        0,
        12,
        0,
        31,
        40,
        45,
        47,
        52,
        58,
        63,
        68,
        83,
        88,
        93,
        0,
    ]


class ChordsLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [DFA(ds, i) for i, ds in enumerate(atn.decisionToState)]

    MEASURE_REPEAT = 1
    REHEARSAL = 2
    NOTE = 3
    ALTERATION = 4
    TIME_SIGNATURE = 5
    SUFFIX = 6
    SLASH = 7
    REPEAT_BARLINE = 8
    DOUBLE_BARLINE = 9
    BARLINE = 10
    NEWLINE = 11
    WHITESPACE = 12

    channelNames = ["DEFAULT_TOKEN_CHANNEL", "HIDDEN"]

    modeNames = ["DEFAULT_MODE"]

    literalNames = ["<INVALID>", "'%'", "'/'", "':||'", "'||'", "'|'"]

    symbolicNames = [
        "<INVALID>",
        "MEASURE_REPEAT",
        "REHEARSAL",
        "NOTE",
        "ALTERATION",
        "TIME_SIGNATURE",
        "SUFFIX",
        "SLASH",
        "REPEAT_BARLINE",
        "DOUBLE_BARLINE",
        "BARLINE",
        "NEWLINE",
        "WHITESPACE",
    ]

    ruleNames = [
        "MEASURE_REPEAT",
        "REHEARSAL",
        "NOTE",
        "ALTERATION",
        "TIME_SIGNATURE",
        "SUFFIX",
        "SLASH",
        "REPEAT_BARLINE",
        "DOUBLE_BARLINE",
        "BARLINE",
        "NEWLINE",
        "WHITESPACE",
    ]

    grammarFileName = "Chords.g4"

    def __init__(self, input=None, output: TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = LexerATNSimulator(
            self, self.atn, self.decisionsToDFA, PredictionContextCache()
        )
        self._actions = None
        self._predicates = None
