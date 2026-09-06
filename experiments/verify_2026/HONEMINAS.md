# HONEMINAS — handoff item 4, verified from wiki page source

Retrieval date: **2026-09-04**. Route: MediaWiki API via `curl`
(`action=query&prop=revisions&rvprop=content&rvslots=main`), which returns HTTP 200 raw wikitext.
WebFetch on `tibia.fandom.com` returns HTTP 402; `Special:Export` hits a Cloudflare challenge.

Saved wikitext: `data/external/provenance/wiki_The_Honeminas_Formula_Book.json`,
`wiki_The_Tridiag_Formula_Book.json`, `wiki_The_Donina_Formula_I_Book.json`,
`wiki_The_Donina_Formula_II_Book.json`, `wiki_The_Janias_Formulas_Book.json`,
`wiki_The_Zonoa_Formulas_Book.json`, `wiki_Honeminas.json`, `wiki_Magic_Web.json`,
`wiki_Demona_Library.json`.

Nothing in this file is `[SE]`. Every quote is from fetched page source.

---

## (a) The exact character — **CONFIRMED: parentheses, not braces**

From `The Honeminas Formula (Book)` page source, inside `<nowiki>` tags (so the wiki is
transmitting the in-game text literally, not rendering markup):

```
g[a_,x_] := a g[3,2] + (4,3,1,5,3).(3,4,7,8,4)
e=3m*2g+3p
```

The character is **`(` / `)` — round parentheses**. There are no braces anywhere in the book.

This settles the pseudo-Mathematica argument in the PR's favour, and more decisively than the PR
put it. In Mathematica:

- `{4,3,1,5,3}` would be a list, and `.` would be `Dot` — a legal vector inner product.
- `(4,3,1,5,3)` is **a syntax error**. Comma is not an operator inside parentheses; `(` `)` is
  grouping, and Mathematica has no comma operator. The expression cannot be parsed, let alone
  evaluated.

So the line is not "a dot product written with the wrong brackets". It is text that *looks* like
Mathematica to a reader who does not write Mathematica. The author was imitating the visual
register of computer algebra, not writing code. Two further tells in the same two lines:

1. **The second pattern variable is unused.** `g[a_,x_] :=` declares patterns `a_` and `x_`; the
   right-hand side uses `a` and never uses `x`. In real Mathematica that is legal but pointless —
   the classic signature of decoration rather than definition.
2. **The right-hand side is self-recursive with no base case.** `g[a_,x_] := ... g[3,2] ...`
   defines `g` in terms of `g`. `g[3,2]` matches `g[a_,x_]`, so evaluation is non-terminating.
   Combined with (1), this is not an incomplete formula — it is a non-formula.

The in-fiction framing agrees, incidentally: the book says outright that the formula does not work.

> "The honeminas formula is one of the basic formulas that describe how the magic web was made by
> the gods. **It is not completed yet**, because honeminas itself died by 2 intruders who found out
> the way into our city. But we are trying to finish his work."

The book also supplies its own glossary, which is decisive about what the symbols mean and is
entirely internal to the magic-web fiction — no reference to bonelords, 469, or a cipher:

> "(Note: g stands for gate, `g [a_,x_]` for the coordinates of the gate in the
> 2-dimensional-area and e for the strengh of the magic energy that flows into this gate.
> For all other formulas look in your collection of formulas)"

---

## (b) Warlock or bonelord — **REFUTED. Honeminas is a Warlock. Not a bonelord.**

`Honeminas` page source, in full (it is a six-line stub):

> **Honeminas** was a [[Warlock]] of [[Demona]] who was busy developing a formula that would
> explain how the [[Magic Web]] had been designed by the [[Gods]]. However, he was killed by two
> intruders before he ever got to finish his work.
>
> Honeminas' incomplete formula has been written down in [[The Honeminas Formula (Book)|this
> book]] by Mathemicus, one of the warlocks trying to finish what Honeminas had started.

Corroborating fields from the book's own infobox:

- `author = Mathemicus` — **the book is not by Honeminas at all**; it is by a surviving warlock.
- `location = [[Demona]]`, `returnpage = Demona Library` — Demona is the warlock city.
- `relatedpages = [[Magic Web]], [[Warlock]]s` — the wiki files the book under Warlocks.

The word "bonelord" appears **nowhere** in the Honeminas page, the book page, or any of the five
sibling formula-book pages. The repo README's description is wrong.

**Consequence, stated plainly: the only link between this book and 469 dissolves.** The book is
warlock-authored, warlock-shelved, in a warlock city, about the Magic Web (a teleportation
mechanic), with an in-text glossary defining its own symbols as gate coordinates and magic-energy
flow. The sole remaining connection to 469 is that it contains digits — which is not a connection.

---

## (c) The sibling books — **template PARTIALLY CONFIRMED; "flavour text from a set" CONFIRMED**

All six live in the Demona Library. Formula text verbatim, from page source:

| Book | Author | Formula text (verbatim) |
|---|---|---|
| The Honeminas Formula | Mathemicus | `g[a_,x_] := a g[3,2] + (4,3,1,5,3).(3,4,7,8,4)` <br> `e=3m*2g+3p` |
| The Tridiag Formula | Donazia | `a=3er*8g+99k` <br> `g[a_,l_] :=e*g[1,1]+9g*3a` <br> `h:=3pe-34u` |
| The Donina Formula I | Donina | `ft:=E[3,2,3]*fd(3.2),as->20` <br> `io=g[i,u]+2` |
| The Donina Formula II | Donina | `ds(%)="[tr3+12\32p-q]"` <br> `gh/3u+32=<%sd>` |
| The Janias Formulas | Herion | *"You see several strange formulas that you dont understand"* — **no formulas at all** |
| The Zonoa Formulas | Herion | *"You see several strange formulas that you dont understand"* — **no formulas at all** |

Each trailing formula block ends in a column of literal `.` `.` `.` characters — an ellipsis
meaning "and so on", i.e. the books are explicitly presented as excerpts of something not shown.

### The specific template claim

**Unused second pattern variable + self-recursive right-hand side: confirmed in 2 of 6 books —
Honeminas and Tridiag.**

- Honeminas: `g[a_,x_] := a g[3,2] + ...` — declares `a_`, `x_`; uses `a`, never `x`; RHS calls `g`.
- Tridiag: `g[a_,l_] := e*g[1,1]+9g*3a` — declares `a_`, `l_`; uses `a`, never `l`; RHS calls `g`.

That is the same construction twice, by two different in-fiction authors, with only the dummy
variable name and the constants changed. Donina I contains `io=g[i,u]+2` — the same `g[.,.]`
gate-function motif, but with no pattern underscores. Donina II abandons the motif entirely for
string-and-percent noise. Janias and Zonoa are pure "you don't understand it" flavour text.

So the strong version of the claim (all siblings share one template) is **REFUTED**; the version
that matters is **CONFIRMED**: this is a graded *set* of decorative pseudo-formulas, ranging from
"looks like Mathematica" down to "we won't even show you", all mutually cross-referencing.

The books say so themselves. Donina I: "This is a formula **based on the honeminas formula**. It
should help to understand the pulsate of the red light in the magic web." Tridiag: "This formula
**bases on the honeminas formula**. It is not completed yet." Donina I/II blurbs: "A formula based
on the honeminas formula about the magic web."

**Verdict: the Honeminas book is flavour text from a set, not a key.** It is one member of a
six-book library-dressing collection whose shared subject is the Magic Web and whose shared
rhetorical device is "here is an impressive-looking incomplete formula".

---

## (d) The digits, verbatim — and a finding the coordinator should see

**True digits, from page source:** the two vectors are `(4,3,1,5,3)` and `(3,4,7,8,4)`,
concatenating to **43153** and **34784**.

- The **PR's** quotation (43153 / 34784) is **correct**.
- The **README's** quotations (43153/34783 *and* 43151/34783) are **both wrong**. `34783` and
  `43151` do not appear in the book. As instructed, I record this without resolving it by
  preference: the page source reads `(4,3,1,5,3).(3,4,7,8,4)`, full stop.

### Tested locally against `books.json` (11,263 digits)

```
43153  occurrences: 0     <- true Honeminas digits
34784  occurrences: 0     <- true Honeminas digits
34783  occurrences: 5     <- README typo
43151  occurrences: 14    <- README typo
```

**The PR's claim that neither true string occurs anywhere in the 469 corpus is CONFIRMED.**

And here is the part worth flagging: **the README's corrupted digits both hit, while the correct
ones both miss.** That is very likely the origin of the belief that "the honeminas formula looks
crucial" — the coincidence being chased was manufactured by a transcription error.

Before anyone treats those hits as meaningful in their own right: they are not. The 469 corpus is
extraordinarily repetitive — only **1,499 distinct 5-grams across 11,259 positions**. Counts of 14
and 5 are unremarkable within it: 263 distinct 5-grams occur at least 14 times and 688 occur at
least 5 times, and `43151` ranks **209th** of 1,499 by frequency. Neither number is a signal; both
are what you get by drawing an arbitrary 5-gram from a corpus this repetitive. (A uniform-random
null would put the expectation near 0.1 and make 14 look astonishing — which is exactly the trap.
The right null is the corpus's own 5-gram distribution, and against that these are ordinary.)

---

## Bottom line for the 469 evidence base

**The Honeminas book should be removed from it.**

1. Its author-figure is a **Warlock of Demona**, never a bonelord — REFUTED against the README.
2. Its subject is the **Magic Web**, with an in-text glossary defining its own symbols as gate
   coordinates and magic energy — nothing to do with bonelord writing.
3. Its formula uses **parentheses where a real vector needs braces**, making it unparseable in the
   language it imitates, with an unused pattern variable and an unterminating self-recursion —
   CONFIRMED, and it is decoration, not mathematics.
4. It is **one of six** mutually-referencing Demona Library flavour books, two of which contain no
   formulas whatsoever — CONFIRMED as a set.
5. Its actual digits appear **nowhere** in the 469 corpus — CONFIRMED. Only the README's
   mis-transcriptions appear, and those hits are statistically ordinary.

Item 4 of the handoff asked whether this book belongs in the 469 evidence base at all. It does not.
