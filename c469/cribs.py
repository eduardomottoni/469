"""Every known 469 string outside the library books.

The `in_books` flag is not decoration.  Substring search shows the cribs split
into two disjoint dialects: the strings that DO occur in the Hellgate books
(the Wrinkled Bonelord's lines, Chayenne's 2009 interview answer) are
quotations and carry no translation, while every string with a claimed English
meaning (Evil Eye, Elder Bonelord, poll answer C, Knightmare, Secret Library,
the librarian's own name 486486) occurs ZERO times in the books.

So no crib simultaneously has a translation and belongs to the library corpus.
Scorers must never mix the two dialects, and must never treat an NPC line as
ground truth for the library code.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Crib:
    text: str
    source: str
    speaker: str
    claimed_plaintext: str | None = None
    language: str | None = None
    confidence: str = "medium"   # high | medium | low
    note: str = ""


CRIBS: tuple[Crib, ...] = (
    # --- translated, but NOT present in the library books -------------------
    Crib("653768764", "tibia.fandom/The_Evil_Eye", "The Evil Eye",
         "Inferior creatures, bow before my power!", "en", "high"),
    Crib("653768764", "tibia.fandom/Elder_Bonelord", "Elder Bonelord",
         "Inferior creatures, bow before my power!", "en", "high",
         "identical string to the Evil Eye's -- same line, same digits"),
    Crib("659978 54764", "tibia.fandom/Elder_Bonelord", "Elder Bonelord",
         "Let me take a look at you!", "en", "high"),
    Crib("1", "tibia.fandom/A_Wrinkled_Bonelord", "A Wrinkled Bonelord",
         "Tibia", "en", "high", "'It's 1, not Tibia, silly.'"),
    Crib("486486", "tibia.fandom/A_Wrinkled_Bonelord", "A Wrinkled Bonelord",
         "(the librarian's own name)", "en", "high"),
    Crib("663 902073 7223 67538 467 80097", "tibia.com poll 2020-04-15", "poll answer C",
         None, None, "low",
         "NOT a crib.  This was previously recorded here as a parallel "
         "translation of answer A.  It is not: the poll's three answers are "
         "three DIFFERENT joke answers to the question, not one sentence in "
         "three encodings.  Answer A is binary for \"These aren't the words "
         "you're looking for\"; answer B is Jekhr (Deepling) for \"Nonbelievers "
         "defy the narrow path to undersea!\" -- a different sentence.  So C has "
         "no known plaintext.  Its 25-year opacity is still evidence, but it is "
         "not known-plaintext and must never be scored as such."),
    Crib("3478 67 90871 97664 3466 0 345", "tibia.fandom/Knightmare", "Knightmare NPC",
         None, None, "medium",
         "7 groups. 3478 DOES occur in the books (24x) and is a nostalgia "
         "bonelord's name; the rest of the groups do not occur at all."),
    Crib("74032 45331", "tibia.fandom/Secret_Library", "book, 2018", None, None, "medium"),
    Crib("29639 46781 9063376290 3222011 677 80322429 67538 14805394 "
         "6880326 677 63378129 337011 72683 149630 4378 453 639 578300 "
         "986372 2953639", "tibia.fandom/Avar_Tar", "Avar Tar", None, None, "low",
         "a 'poem'; Avar Tar is characterised in-game as a braggart and liar, "
         "and these groups barely occur in the books"),

    # --- present in the library books, but untranslated ----------------------
    Crib("485611800364197", "tibia.fandom/A_Wrinkled_Bonelord", "A Wrinkled Bonelord",
         None, None, "high", "occurs once in books.json -- a quotation"),
    Crib("78572611857643646724", "tibia.fandom/A_Wrinkled_Bonelord", "A Wrinkled Bonelord",
         None, None, "high", "occurs 6x in books.json -- a quotation"),
    Crib("114514519485611451908304576512282177", "PortalTibia interview 2009", "Chayenne (CipSoft)",
         None, None, "low",
         "occurs 11x in books.json -- the designer was quoting existing book "
         "text back at the interviewer, not composing new 469"),
    Crib("6612527570584", "PortalTibia interview 2009", "Chayenne (CipSoft)",
         None, None, "low", "occurs 9x in books.json -- also a quotation"),
)

#: The Honeminas formula's two digit vectors, read as a pair by the README.
HONEMINAS = ((4, 3, 1, 5, 3), (3, 4, 7, 8, 4))

#: The 2011 Facebook mirrored-image pairs.  `None` marks a digit the clay
#: figure obscures.  The README's guesses for those are the author's inference
#: and MUST NOT enter any fit -- they are held out.
FB_PAIRS_CERTAIN: tuple[tuple[int, int], ...] = (
    (713, 473), (765, 464), (706, 447), (824, 499), (975, 595),
    (652, 400), (653, 407), (737, 469), (648, 428), (818, 520),
    (985, 621), (2154, 1307), (841, 540), (689, 447), (1017, 658),
    (1280, 625), (684, 448), (694, 453),
)
FB_PAIRS_OBSCURED: tuple[tuple[int | None, int | None, str], ...] = (
    (937, None, "X30, README guesses 530"),
    (726, None, "XY1, README guesses 431"),
    (729, None, "X47, README guesses 447"),
    (565, None, "X75, README guesses 375"),
    (746, None, "X58, README guesses 458"),
    (1021, None, "?X59, README guesses 659"),
    (759, None, "X75, README guesses 475"),
    (718, None, "X38, README guesses 438"),
    (None, 471, "71X"),
    (None, 489, "75X"),
)

#: The Hellgate 4x4 skull matrix, post-2010 (CipSoft changed the skull count).
MATRIX_POST2010 = ((1, 1, 1, 1), (1, 3, 6, 1), (1, 1, 4, 1), (4, 6, 1, 1))
MATRIX_PRE2010 = ((3, 1, 6, 1), (1, 2, 1, 1), (1, 1, 3, 1), (4, 6, 1, 1))


def annotate(books) -> list[dict]:
    """Attach the in_books flag by direct substring search."""
    joined = "|".join(books)
    out = []
    for c in CRIBS:
        groups = c.text.split()
        counts = {g: joined.count(g) for g in groups}
        out.append({
            "text": c.text, "speaker": c.speaker, "confidence": c.confidence,
            "claimed_plaintext": c.claimed_plaintext,
            "group_counts": counts,
            "in_books": all(v > 0 for v in counts.values()),
            "any_in_books": any(v > 0 for v in counts.values()),
            "note": c.note,
        })
    return out
