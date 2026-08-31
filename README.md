# PIOS — Personal Intelligence Operating System

> Athena is its default Mentor Agent. A curriculum defines *what* to learn; PIOS
> decides *what to learn today, why, to what depth, and what comes next* — and keeps
> an honest, verifiable record of how you actually grow over years.

PIOS is not a task manager or a note app. It is a local-first operating system for a
person's long-term growth: an append-only stream of everything you do, a knowledge
graph of what you know, and a record of the decisions you make — with an AI mentor that
*proposes* but never decides. Everything else (skill scores, capability, a digital twin,
a timeline) is a **projection** over that data and can be rebuilt from scratch at any time.

## Two repositories: a public system + private data

Per [Constitution](Constitution.md) Article 5 (personal knowledge belongs to the user),
PIOS is split into two git repos:

```
pios (public)        the software — code, docs, templates. Clone it and run your own PIOS.
└── vault/ (private) a nested private repo (pios-vault): the owner's personal data.
```

The public repo `.gitignore`s `vault/`, so personal data never enters public history.

## Two states (No Hidden State)

```
Immutable (facts, git-tracked in vault/)
    vault/events/*.jsonl · vault/proposals/*.jsonl · vault/briefings/ · vault/**/*.md
Derived (projections, safe to destroy and recompute)
    pios.db · every score and view
```

The test (Constitution Article 9): `rm pios.db && pios rebuild` must reproduce it exactly.

## Documentation (three tiers)

```
Constitution.md      Why & non-negotiables   — the supreme law, rarely changes
docs/DESIGN/         What (the whole system) — 8 chapters, readable in an hour
docs/PRINCIPLES.md   design-philosophy cheat sheet
docs/rfc/            How (each decision)     — one at a time, grows on demand
```

Reading order for a new reader: this README → [Constitution](Constitution.md) →
[docs/DESIGN/](docs/DESIGN/README.md) → the code.

## Layout

```
[public repo: pios]
Constitution.md        the constitution (13 articles)
README.md              this file
docs/PRINCIPLES.md     principles · four-object worldview · success metrics · death traps
docs/DESIGN/           system design (8 chapters) · docs/rfc/  design decisions
schema.sql             schema for the derived index
templates/             decision / idea / experiment templates
agents/mentor/         Athena's daily-briefing prompt
collectors/            L0 collectors (e.g. projects.py — auto-syncs ~/Projects git repos)
engines/               L2 engines (Phase 1+)
scripts/pios.py        the CLI

[private repo: vault/ (pios-vault)]
vault/events/YYYY/MM.jsonl     event stream (append-only; a source of truth)
vault/proposals/YYYY/MM.jsonl  AI proposals + your verdicts (also facts)
vault/briefings/               daily briefings (historical record)
vault/identity/                profile & role profiles
vault/curriculum/              structured course DAGs + degree requirements
vault/concepts/ papers/ projects/ people/   graph entities
vault/ideas/ decisions/ experiments/        research & decision records
vault/journal/ milestones/
```

## Quick start

```bash
python3 scripts/pios.py init                                  # build the derived index
python3 scripts/pios.py log lecture --entity concept:x --depth 1
python3 scripts/pios.py events                                # last 7 days
python3 scripts/pios.py rebuild                               # drop & recompute (Article 9)
```

Record a decision / idea / experiment: copy the matching file from `templates/` into
`vault/decisions|ideas|experiments/`, fill it in, and `pios rebuild` folds it into the graph.

## Evidence depth ladder

Every skill/knowledge score traces to events, each tagged with a depth — so reading can
never masquerade as ability:

```
1  heard    (lecture / skim)
2  understood (close reading + summary)
3  used     (exercise / lab / hands-on)
4  built    (implemented from scratch / a project)
5  taught   (blog / explained to someone)
```

## Roadmap

- **Phase 0 (now)** — scaffold + event stream + manual logging + daily briefing.
  Milestone: **14 consecutive days of briefings acted on**.
- **Phase 1 (semester 1)** — collectors (GitHub / papers / courses) + Skill Engine v1
  (evidence depth × diversity) + FSRS memory + proposal approval loop + weekly review +
  monthly spot-checks.
- **Phase 2 (semester 2)** — nightly Reflection Pass (reschedule / merge-idea / exploration
  proposals) + Capability aggregation + Twin gap analysis.
- **Phase 3 (year 2+)** — Time Machine timeline + calibration curve (Brier) +
  Investment/Career projections + Dashboard.

## License & scope

A personal-infrastructure project, built and maintained by one person over an undergraduate
degree. The moat is not the ~300 lines of code — it is the years of high-quality events,
knowledge graph, decisions, and capability trajectory that accrue in the private vault.
Data is the asset; code is consumable.
