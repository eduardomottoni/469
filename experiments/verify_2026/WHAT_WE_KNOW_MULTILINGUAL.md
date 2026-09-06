# 469 — What Is Actually Established / O Que Está Realmente Estabelecido / Co Zostało Faktycznie Ustalone

Consolidated 2026-09-05 · Consolidado em 05/09/2026 · Skonsolidowano 2026-09-05

- [English](#english)
- [Português](#português)
- [Polski](#polski)

All three versions carry identical numbers. Tags: **[R]** = reinforced (previously believed, now measured) · **[N]** = new.

---
---

# English

## 0. The rule that governs everything below

**A statistic without a matched null model is not evidence.** This corpus produces apparently significant results on demand. Seven separate ~4σ findings have been generated and killed during this work, each by replacing a weak null (shuffle, uniform, textbook constant) with one matching the corpus's length *and* symbol inventory *and* local structure.

Any future 469 result that does not name the null it was scored against should be assumed to be one of these.

## 1. The corpus is verified **[N]**

`books.json` is **byte-identical** to primary sources: 70 books, 11,263 digits, zero mismatching positions.

| source | result |
|---|---|
| tibia.fandom.com, 71 pages (MediaWiki API, raw wikitext) | 70/70 exact |
| independent in-game / server-file scrape | 70/70 exact |
| `elkolorado_bacca_books.txt` | 70/70 exact |
| `01-books.md` | 70/70 exact |

This is **not OCR** — digits sit in the `text =` field of the `{{Infobox Book}}` template.

**The 70-vs-71 discrepancy is resolved.** Pages `8550649967 (Book)` and `85506499670 (Book)` are shelved separately but carry identical text (145 digits). De-duplication, not a missing book. For n-gram work 70 is correct.

*Caveat:* this proves faithfulness to the wiki and a server scrape, not to CipSoft's original authoring.

## 2. The central result: the corpus is 85% duplication **[N]**

| stage | digits | |
|---|---|---|
| raw corpus (70 books) | **11,263** | |
| after cross-book assembly | **6,056** | −46% |
| after removing internal repeats | **1,684** | **−85%** |

The assembled master was never irreducible: **125 blocks of ≥12 digits reappear inside it**, making it 72% self-redundant.

**And 1,684 is still an overestimate.** A 176-digit run occurs at master positions 1472 and 5798 — contigs 10 and 23 sharing 176 digits, **64% of contig 23's length**. They should have been merged. The published "ILP-optimal, 24 contigs" assembly has at least one missed join.

At ~1.3 digits/character, 1,684 digits ≈ **1,300 characters — about one page of text.**

## 3. Copy-paste is proven, not inferred **[R]**

**Held-out cost per digit** (leave-one-book-out):

| model | bits/digit |
|---|---|
| uniform random digits | 3.32 |
| Markov-0 | 3.266 |
| best Markov (order 5) | 0.986 |
| context tree, depth 16 | 0.899 |
| **relative-LZ copy code** | **0.405** |

**Longest exact run shared between two books:**

| | digits |
|---|---|
| IID digits | 8 |
| shuffled corpus | 8 |
| Markov-3 | 26 (max 30) |
| **real corpus** | **279** |

Chance probability of a specific 279-digit run ≈ **10⁻²⁷⁴**. **378 of 2,415 book pairs** (16%) share a run of ≥40 digits.

**Books chain end-to-start:**

| | median join | max | books joining ≥40 |
|---|---|---|---|
| Markov-3 null | 2 | 9 | **0** |
| **real corpus** | **52** | **279** | **38 of 70** |

**Assembly shape:** 202 copy operations; median 2 blocks per book; median block 36 digits; 98.3% coverage by copied material; **52 of 70 books contain no new digits**; only 171 digits are not copyable.

**Hand editing is visible.** Book 64 = `X+Y+Z`, book 65 = `Y+X+Z`, |X| = 52 — a block transposition, and the one statistic the fitted generator could **not** reproduce (z = +2.0).

## 4. Why 578 was the wrong object **[N]**

`seed_estimate.txt` (578 digits) is built by taking **the last digit of each LZ76 factor** — its length is *defined* by the factor count, and it is a **scatter** with adjacency destroyed.

| estimate | digits |
|---|---|
| LZ77 literals | 242 |
| LZ76 innovation — *the attacked file* | 578 |
| second-pass internal dedup | 1,684 |
| information bound | ~2,350 |
| ABC posterior median | 2,602 (90% CI **986–5,931**) |
| ABC best-fit point | 7,407 |

The ABC best-fit lies **outside its own 90% credible interval**.

| residue | digits | injected-key recovery |
|---|---|---|
| LZ76 innovation | 578 | **4.4%** |
| greedy min_copy=3 | 242 | 10.9% |
| **union min_copy=8** | **2,058** | **97.6%** |

**The threshold was wrong:** an i.i.d. digit stream of this length already contains a ≥3 match at **91% of positions**. The chance-corrected threshold is 6.

## 5. The search is now powered, and negative **[N]**

At 97.6% power on 2,058 digits, against matched nulls (exact length **and** inventory):

- 50 pre-registered tests: **zero** clear BH q < 0.05 (min q = 0.083)
- 10 solver configurations: **maximum z = +0.01**

**Refuted:** V10 substitution, V100 homophonic (n ≥ 1535), A1Z26, decimal ASCII, dates, index of coincidence, periodicity/Kasiski, additive-key.

**Still underpowered:** V100 at n = 578; German-language solving (the injector emits English, so 0.49–0.66 is a lower bound).

Further negatives:

- **Not Benford** (χ² = 569) — rules out a harvested list of real-world quantities.
- **Not dates.** **1997 appears once (rank 927 of 1,097 four-grams); 2001 and 2011 appear zero times.** `1991` at rank 42 is an ordinary frequent 4-gram (max count 128).
- **Not human random typing.** Repeat avoidance looks textbook against shuffle (z = −7.08) but vanishes at Markov-2 (z = **+0.02**). Counting bias is asymmetric: step +1 enriched (z = +6.39), step −1 at chance (z = −0.08). A human produces both directions. And `7` is *under*-represented where human RNG over-picks it.
- **`1`-as-delimiter refuted.** Pre-registered; ranking came out `5 < 4 < 8 < 3 < 6 < 9 < 2 < 7 < 0 < 1` — **`1` is the worst of ten.**
- **5-eye / base-5 refuted.** Period-5 framing is *anti*-significant (p = 0.92).

## 6. The false-positive machine — the most transferable finding **[N]**

| apparent finding | weak null | matched null |
|---|---|---|
| Zipf slope 1.304 | vs textbook ~1.0 | z = **+1.2** |
| homophonic solve | **+6.26σ** | **max −0.13** |
| modulus-8 structure | +3.6 to +4.7σ | dies on dedup; BH q = 0.058 |
| `43151` occurs 14× | expectation ~0.1 | rank 209 of 1,499 |
| digit-run suppression | z = **−7.08** | z = **+0.02** |
| handwriting confusion | z = **+3.44** | z = **+0.64** |
| residue structure | **17 of 50** q<0.05 | **0 of 50** |

**Rule:** on 469 the null must match length, symbol inventory, and ≥2-digit context. Shuffle and uniform nulls are useless.

## 7. External constraints **[N]**

**There is no in-game key** — measured against Tibia's entire shipped text (2,135 books, 1,148 NPC keyword trees):

- Fiehonja Library ships the Deepling cipher **plus** the alphabet, 116 glossary entries, **and** six worked-solution books, on the same shelves. Rookgaard's `Ork_Porak` does the same for a numeric orc code.
- **Hellgate Library contains 71 books and all 71 are 469.** No prose, no glossary, no companion.
- Exactly **three** references to the bonelord language exist across all NPCs and books — every one an explicit refusal.
- No Tibian conlang has ever been solved cold.

**Developer statements**, all verified primary. Knightmare (2010), Chayenne (2009), Lionet (2022) each answered with a joke; none said "we're not telling." Knightmare's punchline is itself a non-recoverability claim — *"we have no means to tell if the beholder actually wrote down what we dictated him"* — and he warns *"Sometimes players see allusions where there weren't any intended."*

**The two-dialect split is real: p ≈ 5.3 × 10⁻⁶.** Every 469 string with a claimed English meaning occurs **zero** times in the books; every string that does occur is an untranslated quotation. The length confound runs *against* the result (absent set mean 6.5 digits vs 21.0). **No crib is ground truth for the library code.**

## 8. Corrections to standing claims **[N]**

- **Honeminas does not belong in the evidence base.** He is a **Warlock of Demona**, not a bonelord; the book's author is `Mathemicus`; its glossary says it concerns teleport gates. The formula uses a **parenthesis** — `(4,3,1,5,3).(3,4,7,8,4)` — a Mathematica *syntax error*. True digits `43153`/`34784` occur **0 times**; the README's typos `43151`/`34783` occur 14 and 5 times.
- **Known-plaintext budget shrinks from 26 digits to 7.** Elder Bonelord / Evil Eye lines come from a flat four-entry random `voices` table (`interval = 5000, chance = 10`), byte-identical across four OT projects — sampled independently, so they cannot gloss each other.
- **The Facebook pairs table has 31 rows, not 28.** Seven cells `cribs.py` treats as observations are **not legible**, including `(737, 469)` in `FB_PAIRS_CERTAIN` where only `_69` survives. Family D's 18 "certain" pairs are really 16.
- **Poll answer C is not known-plaintext** — A and B decode to *different* sentences.
- **The medieval-comic premise is disconfirmed**, not merely unfound.

## 9. What remains open

1. **~1,700 digits** of irreducible content that no tested code family explains. The binding constraint has moved from sample size to **the space of codes searched**.
2. **Contig 13 — 791 digits from 19 books** — is the largest coherent object. Both halves of Chayenne's 2009 answer sit inside it, at positions 479 and 666.
3. **Accident vs. design cannot be distinguished.** The branch asserts artefact; the repo owner's later article argues deliberate decoy. Both predict what is observed.
4. **80 single-digit variant sites** in the shipped game data, catalogued but unexplained.
5. **63.7% of the master rests on a single witness** (median coverage depth 1).
6. **Nobody at CipSoft has ever said it means nothing, either.**

## 10. Summary

469 is 11,263 digits that reduce to roughly **1,700** — about one page. The reduction is direct measurement, not inference: 202 copy operations, 52 of 70 books containing nothing new, a 279-digit run shared verbatim where chance allows 8, and 38 books whose closing digits are another book's opening digits where a matched null allows none. That page is now searched at 97.6% power, and every standard code family is refuted rather than untested. No in-game key exists where every comparable Tibian cipher shipped one, and three developers across thirteen years each answered with a joke. Nothing proves the page is empty — but the target is now small, verified and bounded, and the remaining uncertainty is about **which code was used**, not how much material there is.

---
---

# Português

## 0. A regra que governa tudo abaixo

**Uma estatística sem um modelo nulo pareado não é evidência.** Este corpus produz resultados aparentemente significativos sob demanda. Sete achados distintos de ~4σ foram gerados e derrubados durante este trabalho, cada um ao substituir um nulo fraco (embaralhamento, uniforme, constante de livro-texto) por um que iguala o comprimento *e* o inventário de símbolos *e* a estrutura local do corpus.

Qualquer resultado futuro sobre 469 que não nomeie o nulo contra o qual foi medido deve ser presumido como mais um destes.

## 1. O corpus está verificado **[N]**

`books.json` é **idêntico byte a byte** às fontes primárias: 70 livros, 11.263 dígitos, zero posições divergentes.

| fonte | resultado |
|---|---|
| tibia.fandom.com, 71 páginas (API MediaWiki, wikitext bruto) | 70/70 exato |
| extração independente dos arquivos do servidor/jogo | 70/70 exato |
| `elkolorado_bacca_books.txt` | 70/70 exato |
| `01-books.md` | 70/70 exato |

Isto **não é OCR** — os dígitos estão no campo `text =` do template `{{Infobox Book}}`.

**A discrepância 70 vs 71 está resolvida.** As páginas `8550649967 (Book)` e `85506499670 (Book)` ficam em estantes diferentes mas têm texto idêntico (145 dígitos). É deduplicação, não um livro faltante. Para trabalho com n-gramas, 70 é o número correto.

*Ressalva:* isto prova fidelidade à wiki e a uma extração do servidor, não à autoria original da CipSoft.

## 2. O resultado central: o corpus é 85% duplicação **[N]**

| etapa | dígitos | |
|---|---|---|
| corpus bruto (70 livros) | **11.263** | |
| após montagem entre livros | **6.056** | −46% |
| após remover repetições internas | **1.684** | **−85%** |

O master montado nunca foi irredutível: **125 blocos de ≥12 dígitos reaparecem dentro dele**, tornando-o 72% auto-redundante.

**E 1.684 ainda é uma superestimativa.** Um trecho de 176 dígitos ocorre nas posições 1472 e 5798 do master — os contigs 10 e 23 compartilham 176 dígitos, **64% do comprimento do contig 23**. Deveriam ter sido fundidos. A montagem publicada como "ILP-ótima, 24 contigs" tem ao menos uma junção perdida.

A ~1,3 dígitos/caractere, 1.684 dígitos ≈ **1.300 caracteres — cerca de uma página de texto.**

## 3. Cópia-e-cola está provado, não inferido **[R]**

**Custo por dígito em dados retidos** (deixando um livro de fora):

| modelo | bits/dígito |
|---|---|
| dígitos uniformemente aleatórios | 3,32 |
| Markov-0 | 3,266 |
| melhor Markov (ordem 5) | 0,986 |
| árvore de contexto, profundidade 16 | 0,899 |
| **código de cópia LZ-relativo** | **0,405** |

**Maior trecho exato compartilhado entre dois livros:**

| | dígitos |
|---|---|
| dígitos IID | 8 |
| corpus embaralhado | 8 |
| Markov-3 | 26 (máx. 30) |
| **corpus real** | **279** |

Probabilidade ao acaso de um trecho específico de 279 dígitos ≈ **10⁻²⁷⁴**. **378 dos 2.415 pares de livros** (16%) compartilham um trecho de ≥40 dígitos.

**Os livros se encadeiam — fim com início:**

| | junção mediana | máx. | livros com junção ≥40 |
|---|---|---|---|
| nulo Markov-3 | 2 | 9 | **0** |
| **corpus real** | **52** | **279** | **38 de 70** |

**Formato da montagem:** 202 operações de cópia; mediana de 2 blocos por livro; bloco mediano de 36 dígitos; 98,3% de cobertura por material copiado; **52 dos 70 livros não contêm nenhum dígito novo**; apenas 171 dígitos não são copiáveis.

**A edição manual é visível.** Livro 64 = `X+Y+Z`, livro 65 = `Y+X+Z`, |X| = 52 — uma transposição de blocos, e a única estatística que o gerador ajustado **não** conseguiu reproduzir (z = +2,0).

## 4. Por que 578 era o objeto errado **[N]**

`seed_estimate.txt` (578 dígitos) é construído tomando **o último dígito de cada fator LZ76** — seu comprimento é *definido* pela contagem de fatores, e é um **espalhamento** com a adjacência destruída.

| estimativa | dígitos |
|---|---|
| literais LZ77 | 242 |
| inovação LZ76 — *o arquivo atacado* | 578 |
| deduplicação interna de segunda passagem | 1.684 |
| limite de informação | ~2.350 |
| mediana posterior ABC | 2.602 (IC 90% **986–5.931**) |
| melhor ajuste pontual ABC | 7.407 |

O melhor ajuste ABC está **fora do seu próprio intervalo de credibilidade de 90%**.

| resíduo | dígitos | recuperação de chave injetada |
|---|---|---|
| inovação LZ76 | 578 | **4,4%** |
| guloso min_copy=3 | 242 | 10,9% |
| **união min_copy=8** | **2.058** | **97,6%** |

**O limiar estava errado:** um fluxo IID de dígitos deste comprimento já contém uma correspondência de ≥3 em **91% das posições**. O limiar corrigido por acaso é 6.

## 5. A busca agora tem poder estatístico — e é negativa **[N]**

Com 97,6% de poder sobre 2.058 dígitos, contra nulos pareados (comprimento **e** inventário exatos):

- 50 testes pré-registrados: **zero** com BH q < 0,05 (q mínimo = 0,083)
- 10 configurações de solver: **z máximo = +0,01**

**Refutados:** substituição V10, homofônico V100 (n ≥ 1535), A1Z26, ASCII decimal, datas, índice de coincidência, periodicidade/Kasiski, chave aditiva.

**Ainda sem poder suficiente:** V100 em n = 578; solução em alemão (o injetor emite inglês, então 0,49–0,66 é um limite inferior).

Outros negativos:

- **Não é Benford** (χ² = 569) — exclui uma lista colhida de quantidades do mundo real.
- **Não são datas.** **1997 aparece uma vez (posição 927 de 1.097 4-gramas); 2001 e 2011 aparecem zero vezes.** `1991` na posição 42 é um 4-grama comum e comum (contagem máxima 128).
- **Não é digitação humana aleatória.** A evitação de repetições parece exemplar contra embaralhamento (z = −7,08) mas desaparece com Markov-2 (z = **+0,02**). O viés de contagem é assimétrico: passo +1 enriquecido (z = +6,39), passo −1 no acaso (z = −0,08). Um humano produz as duas direções. E o `7` está *sub*-representado, justamente onde a geração humana o super-escolhe.
- **`1` como delimitador refutado.** Pré-registrado; o ranking saiu `5 < 4 < 8 < 3 < 6 < 9 < 2 < 7 < 0 < 1` — **`1` é o pior dos dez.**
- **5 olhos / base-5 refutado.** O enquadramento de período 5 é *anti*-significativo (p = 0,92).

## 6. A máquina de falsos positivos — o achado mais transferível **[N]**

| achado aparente | nulo fraco | nulo pareado |
|---|---|---|
| inclinação de Zipf 1,304 | vs constante ~1,0 | z = **+1,2** |
| solução homofônica | **+6,26σ** | **máx. −0,13** |
| estrutura módulo 8 | +3,6 a +4,7σ | morre na deduplicação; BH q = 0,058 |
| `43151` ocorre 14× | expectativa ~0,1 | posição 209 de 1.499 |
| supressão de repetições | z = **−7,08** | z = **+0,02** |
| confusão de escrita à mão | z = **+3,44** | z = **+0,64** |
| estrutura do resíduo | **17 de 50** q<0,05 | **0 de 50** |

**Regra:** em 469, o nulo precisa igualar comprimento, inventário de símbolos e contexto de ≥2 dígitos. Nulos de embaralhamento e uniformes são inúteis.

## 7. Restrições externas **[N]**

**Não existe chave dentro do jogo** — medido contra todo o texto publicado de Tibia (2.135 livros, 1.148 árvores de palavras-chave de NPCs):

- A Biblioteca de Fiehonja publica os livros da cifra Deepling **mais** o alfabeto, 116 entradas de glossário **e** seis livros com soluções resolvidas, nas mesmas estantes. O `Ork_Porak` de Rookgaard faz o mesmo para um código numérico dos orcs.
- **A Biblioteca de Hellgate contém 71 livros e todos os 71 são 469.** Sem prosa, sem glossário, sem companheiro.
- Existem exatamente **três** referências à língua dos bonelords em todos os NPCs e livros — cada uma delas uma recusa explícita.
- Nenhuma conlang de Tibia jamais foi resolvida sem chave.

**Declarações dos desenvolvedores**, todas verificadas em fontes primárias. Knightmare (2010), Chayenne (2009) e Lionet (2022) responderam com piada; nenhum disse "não vamos contar". O desfecho da piada de Knightmare é ele próprio uma alegação de não-recuperabilidade — *"não temos como saber se o beholder realmente escreveu o que ditamos a ele"* — e ele adverte: *"Às vezes os jogadores veem alusões onde nenhuma foi pretendida."*

**A divisão em dois dialetos é real: p ≈ 5,3 × 10⁻⁶.** Toda string 469 com significado em inglês alegado ocorre **zero** vezes nos livros; toda string que de fato ocorre é uma citação não traduzida. O confundidor de comprimento age *contra* o resultado (conjunto ausente: média de 6,5 dígitos vs 21,0). **Nenhum crib é verdade fundamental para o código da biblioteca.**

## 8. Correções a afirmações vigentes **[N]**

- **Honeminas não pertence à base de evidências.** Ele é um **Warlock de Demona**, não um bonelord; o autor do livro é `Mathemicus`; o glossário do próprio livro diz que trata de portais de teleporte. A fórmula usa **parênteses** — `(4,3,1,5,3).(3,4,7,8,4)` — um *erro de sintaxe* em Mathematica. Os dígitos verdadeiros `43153`/`34784` ocorrem **0 vezes**; os erros de digitação do README `43151`/`34783` ocorrem 14 e 5 vezes.
- **O orçamento de texto-claro conhecido cai de 26 dígitos para 7.** As falas do Elder Bonelord / Evil Eye vêm de uma tabela `voices` aleatória de quatro entradas (`interval = 5000, chance = 10`), idêntica byte a byte em quatro projetos OT — amostradas independentemente, portanto não podem glosar umas às outras.
- **A tabela de pares do Facebook tem 31 linhas, não 28.** Sete células que `cribs.py` trata como observações **não são legíveis**, incluindo `(737, 469)` em `FB_PAIRS_CERTAIN`, onde só sobrevive `_69`. Os 18 pares "certos" da Família D são na verdade 16.
- **A resposta C da enquete não é texto-claro conhecido** — A e B decodificam para frases *diferentes*.
- **A premissa dos quadrinhos medievais está desmentida**, não apenas não encontrada.

## 9. O que permanece em aberto

1. **~1.700 dígitos** de conteúdo irredutível que nenhuma família de códigos testada explica. A restrição limitante passou do tamanho da amostra para **o espaço de códigos pesquisado**.
2. **O contig 13 — 791 dígitos de 19 livros** — é o maior objeto coerente. As duas metades da resposta de Chayenne de 2009 estão dentro dele, nas posições 479 e 666.
3. **Acidente vs. projeto não pode ser distinguido.** O branch afirma artefato; o artigo posterior do próprio dono do repositório defende chamariz deliberado. Ambos preveem o que é observado.
4. **80 sítios de variante de um dígito** nos dados publicados do jogo, catalogados mas não explicados.
5. **63,7% do master repousa sobre uma única testemunha** (profundidade mediana de cobertura 1).
6. **Ninguém na CipSoft jamais disse que não significa nada, tampouco.**

## 10. Resumo

469 são 11.263 dígitos que se reduzem a cerca de **1.700** — aproximadamente uma página. A redução é medição direta, não inferência: 202 operações de cópia, 52 dos 70 livros sem nada novo, um trecho de 279 dígitos compartilhado literalmente onde o acaso permite 8, e 38 livros cujos dígitos finais são os dígitos iniciais de outro livro onde um nulo pareado permite nenhum. Essa página é agora pesquisada com 97,6% de poder, e toda família padrão de códigos está refutada, não apenas não testada. Não existe chave dentro do jogo, ao passo que toda cifra tibiana comparável veio com uma, e três desenvolvedores ao longo de treze anos responderam cada um com uma piada. Nada prova que a página esteja vazia — mas o alvo agora é pequeno, verificado e delimitado, e a incerteza restante é sobre **qual código foi usado**, não sobre quanto material existe.

---
---

# Polski

## 0. Zasada rządząca wszystkim poniżej

**Statystyka bez dopasowanego modelu zerowego nie jest dowodem.** Ten korpus produkuje pozornie istotne wyniki na żądanie. Podczas tej pracy wygenerowano i obalono siedem odrębnych wyników rzędu ~4σ — każdy przez zastąpienie słabego modelu zerowego (tasowanie, rozkład jednostajny, stała podręcznikowa) takim, który dopasowuje długość korpusu *oraz* inwentarz symboli *oraz* strukturę lokalną.

Każdy przyszły wynik dotyczący 469, który nie nazywa modelu zerowego, względem którego został oceniony, należy uznać za kolejny z nich.

## 1. Korpus jest zweryfikowany **[N]**

`books.json` jest **identyczny bajt po bajcie** ze źródłami pierwotnymi: 70 ksiąg, 11 263 cyfry, zero rozbieżnych pozycji.

| źródło | wynik |
|---|---|
| tibia.fandom.com, 71 stron (API MediaWiki, surowy wikitext) | 70/70 dokładnie |
| niezależny zrzut z plików gry/serwera | 70/70 dokładnie |
| `elkolorado_bacca_books.txt` | 70/70 dokładnie |
| `01-books.md` | 70/70 dokładnie |

To **nie jest OCR** — cyfry znajdują się w polu `text =` szablonu `{{Infobox Book}}`.

**Rozbieżność 70 vs 71 została wyjaśniona.** Strony `8550649967 (Book)` i `85506499670 (Book)` stoją na różnych półkach, ale mają identyczny tekst (145 cyfr). To deduplikacja, nie brakująca księga. Do analizy n-gramów poprawną liczbą jest 70.

*Zastrzeżenie:* dowodzi to wierności wobec wiki i zrzutu serwerowego, nie wobec oryginalnego autorstwa CipSoftu.

## 2. Wynik centralny: korpus to w 85% duplikacja **[N]**

| etap | cyfry | |
|---|---|---|
| surowy korpus (70 ksiąg) | **11 263** | |
| po złożeniu międzyksięgowym | **6 056** | −46% |
| po usunięciu powtórzeń wewnętrznych | **1 684** | **−85%** |

Złożony master nigdy nie był nieredukowalny: **125 bloków po ≥12 cyfr powtarza się w jego wnętrzu**, co czyni go w 72% samo-redundantnym.

**A 1 684 to wciąż zawyżenie.** Ciąg 176 cyfr występuje na pozycjach 1472 i 5798 mastera — contigi 10 i 23 dzielą 176 cyfr, **64% długości contigu 23**. Powinny były zostać scalone. Opublikowane złożenie „optymalne ILP, 24 contigi" ma co najmniej jedno pominięte połączenie.

Przy ~1,3 cyfry na znak, 1 684 cyfry ≈ **1 300 znaków — mniej więcej jedna strona tekstu.**

## 3. Kopiuj-wklej jest udowodnione, nie wywnioskowane **[R]**

**Koszt na cyfrę na danych wstrzymanych** (z pominięciem jednej księgi):

| model | bity/cyfrę |
|---|---|
| cyfry jednostajnie losowe | 3,32 |
| Markow-0 | 3,266 |
| najlepszy Markow (rząd 5) | 0,986 |
| drzewo kontekstowe, głębokość 16 | 0,899 |
| **kod kopiujący relative-LZ** | **0,405** |

**Najdłuższy dokładny ciąg wspólny dla dwóch ksiąg:**

| | cyfry |
|---|---|
| cyfry IID | 8 |
| przetasowany korpus | 8 |
| Markow-3 | 26 (maks. 30) |
| **rzeczywisty korpus** | **279** |

Prawdopodobieństwo przypadkowe konkretnego ciągu 279 cyfr ≈ **10⁻²⁷⁴**. **378 z 2 415 par ksiąg** (16%) dzieli ciąg ≥40 cyfr.

**Księgi łączą się końcem z początkiem:**

| | mediana złączenia | maks. | księgi łączące ≥40 |
|---|---|---|---|
| model zerowy Markow-3 | 2 | 9 | **0** |
| **rzeczywisty korpus** | **52** | **279** | **38 z 70** |

**Kształt złożenia:** 202 operacje kopiowania; mediana 2 bloki na księgę; mediana bloku 36 cyfr; 98,3% pokrycia materiałem skopiowanym; **52 z 70 ksiąg nie zawierają żadnej nowej cyfry**; tylko 171 cyfr nie da się skopiować.

**Ręczna edycja jest widoczna.** Księga 64 = `X+Y+Z`, księga 65 = `Y+X+Z`, |X| = 52 — transpozycja bloków, i jedyna statystyka, której dopasowany generator **nie** zdołał odtworzyć (z = +2,0).

## 4. Dlaczego 578 było niewłaściwym obiektem **[N]**

`seed_estimate.txt` (578 cyfr) powstaje przez wzięcie **ostatniej cyfry każdego czynnika LZ76** — jego długość jest *zdefiniowana* liczbą czynników, a sam jest **rozproszeniem** z zniszczonym sąsiedztwem.

| oszacowanie | cyfry |
|---|---|
| literały LZ77 | 242 |
| innowacja LZ76 — *atakowany plik* | 578 |
| deduplikacja wewnętrzna drugiego przebiegu | 1 684 |
| granica informacyjna | ~2 350 |
| mediana rozkładu a posteriori ABC | 2 602 (90% CI **986–5 931**) |
| najlepsze dopasowanie punktowe ABC | 7 407 |

Najlepsze dopasowanie ABC leży **poza własnym 90-procentowym przedziałem wiarygodności**.

| reszta | cyfry | odzysk wstrzykniętego klucza |
|---|---|---|
| innowacja LZ76 | 578 | **4,4%** |
| zachłanny min_copy=3 | 242 | 10,9% |
| **suma min_copy=8** | **2 058** | **97,6%** |

**Próg był błędny:** strumień cyfr IID tej długości zawiera już dopasowanie ≥3 na **91% pozycji**. Próg skorygowany o przypadek wynosi 6.

## 5. Poszukiwanie ma teraz moc statystyczną — i jest negatywne **[N]**

Przy mocy 97,6% na 2 058 cyfrach, względem dopasowanych modeli zerowych (dokładna długość **i** inwentarz):

- 50 wstępnie zarejestrowanych testów: **zero** z BH q < 0,05 (min. q = 0,083)
- 10 konfiguracji solwera: **maksymalne z = +0,01**

**Obalone:** podstawienie V10, homofoniczne V100 (n ≥ 1535), A1Z26, ASCII dziesiętne, daty, wskaźnik koincydencji, okresowość/Kasiski, klucz addytywny.

**Nadal bez wystarczającej mocy:** V100 przy n = 578; rozwiązywanie po niemiecku (wstrzykiwacz emituje angielski, więc 0,49–0,66 to dolna granica).

Dalsze wyniki negatywne:

- **Nie Benford** (χ² = 569) — wyklucza zebraną listę wielkości ze świata rzeczywistego.
- **Nie daty.** **1997 pojawia się raz (pozycja 927 z 1 097 4-gramów); 2001 i 2011 nie pojawiają się ani razu.** `1991` na pozycji 42 to zwykły częsty 4-gram (maksimum 128).
- **Nie ludzkie losowe pisanie.** Unikanie powtórzeń wygląda podręcznikowo względem tasowania (z = −7,08), ale znika przy Markowie-2 (z = **+0,02**). Skłonność do liczenia jest asymetryczna: krok +1 wzbogacony (z = +6,39), krok −1 na poziomie przypadku (z = −0,08). Człowiek produkuje oba kierunki. A `7` jest *nie*doreprezentowana tam, gdzie ludzka generacja ją nadmiernie wybiera.
- **`1` jako separator obalone.** Wstępnie zarejestrowane; ranking wyszedł `5 < 4 < 8 < 3 < 6 < 9 < 2 < 7 < 0 < 1` — **`1` jest najgorsza z dziesięciu.**
- **Pięcioro oczu / system piątkowy obalone.** Ramkowanie o okresie 5 jest *anty*-istotne (p = 0,92).

## 6. Maszyna fałszywych pozytywów — najbardziej przenośne odkrycie **[N]**

| pozorne odkrycie | słaby model zerowy | dopasowany model zerowy |
|---|---|---|
| nachylenie Zipfa 1,304 | vs stała ~1,0 | z = **+1,2** |
| rozwiązanie homofoniczne | **+6,26σ** | **maks. −0,13** |
| struktura modulo 8 | +3,6 do +4,7σ | ginie po deduplikacji; BH q = 0,058 |
| `43151` występuje 14× | oczekiwanie ~0,1 | pozycja 209 z 1 499 |
| tłumienie powtórzeń cyfr | z = **−7,08** | z = **+0,02** |
| pomyłki pisma odręcznego | z = **+3,44** | z = **+0,64** |
| struktura reszty | **17 z 50** q<0,05 | **0 z 50** |

**Zasada:** w 469 model zerowy musi dopasowywać długość, inwentarz symboli i kontekst ≥2 cyfr. Modele tasujące i jednostajne są bezużyteczne.

## 7. Ograniczenia zewnętrzne **[N]**

**Nie istnieje klucz w grze** — zmierzone względem całego opublikowanego tekstu Tibii (2 135 ksiąg, 1 148 drzew słów kluczowych NPC):

- Biblioteka Fiehonja publikuje księgi szyfru Deepling **plus** alfabet, 116 haseł słownika **oraz** sześć ksiąg z rozwiązaniami, na tych samych półkach. `Ork_Porak` z Rookgaard robi to samo dla liczbowego kodu orków.
- **Biblioteka Hellgate zawiera 71 ksiąg i wszystkie 71 to 469.** Bez prozy, bez słownika, bez towarzysza.
- W całości NPC-ów i ksiąg istnieją dokładnie **trzy** odniesienia do języka bonelordów — każde z nich to wyraźna odmowa.
- Żaden tibiański język sztuczny nigdy nie został złamany bez klucza.

**Wypowiedzi twórców**, wszystkie zweryfikowane w źródłach pierwotnych. Knightmare (2010), Chayenne (2009) i Lionet (2022) odpowiedzieli żartem; żaden nie powiedział „nie zdradzimy". Puenta żartu Knightmare'a sama jest twierdzeniem o nieodzyskiwalności — *„nie mamy jak stwierdzić, czy beholder faktycznie zapisał to, co mu dyktowaliśmy"* — a on sam ostrzega: *„Czasem gracze widzą aluzje tam, gdzie żadnych nie zamierzano."*

**Podział na dwa dialekty jest realny: p ≈ 5,3 × 10⁻⁶.** Każdy ciąg 469 z przypisywanym angielskim znaczeniem występuje w księgach **zero** razy; każdy ciąg, który tam występuje, jest nieprzetłumaczonym cytatem. Zakłócenie długością działa *przeciw* wynikowi (zbiór nieobecny: średnia 6,5 cyfry vs 21,0). **Żaden crib nie jest podstawą prawdy dla kodu bibliotecznego.**

## 8. Korekty do obowiązujących twierdzeń **[N]**

- **Honeminas nie należy do bazy dowodowej.** Jest **Warlockiem z Demony**, nie bonelordem; autorem księgi jest `Mathemicus`; jej własny słowniczek mówi, że dotyczy wrót teleportacyjnych. Wzór używa **nawiasu okrągłego** — `(4,3,1,5,3).(3,4,7,8,4)` — co jest *błędem składni* w Mathematice. Prawdziwe cyfry `43153`/`34784` występują **0 razy**; literówki z README `43151`/`34783` występują 14 i 5 razy.
- **Budżet znanego tekstu jawnego kurczy się z 26 cyfr do 7.** Kwestie Elder Bonelorda / Evil Eye pochodzą z płaskiej, czteroelementowej losowej tabeli `voices` (`interval = 5000, chance = 10`), identycznej bajt po bajcie w czterech projektach OT — próbkowane niezależnie, więc nie mogą się wzajemnie objaśniać.
- **Tabela par z Facebooka ma 31 wierszy, nie 28.** Siedem komórek, które `cribs.py` traktuje jako obserwacje, jest **nieczytelnych**, w tym `(737, 469)` w `FB_PAIRS_CERTAIN`, gdzie przetrwało tylko `_69`. 18 „pewnych" par Rodziny D to w rzeczywistości 16.
- **Odpowiedź C w ankiecie nie jest znanym tekstem jawnym** — A i B dekodują się do *różnych* zdań.
- **Przesłanka o średniowiecznych komiksach została obalona**, nie tylko nieodnaleziona.

## 9. Co pozostaje otwarte

1. **~1 700 cyfr** nieredukowalnej treści, której nie wyjaśnia żadna przetestowana rodzina kodów. Wiążące ograniczenie przesunęło się z wielkości próby na **przestrzeń przeszukiwanych kodów**.
2. **Contig 13 — 791 cyfr z 19 ksiąg** — to największy spójny obiekt. Obie połowy odpowiedzi Chayenne z 2009 roku znajdują się w nim, na pozycjach 479 i 666.
3. **Przypadku od zamysłu nie da się odróżnić.** Gałąź twierdzi, że to artefakt; późniejszy artykuł samego właściciela repozytorium dowodzi celowej przynęty. Oba przewidują to, co obserwujemy.
4. **80 miejsc wariantu jednocyfrowego** w opublikowanych danych gry, skatalogowanych, ale niewyjaśnionych.
5. **63,7% mastera opiera się na pojedynczym świadku** (mediana głębokości pokrycia 1).
6. **Nikt w CipSofcie nigdy nie powiedział też, że to nic nie znaczy.**

## 10. Podsumowanie

469 to 11 263 cyfry, które redukują się do około **1 700** — mniej więcej jednej strony. Redukcja jest bezpośrednim pomiarem, nie wnioskowaniem: 202 operacje kopiowania, 52 z 70 ksiąg bez niczego nowego, ciąg 279 cyfr dzielony dosłownie tam, gdzie przypadek pozwala na 8, oraz 38 ksiąg, których końcowe cyfry są początkowymi cyframi innej księgi tam, gdzie dopasowany model zerowy nie pozwala na żadną. Ta strona jest teraz przeszukana z mocą 97,6%, a każda standardowa rodzina kodów jest obalona, nie zaś jedynie nieprzetestowana. Nie istnieje klucz w grze, podczas gdy każdy porównywalny szyfr tibiański został wydany wraz z kluczem, a trzej twórcy na przestrzeni trzynastu lat odpowiedzieli każdy żartem. Nic nie dowodzi, że strona jest pusta — ale cel jest teraz mały, zweryfikowany i ograniczony, a pozostała niepewność dotyczy **tego, jakiego kodu użyto**, nie zaś tego, ile jest materiału.
