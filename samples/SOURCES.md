# Where every sample came from

| File | Who wrote it | Used for |
|---|---|---|
| `my_writing/healthcare_2019.txt` | Me, AMH 2020 essay, April 2019 | Criterion 1; criterion 4's appeals; calibration in unit 7 |
| `my_writing/flooding_2019.txt` | Me, ENC 1102 essay, April 2019 | Criterion 1; criterion 3's human texts; calibration in unit 7 |
| `ai_generated.txt` | Claude, written for unit 7 calibration | Setting the style signal's anchors. **Not used in the unit 8 eval**, because the anchors were tuned on it |
| `ai_lightly_edited.txt` | Claude, light edits of the above | Unit 7 calibration only |
| `ai_hc3_chatgpt.json` | ChatGPT, collected by the HC3 researchers | Criterion 2's AI texts; criterion 3's AI and spliced texts |
| `human_attention_is_all_you_need_2017.txt` | Vaswani et al., 2017 | Criterion 2's human texts |

My headers (name, instructor, date) and citation pages were removed from my
essays. Nothing else was changed.

## HC3 (confirmed ChatGPT text)

- **Source:** Guo et al., *How Close is ChatGPT to Human Experts? Comparison
  Corpus, Evaluation, and Detection* (2023, arXiv:2301.07597). The Hugging
  Face dataset is `Hello-SimpleAI/HC3`, and I used the file `open_qa.jsonl`.
  The researchers collected real ChatGPT answers alongside human answers to
  the same questions.
- **License:** CC BY-SA 4.0. These excerpts are shared under the same license.
- **How the texts were chosen** (rule fixed before anything was scored): in
  file order, take the first ChatGPT answer to each question, and keep it if
  it's 80–300 words. The first 5 are the AI texts (rows 0–4). Then, for the
  next 3 qualifying questions whose human answer is at least 40 words (rows
  5–7), build a splice: the first half of the human answer's sentences
  followed by the second half of the ChatGPT answer's sentences. The human
  answers here are Wikipedia sentences, and they often have no space after a
  full stop (`insurance .She`). My sentence splitter can't find those
  boundaries, so each splice ended up as the whole human answer plus the
  second half of the ChatGPT one. By word count that's still roughly half and
  half.
- **Changes:** HC3 stores line breaks as a backslash followed by `n`. I
  turned those back into real line breaks. Nothing else was edited.

## Attention Is All You Need (confirmed human text)

- **Source:** Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser and
  Polosukhin, *Attention Is All You Need*, NeurIPS 2017 (arXiv:1706.03762).
  Text taken from the ar5iv HTML version. It was written in 2017, before
  ChatGPT existed.
- **Which paragraphs** (rule fixed before anything was scored): the Abstract,
  the first 3 paragraphs of section 1 (Introduction), and the first paragraph
  of section 2 (Background). When I set the rule I said "the 3 paragraphs of
  the Introduction". It actually has 4, and I kept the first 3 rather than
  change the rule after seeing the text.
- **Changes:** math is written as its plain-text form (`h_{t-1}`), and
  footnote markers are removed. Citation brackets like `[35, 2, 5]` are kept
  as written.
- These are short excerpts with attribution, used only for testing a detector.
