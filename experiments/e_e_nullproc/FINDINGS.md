# Family E — the structural null

*Agent 1. Every number here comes from `c469.stats`; every claim is either a
held-out code length (a decidable quantity, no null needed) or carries an
empirical p against `c469.surrogate` families.*

## Headline

**The 469 corpus is a copy-paste artefact.** Under a leave-one-book-out
protocol, a model that says "this book is made of pieces of the other books"
costs **0.40 bits per digit**, while the best sequential statistical model of
any order costs **0.90**. No fixed-order Markov chain, and no variable-order
context tree, comes within a factor of two of the copy model.

That is not a negative result about our search; it is a positive
characterisation of the object. It also bounds how much message there can be.

## 1. Model comparison (`model_compare.py`, `model_comparison.json`)

One protocol for everything: **leave-one-book-out**, bits per digit, every model
a real decodable code. Uniform base-10 is 3.322 bits/digit.

| model | held-out b/d | in-sample b/d | code length of the corpus (bits) |
|---|---|---|---|
| Markov-0 | 3.2655 | 3.2647 | 36,892 |
| Markov-1 | 2.9314 | 2.9206 | 34,106 |
| Markov-2 | 2.0029 | 1.9443 | 34,012 |
| Markov-3 | 1.2584 | 1.1588 | 134,186 |
| Markov-4 | 1.0367 | 0.9087 | 1,221,572 |
| Markov-5 | 0.9863 | 0.8303 | 12,122,725 |
| Markov-6 | 0.9904 | 0.8094 | 121,142,848 |
| CTW depth 2 | 1.9635 | 2.0797 | 23,424 |
| CTW depth 4 | 1.0742 | 1.3578 | 15,293 |
| CTW depth 8 | 0.9086 | 1.2558 | 14,144 |
| CTW depth 16 | **0.8988** | 1.2497 | 14,075 |
| **relative-LZ copy code** | **0.4047** | 0.6930 | **4,558** |

The best statistical model of any order — a variable-order context tree, which
is the strongest thing there is short of a semantic model — needs 0.90 bits per
digit. Saying "this book is made of pieces of the other books" needs **0.40**.
The copy code describes the whole 11,263-digit corpus in **4,558 bits**, a third
of what CTW needs and 1/8 of what a first-order chain needs. Markov's BIC blows
up past order 3 because the parameter count multiplies by ten each step; the
held-out column shows the same thing without needing BIC's asymptotics, and
Markov-6 is already *worse* held-out than Markov-5 (pure memorisation).

**The copy code is not a trick that wins everywhere.** The same table on
surrogates, held-out bits/digit:

| corpus (LZ76 factors) | Markov-3 | CTW-8 | relative-LZ copy |
|---|---|---|---|
| **real 469 (608)** | 1.258 | 0.909 | **0.405** |
| `Shuffle` (3378) | 3.545 | 3.266 | 3.963 (loses) |
| `MarkovK(3)` (1572) | 1.204 | 1.246 | 1.891 (loses) |
| `CopyPasteMutate` (1107) | 1.864 | 1.521 | **0.628** (wins) |

On i.i.d. and Markov material the copy code is *worse* than the sequential
models — it pays for pointers it cannot use. It wins only on material that was
actually built by copying. The real corpus sits on the copy-paste side of this
diagnostic, and further out than the shipped `CopyPasteMutate` defaults.
