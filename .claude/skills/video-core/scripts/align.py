#!/usr/bin/env python3
"""Forced alignment with torchaudio MMS_FA. Never guess timings: every word gets its time from the audio.

    python3 align.py AUDIO TEXT OUT.json [--windows lines.json] [--pad 0.3] [--max-word 1.2] [--offset 0]

TEXT is UTF-8, one line (one sung line / spoken line / point) per row. Supported row forms:
    plain text                          -> speaker ""
    SPEAKER|text                        -> speaker label kept per line
    text (ad-lib in brackets)           -> bracketed words aligned too, marked "adlib": true
    # comment / blank rows              -> ignored
Any script works: Devanagari, Gurmukhi, Urdu, Latin. Each word is romanised with uroman for the aligner;
the original spelling is what goes on screen ("w"), the romanisation is kept as "roman".

Output JSON:
  {"audio":..., "duration":s, "lines":[{"i","speaker","text","start","end",
     "words":[{"w","roman","start","end","adlib","score"}]}]}

--windows: a JSON list of [start,end] per line (or a previous align output). Each line is then aligned
only inside its own window (+-pad). Use it when a line looks squeezed, for party/rap hooks, or for long files.
--max-word caps a word that stretches over a pause (its end is pulled in to start+max).
"""
import argparse, json, re, sys, unicodedata
import torch, torchaudio

def load_audio(path, sr):
    try:
        wav, s = torchaudio.load(path)
    except Exception:  # mp3/m4a without a torchaudio backend: decode with ffmpeg
        import subprocess, numpy as np
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
        return torch.from_numpy(np.frombuffer(raw, dtype=np.float32).copy())[None]
    wav = wav.mean(0, keepdim=True)
    return torchaudio.functional.resample(wav, s, sr) if s != sr else wav

_ur = None
def romanize(word):
    global _ur
    if re.fullmatch(r"[A-Za-z' -]+", word):
        r = word
    else:
        if _ur is None:
            import uroman
            _ur = uroman.Uroman()
        r = _ur.romanize_string(word)
    r = unicodedata.normalize("NFKD", r).lower()
    r = re.sub(r"[^a-z']", "", r)
    return r

NUM = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"}

def parse(text_path):
    lines = []
    for raw in open(text_path, encoding="utf-8"):
        row = raw.strip()
        if not row or row.startswith("#"):
            continue
        spk = ""
        if "|" in row and len(row.split("|", 1)[0]) <= 24:
            spk, row = [x.strip() for x in row.split("|", 1)]
        words, adlib = [], False
        for tok in re.findall(r"\(|\)|\[|\]|[^\s()\[\]]+", row):
            if tok in "([": adlib = True; continue
            if tok in ")]": adlib = False; continue
            disp = tok.strip()
            core = re.sub(r"^[\"'“‘«(]+|[\"'”’»),.!?;:।॥…-]+$", "", disp)
            roman = romanize(core) or "".join(NUM.get(ch, "") for ch in core)
            words.append({"w": disp, "roman": roman, "adlib": adlib})
        if words:
            lines.append({"speaker": spk, "text": row, "words": words})
    return lines

def trellis_align(emission, tokens, blank=0):
    """CTC Viterbi (same as torchaudio tutorial). emission: [T,C] log-probs. returns per-token frame index list."""
    T, N = emission.size(0), len(tokens)
    if N == 0 or T < N:
        return None
    trellis = torch.full((T + 1, N + 1), -float("inf"))
    trellis[0, 0] = 0
    trellis[1:, 0] = torch.cumsum(emission[:, blank], 0)
    tok = torch.tensor(tokens)
    for t in range(T):
        trellis[t + 1, 1:] = torch.maximum(trellis[t, 1:] + emission[t, blank], trellis[t, :-1] + emission[t, tok])
    # backtrack
    j, path = N, []
    for t in range(T - 1, -1, -1):
        if j == 0:
            break
        stay = trellis[t, j] + emission[t, blank]
        change = trellis[t, j - 1] + emission[t, tokens[j - 1]]
        if change > stay:
            path.append((j - 1, t, float(emission[t, tokens[j - 1]].exp())))
            j -= 1
    if j != 0:
        return None
    return path[::-1]  # (token_index, frame, prob)

class Aligner:
    def __init__(self):
        self.bundle = torchaudio.pipelines.MMS_FA
        self.model = self.bundle.get_model(with_star=False).eval()
        self.dict = self.bundle.get_dict(star=None)
        self.sr = self.bundle.sample_rate

    @torch.inference_mode()
    def emission(self, wav):
        chunk = self.sr * 30  # 30 s windows keep memory flat on long files
        outs = []
        for a in range(0, wav.size(1), chunk):
            e, _ = self.model(wav[:, a:a + chunk])
            outs.append(torch.log_softmax(e[0], -1))
        return torch.cat(outs, 0)

    def align_words(self, wav, words, t_offset):
        em = self.emission(wav)
        ratio = wav.size(1) / em.size(0) / self.sr
        toks, owner = [], []
        for wi, w in enumerate(words):
            for ch in w["roman"]:
                if ch in self.dict:
                    toks.append(self.dict[ch]); owner.append(wi)
        path = trellis_align(em, toks, blank=0)
        if path is None:
            return False
        spans = {}
        for ti, frame, p in path:
            wi = owner[ti]
            s = spans.setdefault(wi, [frame, frame, []])
            s[0] = min(s[0], frame); s[1] = max(s[1], frame); s[2].append(p)
        for wi, w in enumerate(words):
            if wi in spans:
                a, b, ps = spans[wi]
                w["start"] = round(t_offset + a * ratio, 3)
                w["end"] = round(t_offset + (b + 1) * ratio, 3)
                w["score"] = round(sum(ps) / len(ps), 3)
        return True

def fill_untimed(words):
    """Words with no alignable letters (emoji, digits-only) get the gap between neighbours."""
    for i, w in enumerate(words):
        if "start" in w:
            continue
        prev = next((x["end"] for x in reversed(words[:i]) if "end" in x), None)
        nxt = next((x["start"] for x in words[i + 1:] if "start" in x), None)
        a = prev if prev is not None else (nxt - 0.3 if nxt is not None else 0)
        b = nxt if nxt is not None else a + 0.3
        w["start"], w["end"], w["score"] = round(a, 3), round(max(b, a + 0.05), 3), 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio"); ap.add_argument("text"); ap.add_argument("out")
    ap.add_argument("--windows"); ap.add_argument("--pad", type=float, default=0.3)
    ap.add_argument("--max-word", type=float, default=1.2)
    ap.add_argument("--offset", type=float, default=0.0, help="seconds to add (if AUDIO is a cut of the song)")
    a = ap.parse_args()

    lines = parse(a.text)
    al = Aligner()
    wav = load_audio(a.audio, al.sr)
    dur = wav.size(1) / al.sr
    if a.windows:
        win = json.load(open(a.windows))
        win = [[l["start"], l["end"]] for l in win["lines"]] if isinstance(win, dict) else win
        assert len(win) == len(lines), f"{len(win)} windows for {len(lines)} lines"
        for line, (s, e) in zip(lines, win):
            s0, e0 = max(0, s - a.pad), min(dur, e + a.pad)
            seg = wav[:, int(s0 * al.sr):int(e0 * al.sr)]
            if not al.align_words(seg, line["words"], s0):
                print(f"warn: line did not fit its window: {line['text'][:40]}", file=sys.stderr)
    else:
        allw = [w for l in lines for w in l["words"]]
        if not al.align_words(wav, allw, 0.0):
            sys.exit("alignment failed: the text is longer than the audio allows. Check the text matches the audio, or pass --windows.")
    for line in lines:
        fill_untimed(line["words"])
        for w in line["words"]:
            if w["end"] - w["start"] > a.max_word:
                w["end"] = round(w["start"] + a.max_word, 3)
            w["start"] = round(w["start"] + a.offset, 3); w["end"] = round(w["end"] + a.offset, 3)
        line["start"], line["end"] = line["words"][0]["start"], line["words"][-1]["end"]
    for i, line in enumerate(lines):
        line["i"] = i
    # squeezed-line report: very fast words usually mean the line belongs elsewhere -> re-run with --windows
    for line in lines:
        n = len(line["words"]); span = line["end"] - line["start"]
        if n > 2 and span / n < 0.09:
            print(f"warn: line {line['i']} looks squeezed ({span:.2f}s for {n} words): re-align it with --windows", file=sys.stderr)
    json.dump({"audio": a.audio, "duration": round(dur + a.offset, 3), "lines": lines}, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(f"aligned {sum(len(l['words']) for l in lines)} words in {len(lines)} lines -> {a.out}")

if __name__ == "__main__":
    main()
