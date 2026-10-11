"""Check module sources against the counts of AUTHORING.md section 1 and section 10 item 7.

Checked: sentence, paragraph, average and word counts, a sentence that starts with a symbol, and formula punctuation.
Not checked (the writer and the reviewer judge them; each is a rule of AUTHORING section 1 or a limit it names):
  * Voice: the main clause early, active voice and filler, "one main point" per sentence and "one idea" per
    paragraph, a bare this/it/that that refers back across a paragraph break, a theorem with more than two
    hypotheses that is not listed, one term per concept, idioms and phrasal verbs, noun stacks (more than two
    nouns before the head noun), stacked negatives, more than one colon in a sentence, question headings,
    "separate two formulas by words", a 中文導讀 box (3-6 sentences, Taiwan usage);
  * Formulas: an inline formula longer than about 15 symbols (it belongs in a display);
  * Length: the 5,500-word target of a first draft and the 36-page limit (build/qa/pdf_scale.py and the PDF
    page count cover pages).

Usage:
    uv run python build/qa/style.py src/lm08.md [src/lm09.md ...] [--quiet] [--strict]

Per module the report gives the prose word count, the sentence count, the average words per sentence, and a
file:line entry for every item below. Exit code 1 when any FAIL is reported; 2 when a file cannot be read (the other
files are still checked).

    FAIL in every volume   unclosed-display: a ``$$`` that opens a display and never closes (the rest of the file
                           would silently drop out of the counts)
                           formula-punct: an inline formula followed by a character that AUTHORING section 1
                           ("Formula punctuation") does not allow (anything but white space, an opening bracket,
                           a GLUE character of build/build.py, or an HTML line break <br>); the whole file is
                           checked, front matter and 中文導讀 boxes included
    FAIL from Volume II    sentence>30: a sentence of more than 30 words
                           para>80: a paragraph of more than 80 words
                           symbol-start: a sentence that starts with an inline formula that is not a number
                           avg>=16: an average of 16 or more words per sentence
                           words>6000: more than 6,000 words of prose
    INFO                   sentence 25-30: a sentence of 25 to 30 words, for the writer's judgment
                           option-symbol-start: a multiple-choice option that starts with a formula

Volume I modules (front matter ``lm:`` 1 to 7) get only formula-punct and unclosed-display as FAIL; their other
results print as INFO.
``--strict`` applies the Volume II rules to every module. ``--quiet`` prints the summary line per module only.

What is counted (AUTHORING section 1, "Voice" and "Length"):
  * Scope: English text after the front matter. Left out: displays ``$$...$$``, tables, fenced code,
    headings, box titles, ``> [!zh]`` boxes, and the Glossary and References sections.
  * Words: split on white space after replacing each inline formula, each ``[[...]]`` reference and each inline
    code span by one token. A token without a letter or digit (a lone dash, "÷", "...") is no word: it joins the
    word before it. A part label such as (a) or **A.**, and a run-in head such as **The exponential.**,
    **$\\rho=+1$.** or *Proof.* (bold or italic; a bold head may end in a colon, **Linearity:**), is counted as prose
    but is not part of a sentence. A run-in head is a label only at the start of a paragraph (or list item) or right
    after a lettered part label; anywhere else a bold or italic sentence is an ordinary sentence. Only a lettered
    part label (a), never a run-in head, splits a paragraph into two groups for the 80-word limit. A bold or italic
    run-in head that starts with a capital letter, at the start of a source line right after a display that ends a
    sentence, begins a new paragraph (``$$ x = 1. $$`` then ``**Bounded.** By the bound ...``); after a display that
    does not end a sentence, or with a lower-case head such as ``*i.e.*``, the text goes on in the same paragraph.
  * Sentences end at . ? or ! (not at a semicolon), or at a full stop inside the last formula of a sentence
    (``$x=1.$ The ...``). Not an end: e.g., i.e., cf., vs., Eq., Fig., "U.S." (recast a
    sentence that ends with it), "No." before a number, a chain of initials, decimals and equation
    numbers such as (7.7) (they are inside a token), "..." or "…" before a lower-case word or a formula, and a
    "?" or "!" followed by a lower-case word (``"why 5-8%?" is therefore ...``). "etc.", "a.m.", "p.m.", "a.s.",
    "al." (as in "et al."), "Inc.", "Ltd.", "Co." and "Corp." end a sentence before a capital letter, a formula or
    a part label such as (b), and not before a lower-case word, also one after an opening bracket ("etc. (see the
    table)"; "Co." not before "Ltd." either). A display that ends with a full
    stop (or with an end-of-proof mark) ends the sentence; a display that does not lets the sentence continue when
    the text after it starts in lower case or with a formula.
  * Paragraphs end at a blank line, a display, a box or heading, a table, a change of ``>`` depth, a new list item.
    A lettered part "(a)" at the start of a sentence starts a new group of the same paragraph, counted by itself for
    the 80-word limit. A sentence that continues after a display counts in the paragraph where it began.
  * Exempt from the sentence and paragraph limits and from the average (their words still count as prose): a sentence
    that itself starts with "Source:", "Sources:", "Computations:", "Computed by" or "Computed with" (the Source and
    Computations sentences of an exhibit note; the sentences after it are checked), in a Notation note a symbol list
    (a sentence with at least 3 inline formulas and at least one per 10 words; the other sentences of the note are
    checked, but a Notation sentence may start with a formula), tables, code and displays. An end-of-proof mark
    ``$\\blacksquare$`` is not a sentence and not a word of one: it ends the sentence before it, and the text after it
    starts a new sentence. Multiple-choice options (``**A.**`` ...) are checked but left out of the
    sentence count and the average, because an option such as ``7.68%`` is a fragment.
  * Not a symbol start: a number (``$5$``, ``$-3\\%$``, ``$10^{-4}\\%$``, ``$1/12$``, ``$\\$5$``,
    ``$\\text{NT\\$}100$``), a part label.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Keep in sync with GLUE in build/build.py (characters the renderer keeps on the formula's line).
GLUE = set(".,;:!?)]\u2019\u201d\"'\uff0c\u3002\u3001\u300d\u300f\uff09\u3011\u300b\uff01\uff1f")
OPENERS = set("([{\uff08\u300c\u300e\u3010\u300a")

INLINE_MATH = re.compile(r"(?<![\\$])\$(?!\$)((?:[^\n$\\]|\\.)+?)\$")  # build.py's pattern
DISPLAY = re.compile(r"(?<!\\)\$\$")
CODE_SPAN = re.compile(r"`[^`\n]+`")
FENCE_OPEN = re.compile(r"^[ >]*(```|~~~)")
REF = re.compile(r"\[\[[^\]\n]*?\]\]")
LINK = re.compile(r"!?\[([^\]\n]*)\]\([^)\n]*\)")
BREAK = re.compile(r"<br\s*/?>", re.IGNORECASE)
TAG = re.compile(r"<[^>\n]+>")
PREFIX = re.compile(r"^>[ \t]?")
LIST_MARK = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
BOX = re.compile(r"^\[!(\w+)\][-+]?\s*(.*)$")
FRONT = re.compile(r"\A---\n.*?\n---[ \t]*(?:\n|\Z)", re.DOTALL)

FORMULA = "\u27e6M{}\u27e7"  # placeholder for one inline formula (index into the formula list)
REFTOK = "\u27e6R\u27e7"
CODETOK = "\u27e6C\u27e7"  # placeholder for one inline code span
FORMULA_TOK = re.compile(r"\u27e6M(\d+)\u27e7")
DEND, DCONT = "\x02E", "\x02C"  # display that ends / does not end a sentence
CLOSERS = "\"\u201d\u2019')]*_"
LEAD = "*_\"\u201c\u2018'(["

# Abbreviations whose full stop never ends a sentence, and those that end one before a capital letter.
ABBR = {
    "e.g.", "i.e.", "cf.", "vs.", "viz.", "Eq.", "Eqs.", "eq.", "Fig.", "Figs.", "Sec.", "Ch.",
    "U.S.",  # almost always followed by a proper noun ("U.S. Treasury"); recast a sentence that ends with it
    "approx.", "p.", "pp.", "Vol.", "vol.", "ed.", "eds.", "Mr.", "Ms.", "Mrs.", "Dr.", "St.", "Jr.",
    "Art.", "ca.", "Jan.", "Feb.", "Mar.", "Apr.", "Jun.", "Jul.", "Aug.", "Sep.", "Sept.", "Oct.",
    "Nov.", "Dec.",
}
CORP = {"Inc.", "Ltd.", "Co.", "Corp."}  # end a sentence before a capital letter, unless another suffix follows
ABBR_MAYBE_END = {"etc.", "a.m.", "p.m.", "a.s.", "al."} | CORP
LABEL = re.compile(r"\*{0,2}(\([a-h]\)|\((?:i|ii|iii|iv|v|vi|vii|viii)\))\*{0,2}|\*\*[A-E]\.\*\*")
EXEMPT_START = ("Source:", "Sources:", "Computations:", "Computed by", "Computed with")
# a run-in head, bold or italic: **The exponential.**, **$\rho=+1$.**, *Proof.*, *Proof (when $h''\le0$ on $I$).*
# a bold head may also end in a colon: **Linearity:**
RUN_IN = re.compile(r"(?:\*\*[^*]+[.:]\*\*|\*[^*]+\.\*|_[^_*]+\._)")
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
END_MARKS = {r"\blacksquare", r"\square", r"\qed"}  # end-of-proof marks are not sentences
SPACING = re.compile(r"\\(?:q?quad|[,;:! ])|\s")  # spacing commands that may surround an end mark


def is_end_mark(formula: str | None) -> bool:
    """``$\\blacksquare$``, also written with spacing: ``$\\quad\\blacksquare$``."""
    return formula is not None and SPACING.sub("", formula) in END_MARKS

NAMES = {
    "-": "hyphen -", "\u2013": "en dash", "\u2014": "em dash", "\u2212": "minus sign", "%": "percent %",
    "\uff1b": "fullwidth semicolon", "\uff1a": "fullwidth colon", "/": "slash /", "\x01": "code",
    "\u201c": "opening quote", "\u2018": "opening quote",
}


@dataclass
class Item:
    line: int
    kind: str
    msg: str
    fail: bool = False


@dataclass
class Para:
    depth: int
    start: int
    notation: bool
    option: bool
    tokens: list[tuple[str, int]] = field(default_factory=list)


@dataclass
class Sentence:
    words: int
    line: int
    first: str
    text: str
    exempt: bool
    group: tuple[int, int]


# ---------------------------------------------------------------- formula punctuation


def describe(c: str) -> str:
    if c in NAMES:
        return NAMES[c]
    if c.isascii() and c.isalpha():
        return f"letter {c!r}"
    if c.isdigit():
        return f"digit {c!r}"
    return f"character {c!r} (U+{ord(c):04X})"


def formula_punctuation(text: str) -> list[Item]:
    """Every inline formula followed by a character that the formula-punctuation rule does not allow."""

    def blank(m: re.Match[str]) -> str:
        return re.sub(r"[^\n]", "\x01", m.group(0))  # keeps offsets and line numbers

    t = re.sub(r"(?ms)^[ >]*(```|~~~).*?^[ >]*\1[ \t]*$", blank, text)
    t = CODE_SPAN.sub(blank, t)
    t = re.sub(r"(?s)(?<!\\)\$\$(.+?)(?<!\\)\$\$", blank, t)
    skip = re.compile(r"(?:\*+|_+|\]\([^)\s]*\)|</(?:em|strong|a)>)+")
    items: list[Item] = []
    for m in INLINE_MATH.finditer(t):
        j = m.end()
        sk = skip.match(t, j)
        if sk:
            j = sk.end()
        if j >= len(t):
            continue
        c = t[j]
        if c == "\\" and j + 1 < len(t):  # a backslash escape renders the next character
            c = t[j + 1]
        if c.isspace() or c in GLUE or c in OPENERS or BREAK.match(t, j):
            continue
        line = t.count("\n", 0, m.start()) + 1
        before = t[max(0, m.start() - 12):j + 10].replace("\n", " ").replace("\x01", "#")
        items.append(Item(line, "formula-punct", f"{describe(c)} right after an inline formula: ...{before}...", True))
    return items


# ---------------------------------------------------------------- prose tokens, sentences, paragraphs


def head_length(words: list[str]) -> int:
    """Number of tokens of the run-in head that starts ``words`` (0 when there is none).

    **Source:** and the other exhibit-note starts are no run-in head: their sentence is exempt, not dropped."""
    if not words or not words[0].startswith(("*", "_")):
        return 0
    if " ".join(words[:2]).lstrip("*_").startswith(EXEMPT_START):
        return 0
    for n in range(1, min(len(words), 10) + 1):
        if RUN_IN.fullmatch(" ".join(words[:n])):
            return n
    return 0


def is_number(formula: str) -> bool:
    """A formula that is a number: digits with an optional sign, % sign, units in \\text{} or power of ten."""
    s = re.sub(r"\\(?:text|mathrm)\{(?:[^{}]|\\.|\{[^{}]*\})*\}", "", formula)
    s = re.sub(r"\\[,;:! ]|\{,\}", "", s)
    s = s.replace("{", "").replace("}", "").replace(" ", "")
    # sign, \$, digits, fraction 1/12, 2.0\times10^-5, power 10^-4, then \%
    pattern = (r"[+\-\u2212]?(?:\\\$)?\d[\d.,]*(?:/\d+)?(?:\\(?:times|cdot)10\^[-\u2212+\d]+)?"
               r"(?:\^[-\u2212+\d]+)?\\?%?")
    return re.fullmatch(pattern, s) is not None


def display_ends_sentence(body: str) -> bool:
    s = re.sub(r"\\tag\{[^}]*\}", "", body)
    s = re.sub(r"(\\end\{[^}]*\}|\\right\.|\\[,;:! ]|\\q?quad|\\\\|\}|\s)+$", "", s.strip())
    if any(s.endswith(m) for m in END_MARKS):  # a display that ends with a proof mark ends the sentence
        return True
    return s[-1:] in (".", "?", "!")


def starts_lower_or_math(tok: str) -> bool:
    t = tok.lstrip(LEAD)
    return t.startswith("\u27e6M") or t[:1].islower()


def ends_with_period(formula: str) -> bool:
    """A formula whose last visible character is a full stop: ``$x=1.$``."""
    return re.sub(r"(\\[,;:! ]|\\q?quad|\\\\|\s)+$", "", formula.strip()).endswith(".")


def ends_sentence(tok: str, prev: str, nxt: str, math_dot: bool = False) -> bool:
    core = tok.rstrip(CLOSERS)
    if math_dot:  # the full stop is inside the formula, '$x=1.$ The ...'
        return not starts_lower_or_math(nxt)
    if core[-1:] in ("?", "!"):
        # '"why 5-8%?" is therefore ...' goes on; a part label such as (b) starts a new sentence
        return LABEL.fullmatch(nxt) is not None or not nxt.lstrip(LEAD)[:1].islower()
    if core[-1:] not in (".", "…"):
        return False
    base = core.lstrip(LEAD)
    if base.endswith(("...", "…")):  # '1, 2, ... and so on' goes on; '... Then' and '... (b)' may end a sentence
        return nxt == "" or LABEL.fullmatch(nxt) is not None or nxt.lstrip(LEAD)[:1].isupper()
    if base in ABBR:
        return False
    if base in ("No.", "Nos."):  # "No. 5" is a number; "No. The variance ..." is a reply
        return not (nxt[:1].isdigit() or nxt.startswith("⟦M"))
    if base in CORP and nxt.lstrip(LEAD) in CORP:  # "Acme Co. Ltd."
        return False
    if base in ABBR_MAYBE_END:  # 'etc. Then ...', 'Inc. $x$ is ...' and 'etc. (b) ...' start a new sentence
        if LABEL.fullmatch(nxt):
            return True
        n = nxt.lstrip(LEAD)
        return n.startswith("⟦M") or n[:1].isupper()
    initial = re.compile(r"[A-Z]\.")
    chain = initial.fullmatch(base) and (initial.fullmatch(nxt.lstrip(LEAD)) or initial.fullmatch(prev.lstrip(LEAD)))
    return not chain  # a chain of initials, "J. P. Morgan", does not end a sentence


class Analyzer:
    def __init__(self, text: str):
        text = text.replace("\r\n", "\n")
        # an HTML comment is not prose: blank it, keeping offsets and line numbers
        self.text = COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
        self.formulas: list[str] = []
        self.paras: list[Para] = []
        self.cur: Para | None = None
        self.waiting = False  # a blank line followed the current paragraph
        self.in_disp = False
        self.disp_line = 0  # line where the open display began
        self.disp: list[str] = []
        self.stack: dict[int, tuple[str, str]] = {}
        self.zh_depth: int | None = None
        self.skip_section = False
        self.in_fence = False
        m = FRONT.match(self.text)
        self.body_start = self.text.count("\n", 0, m.end()) if m else 0
        self.volume_no = self.front_number(m.group(0)) if m else None

    @staticmethod
    def front_number(front: str) -> int | None:
        m = re.search(r"(?m)^lm:\s*(\d+)", front)
        return int(m.group(1)) if m else None

    # -- tokens
    def tokens(self, piece: str, line: int) -> list[tuple[str, int]]:
        def keep(m: re.Match[str]) -> str:
            self.formulas.append(m.group(1))
            return FORMULA.format(len(self.formulas) - 1)

        s = INLINE_MATH.sub(keep, piece)
        s = REF.sub(REFTOK, s)
        s = s.replace("\\$", "$")
        s = LINK.sub(r"\1", s)
        s = BREAK.sub(" ", s)
        s = TAG.sub("", s)
        s = s.replace("\x00", CODETOK)  # an inline code span is one token, like a formula
        return [(t, line) for t in s.split()]

    # -- paragraphs
    def finalize(self) -> None:
        if self.cur is not None and self.cur.tokens:
            self.paras.append(self.cur)
        self.cur = None
        self.waiting = False

    def notation(self) -> bool:
        box = self.stack.get(1)
        return bool(box and box[0] == "note" and box[1].lower().startswith("notation"))

    def run(self) -> None:
        lines = self.text.split("\n")
        for idx in range(self.body_start, len(lines)):
            self.line(idx + 1, lines[idx])
        self.finalize()

    def line(self, no: int, raw: str) -> None:
        depth, rest = 0, raw
        while True:
            m = PREFIX.match(rest)
            if not m:
                break
            depth += 1
            rest = rest[m.end():]
        stripped = rest.strip()
        if self.zh_depth is not None:
            if depth >= self.zh_depth or (stripped == "" and depth >= 1):
                return
            self.zh_depth = None
        if not self.in_disp and FENCE_OPEN.match(raw) and stripped.startswith(("```", "~~~")):
            self.in_fence = not self.in_fence
            self.finalize()
            return
        if self.in_fence:
            return
        if self.in_disp:
            self.pieces_to_tokens(rest, no)
            return
        if depth == 0 and re.match(r"#{1,6}\s", stripped):
            self.finalize()
            if stripped.startswith("## "):
                self.skip_section = re.match(r"##\s+(Glossary|References)\b", stripped) is not None
            return
        if self.skip_section:
            return
        if stripped == "":
            if self.cur is not None:
                self.waiting = True
            return
        for d in [d for d in self.stack if d > depth]:
            del self.stack[d]
        if depth == 0:
            self.stack.clear()
        box = BOX.match(stripped)
        if box:
            self.finalize()
            self.stack[depth] = (box.group(1), box.group(2))
            if box.group(1) == "zh":
                self.zh_depth = depth
            return
        if stripped.startswith(("|", "![")):
            self.finalize()
            return
        if not TAG.sub("", stripped).strip():
            self.finalize()
            return
        lm = LIST_MARK.match(rest)
        content = rest[lm.end():] if lm else rest
        self.begin(no, depth, content, lm is not None)

    def begin(self, no: int, depth: int, content: str, is_list: bool) -> None:
        c = CODE_SPAN.sub("\x00", content)
        starts_display = c.lstrip().startswith("$$")
        pieces = self.split_display(c, no)
        first = next((self.tokens(p, no) for k, p in pieces if k == "t" and p.strip()), [])
        cur = self.cur
        keep = cur is not None and cur.depth == depth and not is_list
        # a run-in head that starts with a capital letter, on a new line after a display that ends a sentence,
        # "**Bounded.** By ...", begins a new paragraph; "*i.e.* ..." after a display that goes on does not
        after_end = keep and cur is not None and bool(cur.tokens) and cur.tokens[-1][0] == DEND and not starts_display
        if after_end and first and first[0][0].lstrip("*_")[:1].isupper() and head_length([t for t, _ in first[:10]]):
            keep = False
        if keep and self.waiting and cur is not None:
            last = cur.tokens[-1][0] if cur.tokens else ""
            keep = starts_display or (last == DCONT and bool(first) and starts_lower_or_math(first[0][0]))
        if not keep:
            self.finalize()
            self.cur = Para(depth, no, self.notation(), bool(re.match(r"\s*\*\*[A-E]\.\*\*", content)))
        self.waiting = False
        self.emit(pieces, no)

    def split_display(self, c: str, no: int) -> list[tuple[str, str]]:
        pieces: list[tuple[str, str]] = []
        pos = 0
        while True:
            m = DISPLAY.search(c, pos)
            if self.in_disp:
                if not m:
                    self.disp.append(c[pos:])
                    break
                self.disp.append(c[pos:m.start()])
                pieces.append(("d", "\n".join(self.disp)))
                self.disp, self.in_disp, pos = [], False, m.end()
            else:
                if not m:
                    pieces.append(("t", c[pos:]))
                    break
                pieces.append(("t", c[pos:m.start()]))
                self.in_disp, self.disp, pos = True, [], m.end()
                self.disp_line = no
        return pieces

    def pieces_to_tokens(self, rest: str, no: int) -> None:
        pieces = self.split_display(CODE_SPAN.sub("\x00", rest), no)
        self.emit(pieces, no)

    def emit(self, pieces: list[tuple[str, str]], no: int) -> None:
        if self.cur is None:
            self.cur = Para(0, no, self.notation(), False)
        for kind, p in pieces:
            if kind == "t":
                self.cur.tokens.extend(self.tokens(p, no))
            else:
                self.cur.tokens.append((DEND if display_ends_sentence(p) else DCONT, no))

    # -- sentences
    def sentences(self, p: Para) -> list[Sentence]:
        toks = p.tokens
        real = [k for k, (t, _) in enumerate(toks) if t not in (DEND, DCONT)]
        out: list[Sentence] = []
        cur: list[str] = []
        state = {"line": 0, "seg": 0, "label": 0}
        seg = label = skip_until = 0
        head_ok = True  # nothing but part labels has come yet, so a run-in head may start here

        def exempt() -> bool:
            if " ".join(cur[:2]).lstrip("*_").startswith(EXEMPT_START):
                return True  # the Source or Computations sentence of an exhibit note
            if p.notation:  # a symbol list of a notation note: many formulas, at least one per 10 words
                formulas = sum(1 for t in cur if FORMULA_TOK.match(t.lstrip(LEAD)))
                return formulas >= 3 and formulas * 10 >= len(cur)
            return False

        def close() -> None:
            if cur:
                out.append(Sentence(len(cur), state["line"], cur[0], self.show(cur), exempt(),
                                    (state["label"], state["seg"])))
                cur.clear()

        for k, (tok, line) in enumerate(toks):
            if k < skip_until:
                continue
            if tok in (DEND, DCONT):
                seg += 1
                if tok == DEND:
                    close()
                else:
                    nxt = next((toks[j][0] for j in real if j > k), None)
                    if nxt is None or not starts_lower_or_math(nxt):
                        close()
                continue
            if is_end_mark(self.formula_of(tok)):  # $\blacksquare$ ends the sentence before it and is no word
                close()
                head_ok = False
                continue
            if not re.search(r"\w", tok):  # a lone dash or "÷" is no word: it joins the word before it
                if not cur:
                    continue
                cur[-1] += tok
                tok = cur[-1]
            else:
                if not cur and LABEL.fullmatch(tok):
                    label += 1  # a lettered part label splits the paragraph into groups
                    head_ok = True  # and a run-in head may follow it
                    continue
                # a run-in head (bold or italic) is a label, but only at the start of a paragraph or right after
                # a lettered part label; it does not split the paragraph. Elsewhere it is an ordinary sentence.
                n = head_length([t for t, _ in toks[k:k + 10]]) if not cur and head_ok else 0
                if n:
                    skip_until = k + n
                    head_ok = False
                    continue
                head_ok = False
                if not cur:
                    state.update(line=line, seg=seg, label=label)
                cur.append(tok)
            prev = cur[-2] if len(cur) > 1 else ""
            nxt = next((toks[j][0] for j in real if j > k), "")
            f = FORMULA_TOK.fullmatch(tok.strip(LEAD + CLOSERS))
            math_dot = f is not None and ends_with_period(self.formulas[int(f.group(1))])
            if ends_sentence(tok, prev, nxt, math_dot):
                close()
        close()
        return out

    def show(self, toks: list[str]) -> str:
        def formula(m: re.Match[str]) -> str:
            f = self.formulas[int(m.group(1))]
            return "$" + (f if len(f) <= 24 else f[:23] + "\u2026") + "$"

        s = FORMULA_TOK.sub(formula, " ".join(toks)).replace(REFTOK, "[[\u2026]]").replace(CODETOK, "`\u2026`")
        words = s.split()
        return " ".join(words[:14]) + (" \u2026" if len(words) > 14 else "")

    def formula_of(self, tok: str) -> str | None:
        m = FORMULA_TOK.match(tok.lstrip(LEAD))
        return self.formulas[int(m.group(1))] if m else None


# ---------------------------------------------------------------- report


@dataclass
class Result:
    name: str
    words: int
    sentences: int
    average: float
    items: list[Item]
    volume1: bool


def check(path: Path, strict: bool) -> Result:
    text = path.read_text(encoding="utf-8")
    an = Analyzer(text)
    an.run()
    num = an.volume_no
    if num is None:
        m = re.search(r"lm(\d+)", path.stem, re.IGNORECASE)
        num = int(m.group(1)) if m else None
    volume1 = num is not None and num <= 7 and not strict

    items = formula_punctuation(an.text)
    words = sum(1 for p in an.paras for t, _ in p.tokens if t not in (DEND, DCONT) and re.search(r"\w", t))
    total_w = total_s = 0
    groups: dict[tuple[int, tuple[int, int]], tuple[int, int]] = {}
    if an.in_disp:
        items.append(Item(an.disp_line, "unclosed-display", "a $$ opens a display that never closes; "
                          "the text after it is not counted", True))
    for pi, p in enumerate(an.paras):
        for s in an.sentences(p):
            if s.exempt:
                continue
            if not p.option:  # an option such as "7.68%" is a fragment, not a sentence
                total_w += s.words
                total_s += 1
            if s.words > 30:
                items.append(Item(s.line, "sentence>30", f'{s.words} words: "{s.text}"', True))
            elif s.words >= 25:
                items.append(Item(s.line, "sentence 25-30", f'{s.words} words: "{s.text}"'))
            f = an.formula_of(s.first)
            if f is not None and not is_number(f) and not p.notation:  # a notation entry may start with its symbol
                kind = "option-symbol-start" if p.option else "symbol-start"
                items.append(Item(s.line, kind, f'starts with the formula ${f}$: "{s.text}"', not p.option))
            key = (pi, s.group)
            w, ln = groups.get(key, (0, s.line))
            groups[key] = (w + s.words, ln)
    for w, ln in groups.values():
        if w > 80:
            items.append(Item(ln, "para>80", f"paragraph of {w} words", True))
    avg = total_w / total_s if total_s else 0.0
    if avg >= 16:
        items.append(Item(0, "avg>=16", f"average {avg:.2f} words per sentence", True))
    if words > 6000:
        items.append(Item(0, "words>6000", f"{words} words of prose (limit 6,000)", True))
    for it in items:
        if volume1 and it.kind not in ("formula-punct", "unclosed-display"):
            it.fail = False
    return Result(str(path), words, total_s, avg, sorted(items, key=lambda i: (i.line, i.kind)), volume1)


def report(r: Result, quiet: bool) -> int:
    fails = [i for i in r.items if i.fail]
    infos = [i for i in r.items if not i.fail]
    if not quiet:
        tag = "Volume I: only formula-punct and unclosed-display fail" if r.volume1 else "Volume II rules"
        print(f"== {r.name} ({tag})")
        for it in r.items:
            label = "FAIL" if it.fail else "INFO"
            where = f"{r.name}:{it.line}" if it.line else r.name
            print(f"{where}: {label} {it.kind}: {it.msg}")
    kinds: dict[str, int] = {}
    for it in r.items:
        kinds[it.kind] = kinds.get(it.kind, 0) + 1
    detail = ", ".join(f"{k} {n}" for k, n in sorted(kinds.items())) or "none"
    print(f"{Path(r.name).stem}: prose words {r.words} | sentences {r.sentences} | avg {r.average:.2f} | "
          f"FAIL {len(fails)} | INFO {len(infos)} | {detail}")
    return len(fails)


def main() -> int:
    ap = argparse.ArgumentParser(description="Check module sources against AUTHORING.md section 1.")
    ap.add_argument("paths", nargs="+", type=Path, help="module sources, e.g. src/lm08.md")
    ap.add_argument("--quiet", action="store_true", help="print the summary line per module only")
    ap.add_argument("--strict", action="store_true", help="apply the Volume II rules to every module")
    args = ap.parse_args()
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    fails = 0
    unreadable = False
    for path in args.paths:
        try:
            result = check(path, args.strict)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"{path}: cannot read ({exc})", file=sys.stderr)
            unreadable = True
            continue
        fails += report(result, args.quiet)
    return 2 if unreadable else (1 if fails else 0)


if __name__ == "__main__":
    sys.exit(main())
