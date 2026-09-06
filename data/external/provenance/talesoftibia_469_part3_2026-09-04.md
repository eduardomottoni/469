# Tales of Tibia — 469, Part 3: "Descent into Madness"

- **URL:** https://article.talesoftibia.com/469/3
- **Retrieved:** 2026-09-04
- **Author:** "Simula" / s2ward

## Archiving note

Structured reconstruction, not a verbatim mirror (see part 1 file). This is the part the repository
most needs, because it contains the **open Drefia coordinate leads** that the repo's PR never
considered. Those are recorded here concretely.

## THE DREFIA LEAD (recorded in full detail)

The article opens part 3 by proposing that "tridiag" in the Demona formula set means a **tridiagonal
matrix**, and gives an illustrative 4×4 grid:

```
[1, 1, 1, 1]
[1, 3, 6, 1]
[1, 1, 4, 1]
[4, 6, 1, 1]
```

It then reports the concrete find:

> "When following the magic web, I stumbled upon these formulae in **Drefia** that lands on a
> 'gate' — In a great stoke of coincidence, these were brought to my attention by **Besd Tesd** as I
> was analyzing pieces of the map-puzzle."

**Three formulae are found in Drefia**, rendered in the article as LaTeX (with the author's own typo
`pmatric`/`pmatrix` preserved):

1. `\frac{1}{2} ab` — read as the area of a triangle given two sides and the included angle:
   `Area = (1/2) * a * b * sin(theta)`
2. `A_G\cdot h` — read as the area of a parallelogram given base, height and included angle:
   `Area = A_G * h = b * h * sin(gamma)`
3. `\vec{P} = \begin{pmatrix}p_1\\p_2\end{pmatrix}` — a 2-component column vector

The author's reading of the three together:
- formula 1 gives an **area of a triangle** (matching the "tridiag" book name, since tridiagonal
  matrices are "commonly used to create triangles");
- formula 2's **dot product** matches the honeminas `(4,3,1,5,3).(3,4,7,8,4)` construction — he
  computes this dot product as **88** in-line (note: the correct value is 83; see the repo's own
  `experiments/provenance/HONEMINAS.md`), and notes the dot product is used for parallelogram area;
- formula 3 gives **points in 2-D space**, matching the Dianscher coordinates.

Cross-referenced to the Demona note that "g stands for gate, g[a_,x_] for the coordinates of the gate
in the 2-dimensional-area and e for the strengh of the magic energy that flows into this gate."

### What is still open in this lead

- The **exact in-game location in Drefia** is given only as "lands on a 'gate'" on the author's
  reconstructed magic web. No coordinates, no room name, no screenshot caption is transcribed in the
  page text.
- The **source is second-hand**: credited to another player, **Besd Tesd**, not found by the author.
- The formulae are **not connected to 469 digits anywhere in the article**. They are used solely to
  justify reading the Dianscher coordinates as three points forming a triangle. No decode is
  attempted, no digit stream is derived, no verification is offered.
- The article never returns to Drefia after this section.

**This is the single concrete unverified primary-source item in the whole series.** Anyone continuing
should establish, from the Tibia wiki or in-game: (a) whether these three LaTeX-rendered formulae
actually exist as Drefia in-game content, (b) their exact location, and (c) whether the LaTeX
rendering is the article author's transcription of plain in-game book text or of images/decorations.

## Rest of part 3

**§ Re-deriving the Dianscher coordinates.** The author states the previous fit failed and that he
spent "some odd 6 hours" and about 20 iterations before a system cohered. His fix: the ancient map
"looks creased in the upper right corner, so I mirrored it". Mirrored, it extends to Z and **both
coordinate sets form a perfect triangle in the same area**.

His refined reading of `p3,q9,0o and p3,23,0t`:
- `P3` — first coordinate is x, three steps east from (P,P), matching the vector formula;
- `Q9` — the y direction, nine steps north of (Q,Q); x-then-y ordering per formula 3;
- `0t` — possibly theta or gamma; the number is on the left side, as in `0o = (O,O)`; he notes the
  angle between `0o` and `0t` is 45 degrees but is explicitly unsure whether these are angles or
  points;
- `23` — read as (23,23), counted numerically rather than alphabetically.

He notes that "Coordinates for the area around Dianscher" shares an author (Mathemicus) with the
honeminas book, treats that as confirmation, and speculates "Maybe the coordinates could be used
somehow to even decipher 469" — but does not attempt it.

**§ Building the full magic web.** He argues Tibia is round (upper Zao close to Banuta), quoting a
Zao book about the reign of Tzuzak VII: a plague, conspiracies, and saviours who "came from the
north... On mighty wings". Then a long picture-caption list of claimed web nodes: Queen of the
Banshees, Senja castle, the mage tower in Hellgate, a fairy ring, a dream catcher, the raging mage,
Banuta, Vengoth, Rainn castle, a menhir circle, the Ab'dendriel spawnpoint, the circle of life, the
Jakundaf desert dungeon entrance, Brightsword quest's tower, the cursed crystal, the scrying orb of
elvenbane, below the Ab'dendriel temple, the snakemen tower above Dago's crypt, the Yalahar
magicians' quarter, serpent spawns below the cult, and Roshamuul.

**§ Ley lines.** Quotes Milos: most Tibian cultures know of "straight lines that run across the
landscape, connecting both, natural and sacred sites", called fairy paths or spirit lines, and in Zao
"dragon lines"; markers include mounds, cairns, standing stones, stone circles, ponds, wells, shrines,
temples and cross-roads. The author treats this as in-game confirmation of the web.

**§ The nine gates.** Claims that with the Thais dream machine at the centre, **eight gates sit at
equal distances**, all nine related to death, containing beds, towers, teleporters, bonelords and
stone circles. Notes a second copy of the same map in Zathroth's secret library scribbled with Zs.

**§ The Kilmaresh reuse (the article's strongest structural claim).** The author reports finding the
**same map** in the ancient ruins of Fafnar in Kilmaresh, where the Explorer's Society representative
calls it a map of the Kilmaresh area. Applying the same overlay system there produces an X at which
an **unannounced raid** occurs: sometimes a crashed pirate ship, sometimes only pirates, sometimes
nothing, with a chest of gold present when the ship has crashed. He reconciles the Sunken City
anchoring by reading "15th latitude of Fafnar" as `A..B..C..D..Fafnar` = positions 11–15, i.e. Fafnar
= 15, and argues 90 vs 45 degrees are both "legal" on a compass. He argues the pirates would come
from the north-east having just visited Port Hope, and that this is the only safe anchorage hidden
from ogres and minotaurs.

He notes that beneath this X lies the **opticompass from the Mysterious Ornate Chest quest**, and
argues the reuse of a 2001 map for 2015 Kilmaresh content strengthens rather than weakens the case:
"469 has been unexplained for some 22~ years since it was added, maybe it was too difficult?"

His own summary of what he claims to hold at this point: one map that was originally a unique quest
reward from Demona; a map-on-map placement method that works in two different Tibian regions; at
least five hints that the map matters, in closely related places; a reasonable system; and two
different places where the system produces a result.

**§ Serpentine Tower and Draconia.** Draconia is claimed as a gate containing a bonelord shield and a
star amulet, echoing Demona. Serpentine Tower is presented as an astrology and magic centre. Quoted
research papers: 56-09 A (three mages lost in a controlled demon summoning; three graves are present
in-game), 33-16 H (flawed 'stoneskin' spell, focusable into an amulet — matched to the quest's stone
skin amulet reward), 02-56 A (the 'cat-eye' spell, reproducing an elder-race spell for seeing in the
dark, with a "hurtful effect of sudden light"), 74-08 G ('find person' improvements), 44-33 C (a
divination spell specifying the gender of an unborn child — which he reads against the Banuta ghost
priest's "egg stealers" dialogue as evidence of dream-shaping unborn life), and 77-04 D (the 'move
earth' spell entering field testing, with the writer envying "the priests for the elemental powers
they are wielding").

**§ The snake-eyes chant.** From a forbidden temple on a claimed web gate, a chant about snake eyes,
gold and old lizards, salamanders of fire and ire, and a "snake-eyes lord". The author fuses this with
the cat-eye research paper and the Mad Mage library's "Ten ways to use the spell 'invisibility'" to
propose that the cat-eye spell is really a **snake-eye spell**, one of ten combinations of *utana vid*
with a light spell, making eyes glow and burn.

**§ Origins chain.** Quotes an Ancient Priest by Horestis on shamans rising to power, the chieftain
marrying into priest families to form the first dynasty, and sinister secrets "stolen and traded from
the lizards" from "the envious and reclusive scarab spirit", breaking the old pact. Quotes *Suns and
Stars, Part I* on stars and suns influencing the flow of magic and constraining when rituals can be
performed. Quotes Teruvax Tristam's UMO (unknown magical objects) book — abductions since before
mankind, UMOs as floating colourful lights with a paralyse-like effect, described as entities rather
than vehicles, ending "Always look up to the sky when it's dark!" The author reads UMO colours as
bonelord eye-elements.

**§ Ztiss and the many-eyed horrors.** The load-bearing quote for the article's origin story, from
Ztiss during The New Frontier: Zao united the tribes, tamed animals, taught seeding and harvesting,
"ztole ze zecret of zteel from ze evil lordz of ze deep and flooded zeir cavez to drown zem", and
**"fought ze many-eyed horrorz and enzlaved zem. When zey finally rebelled, Zao had learnt enough of
zeir magic to crush zem"** — then ascended to the sky to watch over his people from the clouds. The
author reads this as the origin of 469: someone enslaved the bonelords and learned their magic. He
notes the ascension parallels his Durin thesis.

**§ Gods and Kirok.** Old tribe gods read as compressed forms: Fasuon = Fafnar + Suon; Uzroth = Uman
Zathroth; Pandor the Warrior ≈ Banor; Krunus ≈ Crunor; "kiroki" mentioned by barbarians ≈ Kirok.
Quotes Genesis I on Fardos and Uman Zathroth, an Isle of the Kings book on "the three that were four"
and the essence of mind being stolen, the Excalibug prophecy ("when the one-eyed king dies in fire"),
and the Age of Chaos text on **Kirok the Mad** — born from a shard broken off during the failed
attempt to separate the double god, patron of science and research, famous for a twisted sense of
humour, "He adores bad taste and ingenious pranks". The author proposes Kirok the Mad = the Mad Mage,
which would explain his ubiquity and two-god power. Notes the Elementalist outfit is assembled from
Mad Mage and Raging Mage parts.

**§ Language teasers for later parts.** The First Dragon mentions possibly translating his memoirs
into orcish "or even one in bonelord language" and that "it's a funny story how I learnt the bonelord
language", saved for a possible part two of his memoirs. Also *Notes about gharonk language* (a town
whose language has "a simplified but quite usual grammar", with a recorded sentence "Nag narat umog
yargoth!" and a word table), and an ancient inscription under Thais readable only in fragments
("The First Dragon..."). Part 3 ends by teasing Spectulus's room, "4 'eyes' and a cardinal wheel",
described as a "BONELORD.. coordinating machine".
