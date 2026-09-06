# The Honeminas formula: what it actually is

*Direct check, not speculation. The Tibia Fandom wiki is blocked by this
session's egress proxy, so book texts here come from search-result extracts;
they are consistent across several independent queries but are marked as
second-hand where it matters.*

## Short answer

It is a piece of **flavour text in a warlock's library about teleportation**,
one of at least six near-identical "formula" books in the same room, written in
broken pseudo-Mathematica. In-game lore states it is **unfinished**. It has no
established connection to 469 at all — the connection appears to originate in
this repository's own README, which also mis-transcribes its numbers.

## 1. What the book is, in-universe

Honeminas was a **Warlock of Demona** developing a formula to explain how the
**Magic Web** (Tibia's teleportation/ley-line system) had been designed by the
gods. He was killed by two intruders before finishing. The surviving fragment
was written down by **Mathemicus**, another warlock continuing the work.

So the book is canonically an *incomplete formula by a dead man, transcribed by
someone else*. Its incompleteness is the stated premise, not a puzzle.

## 2. It is not unique — it is one of a set

Demona Library holds a whole family of these, all "based on the honeminas
formula", all in the same style:

| book | author | formula text (second-hand) |
|---|---|---|
| The Honeminas Formula | Mathemicus, after Honeminas | `g[a_,x_] := a g[3,2] + (4,3,1,5,3).(3,4,7,8,4)` ; `e=3m*2g+3p` |
| The Tridiag Formula | Donazia | `a=3er*8g+99k` ; `g[a_,l_] :=e*g[1,1]+9g*3a` ; `h:=3pe-34u` |
| The Donina Formula I | Donina | `ft:=E[3,2,3]*fd(3.2),as->20` ; `io=g[i,u]+2` |
| The Donina Formula II | Donina | `ds(%)="[tr3+12\32p-q]"` ; `gh/3u+32=<%sd>` |
| The Janias Formulas | — | — |
| The Zonoa Formulas | — | — |

The Tridiag book is the tell. It repeats Honeminas's exact structural quirks:
`g[a_,l_] := ... g[1,1] ...` is the same self-recursive definition with the same
**unused second parameter**. One person wrote several of these to the same
template. The Donina books add `->` (Mathematica's `Rule`) and `%` (Mathematica's
`Out[]` shorthand), confirming the register: someone imitating a Mathematica
notebook.

## 3. The syntax does not work

| element | verdict |
|---|---|
| `g[a_,x_] :=` | valid Wolfram `SetDelayed` with pattern variables |
| `x_` | **declared and never used** on the right-hand side |
| `a g[3,2]` on the RHS | **self-recursive**: `g[3,2]` re-matches `g[a_,x_]`, so evaluating it recurses until `$RecursionLimit` |
| `(4,3,1,5,3).(3,4,7,8,4)` | **syntax error**: a Wolfram list needs braces, `{4,3,1,5,3}.{3,4,7,8,4}` |
| `e=3m*2g+3p` | `Set` not `SetDelayed`; `g` is a scalar here but a function above |
| the accompanying note | calls `g[a_,x_]` "the coordinates of the gate" — i.e. a point, while the syntax defines a function |

It would not parse, and if the list syntax were repaired it would not terminate.
This is pastiche of the look of a computer-algebra session, by someone who had
seen one. That is a real dating fingerprint — Mathematica was in university
computer labs in the late 1990s, and CipSoft's founders were University of
Regensburg students, one with a physics degree — but it is a fingerprint of
*flavour text*, not of a working system.

## 4. The numbers, and a transcription error in this repo

Read as vectors and taken at face value:

    {4,3,1,5,3} . {3,4,7,8,4} = 12 + 12 + 7 + 40 + 12 = 83

Concatenating the two vectors gives **43153** and **34784**.

README.md builds its "469 comes in pairs, left larger than right" argument on
this book, quoting the pair as `43153 / 34783` in one place and `(43151 34783)`
in another. Both right-hand values are wrong, and the two passages disagree with
each other. Checked against `books.json`:

| string | in the formula? | occurrences in the 70 books |
|---|---|---|
| `43153` | yes (vector 1) | **0** |
| `34784` | yes (vector 2) | **0** |
| `43151` | no — README typo | 14 |
| `34783` | no — README typo | 5 |

**Neither number from the formula appears anywhere in the corpus.** The matches
the README reports are matches for the corrupted versions. The observation that
"these numbers appear in the books" is an artefact of the typo.

## 5. Is Honeminas even a bonelord?

README.md states "Warlocks of Demona had a bonelord called 'honeminas'". Every
source found describes Honeminas as **a Warlock of Demona**, in a warlock
dungeon, whose work was continued by other warlocks (Mathemicus, Donina,
Donazia). Nothing found calls him a bonelord.

If that is right, the entire link between this book and 469 dissolves: it is a
warlock's teleportation formula, in a warlock library, in a warlock dungeon,
connected to the bonelord language only by the fact that both contain digits.

*Flagged as second-hand pending a direct read of the wiki page, which the proxy
currently blocks.*

## 6. Consequence for 469

The Honeminas formula should be removed from the 469 evidence base:

1. it is about the Magic Web, not language;
2. it is one of six sibling books, so nothing about it is singular;
3. it is canonically unfinished;
4. its notation is non-functional pastiche;
5. its author is a warlock, not a bonelord;
6. its numbers do not occur in the books, contrary to the claim made for them.

This is consistent with the statistical result: Family D's exhaustive
enumeration already found that the Honeminas dot-product family fits the
Facebook number pairs no better than random pair sets (p = 0.87).
