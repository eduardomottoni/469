# Provenance research — source log

Retrieval date for everything below: **2026-09-04**.

## IMPORTANT METHODOLOGICAL CAVEAT

This session's egress proxy blocked `WebFetch` for almost every relevant domain
(`tibia.com`, `tibia.fandom.com`, `tibiawiki.com.br`, `tibiasecrets.com`,
`otland.net`, `forumarchive.xenobot.net`, `tibiaqa.com`, `cipsoft.com`,
`portaltibia.com.br`, `en.wikipedia.org`, `reference.wolfram.com`,
`web.archive.org`, `regensburg-startups.de` — all returned `EGRESS_BLOCKED`).
Only `github.com` was directly fetchable.

Therefore most web-derived statements below are **search-engine summaries of
those pages, not the pages themselves**. They are logged with the URL so a
future session with wider egress can verify. Anything not directly fetched is
marked `[VIA-SEARCH]` and must be treated as second-hand until confirmed.

---

## A. CipSoft / founders (background facts)

- `[VIA-SEARCH]` https://en.wikipedia.org/wiki/CipSoft — CipSoft GmbH founded
  June 2001 by Guido Lübke, Stephan Payer, Ulrich Schlott, Stephan Vogler;
  Tibia online since 1997; company name from the University of Regensburg
  "CIP-Pools" (Computer-Investitions-Programm/Projekt).
- `[VIA-SEARCH]` https://tibia.fandom.com/wiki/CipSoft_GmbH and
  https://www.tibia-wiki.net/wiki/Guido_L%C3%BCbke — Guido Lübke b. 1973-10-22,
  physics degree from Regensburg, "studies focused on computer technology and
  on simulation methods", product manager of Tibia.
- `[VIA-SEARCH]` https://www.cipsoft.com/en/press/press-releases/232-20-years-of-cipsoft
  (20th anniversary press release, 2021) — founding story, CIP-Pool naming.
- `[VIA-SEARCH]` https://mein-mmo.de/en/25-years-ago-4-mmo-pioneers-from-germany-had-no-money-for-a-fax-machine...,1572133/
  — 25th-anniversary long interview with managing directors Stephan Vogler and
  Benjamin Zuckerer. No 469 content surfaced in the search summary.
- `[VIA-SEARCH]` https://www.gameswirtschaft.de/wirtschaft/cipsoft-jubilaeum-25-jahre-080626/
- `[VIA-SEARCH]` http://www.regensburg-startups.de/interviews/cipsoft/ (blocked; local interview)

## B. Dev statements about the bonelord / 469 language

- **Chayenne interview, 2009-05-15**, fansite Portal Tibia (Brazil).
  https://forum.portaltibia.com.br/topic/11420-entrevista-com-chayenne/
  and https://portaltibia.com.br/pt/entrevista-com-chayenne-lider-do-time-de-content-management-da-cipsoft/
  Q: "What about the Beholder language? People are dying to understand it.
  What can you say about it?"
  A: `114514519485611451908304576512282177 :) 6612527570584 xD`
  (Quote as transcribed in this repo's own `00-timeline.md`; independently
  echoed by search results. Chayenne = then-lead game content designer.)
- **Lionet interview**, TibiaSecrets article 137, https://tibiasecrets.com/article137
  `[VIA-SEARCH]` — Lionet is a CipSoft Game Content Designer responsible for
  "some of Tibia's mysteries". Asked what he would say to a Bonelord in real
  life, with the option to answer cryptically, the reported answer was `1/0`.
  NOT VERIFIED FIRST-HAND — search summary only.
  Announcement of the interview: https://guildstats.eu/forum/viewtopic.php?f=9&t=14924
- Knightmare (CipSoft) interviews, archived:
  https://web.archive.org/web/20111105153731/http://www.tibianews.net/component/content/article/83-interviews/682-interview-with-cipsoft-knightmare.html
  https://web.archive.org/web/20060719103608/http://www.tibianews.net/section.asp?Ids=5&Id=359
  https://web.archive.org/web/20160228205824/http://www.tibialibrary.org/en/articles/stories/26-tibias-15th-anniversary-stories-told-by-knightmare
  (BLOCKED this session. A fansite claim `[VIA-SEARCH]` that "Knightmare was a
  content designer believed to have designed the 469 language" is community
  speculation, not a dev statement.)
- Community aggregations: https://github.com/s2ward/469 (fetched directly),
  https://tibiasecrets.com/article160 "The Great Tibian Cipher",
  https://forumarchive.xenobot.net/archive/index.php/t-7529.html,
  https://article.talesoftibia.com/469/1/
  None contains a CipSoft statement on decodability.

## C. In-game "Mathematica" formula books (Demona Library, 2001 content)

All texts below `[VIA-SEARCH]` from the Portuguese TibiaWiki / Fandom pages.

- The Honeminas Formula (by "Mathemicus"), Demona's Main Library I:
  `g[a_,x_] := a g[3,2] + (4,3,1,5,3).(3,4,7,8,4)` ; `e=3m*2g+3p`
  https://tibia.fandom.com/wiki/The_Honeminas_Formula_(Book)
  https://www.tibiawiki.com.br/wiki/The_Honeminas_Formula_(Book)
- The Tridiag Formula (by "Donazia", "bases on the honeminas formula"):
  `a=3er*8g+99k` ; `g[a_,l_] := e*g[1,1]+9g*3a` ; `h:=3pe-34u`
  https://www.tibiawiki.com.br/wiki/The_Tridiag_Formula_(Book)
- The Donina Formula I: `ft:=E[3,2,3]*fd(3.2),as->20` ; `io=g[i,u]+2`
  https://tibia.fandom.com/wiki/The_Donina_Formula_I_(Book)
- The Donina Formula II: `ds(%)="[tr3+12\32p-q]"` ; `gh/3u+32=<%sd>`
  https://www.tibiawiki.com.br/wiki/The_Donina_Formula_2_(Book)
- Index: https://tibia.fandom.com/wiki/Category:Books_in_Demona_Library

## D. Mathematica dating / availability

- `[VIA-SEARCH]` https://en.wikipedia.org/wiki/Wolfram_Mathematica — first
  released 1988-06-23; v3.0 released 1996-09-03; v4.0 released 1999-05-19.
- German university Mathematica site/campus licences (present-day pages, used
  only as evidence that faculty-wide licensing is the normal German model):
  https://www.rz.uni-freiburg.de/en/services/procurement/software/mathematica/info-mathematica-en
  https://www.it.physik.uni-muenchen.de/dienste/software/mathematica/index.html
  https://www.uni-due.de/physik/mathematicalizenz
  https://www.rz.uni-wuerzburg.de/dienste/shop/software/mathematica/
  https://collab.dvb.bayern/spaces/TUMtuphcip/pages/67801381/Mathematica (TUM physics CIP pool)
- University of Regensburg CIP pools (present day):
  https://www.ur.de/rechenzentrum/it-services/cip-pool/index.html
  Software list: https://www.uni-regensburg.de/rechenzentrum/it-dienste/client-services/software-angebot
  **NOT FOUND: any dated 1995-2001 record of a Mathematica licence at Regensburg.**
  A possible archival lead (UR Rechenzentrum software-licence files 1995-1997)
  appeared in Archivportal-D search results but could not be fetched.

## E. Gödel, Escher, Bach in German

- `[VIA-SEARCH]` German edition: *Gödel, Escher, Bach — ein Endloses
  Geflochtenes Band*, trans. Philipp Wolff-Windegg & Hermann Feuersee,
  Klett-Cotta, 1985. https://www.klett-cotta.de/produkt/...-9783608949063-t-4245
- `[VIA-SEARCH]` Mass-market paperback dtv 30017, ISBN 978-3-423-30017-9,
  1991/1992 (sources disagree on year).
  https://www.amazon.de/G%C3%B6del-Escher-Bach-Endloses-Geflochtenes/dp/3423300175
- heise (c't publisher) retrospective calling it a computer-culture classic:
  https://www.heise.de/blog/Klassiker-neu-gelesen-Goedel-Escher-Bach-4702826.html

## F. Number 469 — checks performed

- RFC 469 = "Network mail meeting summary", M. D. Kudlick, March 1973.
  https://www.rfc-editor.org/rfc/rfc469.html  (`[VIA-SEARCH]`, but the title is
  unambiguous and independently listed by datatracker.ietf.org)
- Tibia client versions around 2001 were 6.4 (2001-11-02) and 6.5 (2001-12-19);
  the old client ran to v7.0 in 2002. https://tibia.fandom.com/wiki/Updates
  → 469 is NOT a Tibia client/version number. `[VIA-SEARCH]`
- Arithmetic (computed locally): 469 = 7 x 67; digit sum 19; digit product 216.
- NOT FOUND: any source giving an origin for the name "469".
