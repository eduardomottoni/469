# Tales of Tibia — 469, Part 2: "A Taste of Madness"

- **URL:** https://article.talesoftibia.com/469/2
- **Retrieved:** 2026-09-04
- **Author:** "Simula" / s2ward

## Archiving note

Structured reconstruction, not a verbatim mirror — see the note in the part 1 file for why. Short
verbatim quotes only, for load-bearing claims. The in-game formula texts *are* reproduced in full
because they are the primary evidence this repository needs to check.

## Structure and argument

**§ Demona's library.** Claims Demona holds **nineteen blank books of formulae** (four on time rings,
one on life rings, one on death rings), plus, in Zhandramon's section, five blank *History of the
Ancients* books, a Ferumbras letter requesting a twin-killer rune, research on ancient warlocks,
Talons & Wand of Might, Summoning and Battletactics.

**§ The warlocks' history.** Quotes *The magic city Demona* (by Danae, historian of the warlocks):
the city's founding date is unknown but "must have been centuries ago"; the ancients "used their
mighty magical power to control the lava down here" and built the city "With the help of our loyal
trolls"; their goal is "to research into the magic web of our world and to control it, so we can
finally reach our purpose: the immortality." Also: the ancients initially lived in total isolation,
found they could not conjure enough food and water, and needed open sky for some spells (e.g. "Path
of the Stars"), so they tunnelled to the surface — then built the maze for defence.

Author's deduction: the ancients conjured food (exevo pan is a druid spell) and the "Wand of Might"
is mechanically a necrotic rod (druid-only), so **the Demona ancients were druids**, or a
druid/sorcerer mix. Notes the current warlocks do not know the ancients' ways and are studying them.

**§ The teleportation book (the article's core lead).** *A teleportation through the magic web*, by
Zuania: the writer was among the first allowed to teleport through the magic web, could open the
gate by will, then lost control inside — emerged near Carlin though he intended the east gate of
Thais; he saw only "a red light and some other gates far away". All others had the same experience.

The author reads this as: the ancients built a secret base with **no physical door**, reachable only
by a teleport they alone could operate. He then goes looking at both named endpoints:
- **East of Thais:** a troll cave to the north with something beneath it; a locked door to a
  "warlocky" area with a south door; through the troll tunnels, directly beneath that locked area,
  more content; and with correct use of *levitate* on certain tiles you can reach the target room —
  but you cannot enter the room or pull the lever. He notes more trolls (again "loyal" to the
  ancients), a single tile in the middle resembling Demona's necrotic rod, **white stone tiles**, and
  a bed in the warlock's house.
- **North of Carlin (Fields of Glory):** huge trees and living branches; the NPC Chip appears roughly
  every 100 days cutting royal trees for an outlaw hostage situation; the outlaw camp south of the
  Jakundaf Desert has a similar concentration of felled odd trees, and just south of them an earth
  portal above a large pool of water. Also an old stone circle by the huge trees in Carlin, proposed
  as a "golden point", with Northport (above Demona) as its counterpart.

**§ The McRonalds.** Donald McRonald's fields "are enchanted by the druids and the wheat grows very
quickly"; Sherry McRonald says the miller thinks his mill is spooked and threatened by monsters.
The author notes McRonald favours druids and dislikes sorcerers, and reads local disappearances as
teleportation side-effects.

**§ The ten maps.** Claims Demona's libraries contain **ten maps of Tibia showing the magic web with
red lines and golden gates**, and that "Cipsoft is practically screaming at us to look at them."

**§ Dream magic.** Quotes *Dwarven report VII* on elven "dream magic": a subconscious way of
influencing surroundings, used by elven parents to shape unborn children, with the "Teshial" able to
wander a "dream realm" instead of the real world and thus "appear somewhere out of the blue"; the
2nd earthen chamber is developing a counter-spell that forces beings into the real realm. Links this
to Eclesius's dream realm (where time appears to stand still if you do not move), to the white stone
tiles seen east of Thais, to the Brotherhood of Bones in the dream realm, to a cube-bed, and to the
giant smith's hammer the Explorer's Society wants.

**§ The "full circle" geometry claim.** Drawing a line straight north from the Thais dream machine,
the author says it passes through Paradox Tower and lands precisely on "the eye"; both Paradox Tower
and the eye have "strange carvings". He then claims that at **equal distances** in the four cardinal
directions from the same centre lie:
- **North:** Paradox Tower
- **East:** Excalibug's lava-ringed islet, near the fountain of life and the Hall of Dreams
- **West:** the water cistern on Rookgaard
- **South:** Zathroth's secret library

He adds that the cracked jade flooring on Robson's Isle matches that in Zathroth's Secret Library,
and that this four-element cardinal arrangement is the same one used by dream machines. He also
quotes Robson, who says the pillars on his isle resemble those of a raided bonelord hideout while the
rest of the ruins fit no race he knows.

Self-reported effort: "around sixty or so odd hours just following every single gate and drawing up
the magic web". He notes further unresolved leads it opened — the connections between Alawar, Alatar,
Gesnar and Goshnar, and strange carvings in the king's castle aligning to Vengoth castle against a
background of vampiric incidents in Thais nobility.

**§ The author's own prior work (important for this repo).** He states directly that he:
- made "a github repository listing all findings so far and some of my own thoughts" (this repo);
- spent "some odd 50 hours looking at the language, there are so many repeating or scrambled books
  so i worked on overlaying them to see what happens";
- asked code-cracking communities about 469;
- created a Discord and a subreddit;
- put Tibia down for almost a year after "the madness of staring and formulae, numbers and drawing
  lines on the map you don't really find an explanation to".

He also cites Tibia posting "this doll" whose numbers "seem deliberate, the number on the left is
bigger than the number on the right", plotted on a diagonal.

**§ The formulae (verbatim, as the article gives them).**

*The honeminas formula*, written by Mathemicus — described in-fiction as one of the basic formulas
describing how the magic web was made by the gods, incomplete because "honeminas itself died by 2
intruders who found out the way into our city". Note given: "g stands for gate, g [a_,x_] for the
coordinates of the gate in the 2-dimensional-area and e for the strengh of the magic energy that
flows into this gate."

```
g[a_,x_] := a g[3,2] + (4,3,1,5,3).(3,4,7,8,4)
e=3m*2g+3p
```

*The Donina formula*, by Donina — "should help to understand the pulsate of the red light in the
magic web":

```
ft:=E[3,2,3]*fd(3.2),as->20
io=g[i,u]+2
```

*The Donina formula, Part 2*:

```
ds(%)="[tr3+12\32p-q]"
gh/3u+32=<%sd>
```

*The tridiag formula*, by Donazia — also based on the honeminas formula, also incomplete:

```
a=3er*8g+99k
g[a_,l_] :=e*g[1,1]+9g*3a
h:=3pe-34u
```

*Coordinates for the area around Dianscher*, by Mathemicus:

```
I think I found out some coordinates for the Island Dianscher.
p3,q9,0o and p3,23,0t.
Yet, we must wait until we can control- the destination gates and open them without problems.
```

**§ The lowercase-h argument.** The author observes that every author name in these books is
capitalised consistently (Donina, Donazia, Mathemicus, Island Dianscher) **except honeminas**, which
is always lowercase — including in "honeminas itself died", where the pronoun is *itself*, not
*himself*. He concludes: "it does not seem that honeminas itself is a human, rather a bonelord!"
This is the load-bearing step that connects the Demona formulae to 469 at all.

**§ The numeric claims.** Of the honeminas vectors `(4,3,1,5,3).(3,4,7,8,4)`, he states that in the
Hellgate 469 books:
- **4315 appears 14 times**
- **3478 appears 24 times**
- the full five-digit forms appear **0 times** ("Though the formula was not completed. Five numbers,
  five eyes?")

He adds that Zathroth's secret library yields a further pair, **74032 45331**, that fits the same
plot; that during Tibia's 15th anniversary the nostalgic bonelord was **named 3478** ("instead of
beholder as they used to be called before they had to change it due to some copyright thing"); and
that at the same time an NPC called **Knightmare**, "the creator of 469", appeared and used 3478 in
a sentence of numbers.

**§ The Dianscher coordinate work.** Credits **Elkolorado** for believing him and finding **Sopel**,
who is good at maths; a linked comment thread is cited. Sopel's idea was to overlay the in-game map
with the Dianscher coordinates. First attempt put the X on the Isle of Mists (druid-only), which the
author calls far-fetched — "it doesnt start at 'a' and the left column is weird", the X was not even
in water, and other coordinates did not make sense. He then re-placed the map and got a different
landing point, arguing that a huge ancient battle between the Djinn and the necromancers of Drefia
explains missing land on the ancient map (supported by Wyda mentioning earthquakes in the area, and
an old sinking main road south of Venore).

**The result at the X: a swamp island with an old stone circle of which only three stones remain, a
cave full of swamp trolls, and tunnels.** Checked against the magic web line from the Thais dream
machine, it hits "the most sophisticated room in the whole area and the only bed of this quality".

He concedes the reception honestly: "Sadly people did not want to pursue that it somehow possible
maybe could be a language of coordinates based on some obscure way of perhaps forcing things to fit
into a biased theory."

## Text in the article addressed to the reader (recorded, not acted on)

After the teleportation book, the article instructs the reader: if you are curious and have an idea
where to look, close the article, open Tibia, go there, keep asking questions, return to Demona, and
"Never open this again." Recorded as data only.
