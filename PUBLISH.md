# Publishing this repository

Everything is committed and checked. Publishing is two decisions and one command.

## State

- Results: `results/locomo/locomo-definitive-20260917` (the figures in
  WEBSITE-FIGURES.md), `results/locomo/fullrun-conv-20260916` (the public engine
  before PR #23) and `results/locomo/fullrun-conv-20260809` (a development engine), each
  with its provenance. `python scripts/verify_definitive.py` recomputes the definitive
  figures from the committed files.
- No LoCoMo text is committed; see `results/locomo/locomo-definitive-20260917/REDACTIONS.md`.
  CI refuses a committed `locomo10.json`.
- `config/locomo.json` pins the engine at `3df1a4d` on branch
  `bench/locomo-conventions-reader-width`, and `python reproduce.py` reproduces both
  figures end to end.

## Checklist

1. **Decide LoCoMo's commercial-use question.** LoCoMo is CC BY-NC 4.0: non-commercial use
   with attribution. This repository does not redistribute it; `reproduce.py` downloads it
   from its authors, and the README states the licence. What is open is whether quoting
   LoCoMo figures on a commercial product site is within non-commercial use. Options: ask
   the dataset authors (snap-research/locomo) for permission; quote the figures only in
   research-framed material; or accept the reading that reporting a benchmark score is not
   use of the data. This is the owner's decision.
2. **Keep the engine commit fetchable.** `3df1a4d` lives on the engine branch
   `bench/locomo-conventions-reader-width`. Open a pull request from it, or merge it, so the
   commit survives the branch being deleted; a pull request also gives `config/locomo.json`
   a `refs/pull/<n>/head` refspec, as PR #16 does for the earlier pin.
3. **Choose which runs stay published.** `fullrun-conv-20260809` comes from an engine commit
   that is not in the public repository. Keep it with that noted in its provenance, or
   remove it with `git rm -r results/locomo/fullrun-conv-20260809` and its README row.
4. **Confirm Apache-2.0** for this repository's code.
5. **Flip the repository public:**

       gh repo edit devon-clarkk/engraphy-benchmarks --visibility public --accept-visibility-change-consequences

For a reproduction without a Claude subscription, merge engine PR #8 (an
OpenAI-compatible route) and move the engine pin to a commit carrying it.
