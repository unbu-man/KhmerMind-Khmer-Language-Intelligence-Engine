# Translation, subtitles, and accessible ways to communicate

KhmerMind studies how a model learns new business facts and retains older ones. Translation is a way to extend that experiment: ask the same question in Khmer and English, then check whether both routes retrieve the same correct fact after each release.

## 1. Choose the task that preserves what matters

| Input | What the system should do | Example |
| --- | --- | --- |
| Khmer text | Translate the meaning into another language | «តើស្តុកបម្រុងជាអ្វី?» → “What is safety stock?” |
| Japanese dialogue in anime | Transcribe the speech if needed, translate the dialogue, and time subtitles | `ありがとう` → «អរគុណ» → subtitle displayed when the character speaks |
| Invented words in a fictional story | Use documented meanings, a glossary, or enough context to interpret them | A fictional place name may be kept as a name if a translation has no established equivalent. |
| Print text for a Braille reader | Transcribe to the Braille code for that language | Khmer text → Khmer Braille. English text → Unified English Braille. |
| A deliberate blink used as a signal | Decode an agreed selection or message | In a toy example, one deliberate blink selects “yes” and two select “no.” The person and listener agree on the signals first. |

Braille is a tactile writing system. To present an English passage in Khmer Braille, first translate the passage into Khmer. Then transcribe the Khmer text using the relevant Braille code. The Cambodia entry in *World Braille Usage* documents a Khmer code. Assistive communication can also use signals such as eye gaze to select messages. A blink example is about recognizing an agreed signal. An unrecognized pattern should stay undecoded in a learning demo. [World Braille Usage](https://www.perkins.org/resource/world-braille-usage/) · [Unified English Braille](https://iceb.org/publications/ueb/) · [ASHA communication methods](https://www.asha.org/practice-portal/professional-issues/augmentative-and-alternative-communication/)

An anime subtitle adds timing and screen-space constraints to translation. Start with a short, self-written example or a clip you have permission to use. Given a Japanese script, you can practice translating and timing it before adding automatic speech recognition. [Díaz Cintas and Remael, *Subtitling: Concepts and Practices*](https://www.routledge.com/Subtitl-ing-Concepts-and-Practices/Cintas-Remael/p/book/9781138940543)

## 2. Books and chapters to read

| Study order | Book | What to learn |
| --- | --- | --- |
| 1 | Dan Jurafsky and James H. Martin, [*Speech and Language Processing*, online draft](https://web.stanford.edu/~jurafsky/slp3/) | Read Chapter 2 for words, tokens, and segmentation. Read Chapter 13 for machine translation. Chapters 16–17 cover speech recognition and text-to-speech. The numbers are for the August 2026 draft. |
| 2 | Aston Zhang, Zachary C. Lipton, Mu Li, and Alexander J. Smola, [*Dive into Deep Learning*](https://d2l.ai/chapter_recurrent-modern/machine-translation-and-dataset.html) | Read `10.5–10.7 for paired data, an encoder–decoder, and a working sequence-to-sequence example. Trace an input through the encoder and the target tokens through the decoder. |
| 3 | Philipp Koehn, [*Neural Machine Translation*](https://www.cambridge.org/core/books/neural-machine-translation/7AAA628F88ADD64124EA008C425C0197) | Use Chapter 8 for a deeper look at the model. The author's site also links book exercises and code. [Book resources](https://www2.statmt.org/nmt-book/) |
| Application | Jorge Díaz Cintas and Aline Remael, [*Subtitling: Concepts and Practices*](https://www.routledge.com/Subtitl-ing-Concepts-and-Practices/Cintas-Remael/p/book/9781138940543) | Study how timing and reading space change the final subtitle, even after the words have been translated. |
| Reference | Perkins, ICEB, and the Library of Congress, [*World Braille Usage*, 3rd ed.](https://www.perkins.org/resource/world-braille-usage/) | Look up the Cambodia entry. Compare the Khmer code documentation with the English rules before trying any transcription. |

Machine translation for Khmer already exists. The Workshop on Asian Translation publishes a Khmer–English parallel data page with links to news-domain data from the Asian Language Treebank. FLORES-200 includes Khmer for multilingual evaluation, and No Language Left Behind describes a multilingual translation model. These are starting points for translation and evaluation. Our business glossary still needs its own reviewed domain examples. [Workshop on Asian Translation](https://lotus.kuee.kyoto-u.ac.jp/WAT/km-en-data/) · [FLORES-200 language list](https://github.com/facebookresearch/flores/blob/main/flores200/README.md) · [No Language Left Behind](https://doi.org/10.1038/s41586-024-07335-x)

## 3. Follow the math with a tiny translation

Let $x$ be the tokenized source text and $y=(y_1,\ldots,y_m)$ the target text, including an end-of-sequence token where used. The decoder models the target one token at a time:

$$
p_\theta(y\mid x)=\prod_{t=1}^{m}p_\theta(y_t\mid y_{<t},x).
$$

For a toy translation of `ありがとう` into English, imagine the output tokens are `Thank`, `you`, and `<end>`. If the model assigns those steps probabilities $0.80$, $0.75$, and $0.50$, the probability of that particular sequence is $0.80\times0.75\times0.50=0.30$. These are example numbers. Each factor depends on the source and the target tokens already produced. A different tokenizer can change how many prediction steps the model needs. [Jurafsky and Martin, Machine Translation](https://web.stanford.edu/~jurafsky/slp3/13.pdf) · [KhmerMind tokenization math](../lessons/07-tokenization-math.md)

Ways to study this from scratch:

1. Write three sentence pairs. Record which text is the source and which is the target. Split by pair so a translation or paraphrase of a test sentence does not appear in training.
2. Count input and output tokens and note where a word needed subword tokens.
3. Sketch the encoder and decoder. Write out the probability factors for one example, including the end token.
4. Check whether the translation preserves domain meaning, especially names, numbers, and close terms such as gross and net.

## 4. Use translation to test KhmerMind

The current glossary has some English terms inside its Khmer training questions. A few English strings can match through their shared text. The release-3 examples below were run through the existing glossary search.

| Question | Correct fact | Observed result |
| --- | --- | --- |
| «តើស្តុកបម្រុងជាអ្វី?» | `safety_stock_v1` | `safety_stock_v1` |
| “What is safety stock?” | `safety_stock_v1` | `safety_stock_v1` |
| “What extra inventory do we keep to avoid running out?” | `safety_stock_v1` | `inventory_turnover_v1` |
| “What buffer do we keep in case goods run out?” | `safety_stock_v1` | `UNKNOWN` |

The correct English hit shares the phrase `safety stock` with an indexed question. The other two examples show why an experiment needs multiple phrasings. These four queries illustrate test design. They do not establish bilingual accuracy.

A follow-up can compare direct search with translating English questions into Khmer before search. Use human-reviewed English–Khmer pairs linked to the same fact and keep both sides of each pair in the same split. Track errors separately when translation changes the meaning and when the glossary returns the wrong fact after a good translation. If the project later generates translated answers, score those for meaning and terminology as well.

For $N$ known test pairs, let $f_i$ be the correct active fact version and $\hat f_{i,\mathrm{km}}$ and $\hat f_{i,\mathrm{en}}$ be the predictions from the two inputs. Measure how often both routes are correct:

$$
\mathrm{PairedAccuracy}=\frac{1}{N}\sum_{i=1}^{N}
\mathbf{1}[\hat f_{i,\mathrm{km}}=f_i\ \land\ \hat f_{i,\mathrm{en}}=f_i].
$$

If both routes succeed on 8 of 10 pairs, paired accuracy is $0.80$. Agreement between two wrong predictions earns no credit. Report the score for old and new facts after each release, alongside the existing forgetting metric. That keeps the experiment about retaining knowledge across updates and adds a check for using that knowledge in another language.
