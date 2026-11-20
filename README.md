# Cobot cell: hazard analysis and safety concept

[![CI](https://github.com/Madmaxcoder2612/cobot-hara-safety-concept/actions/workflows/ci.yml/badge.svg)](https://github.com/Madmaxcoder2612/cobot-hara-safety-concept/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Status: learning project](https://img.shields.io/badge/status-learning%20project-orange)

A worked example of the first half of the functional safety lifecycle for a collaborative robot arm that tends a CNC machine while an operator shares its workspace, with no fence.

It goes from **"what can hurt someone?"** to **"what must the control system do about it, and how would we prove it does?"**, and a script checks that the chain from hazard to test has no gaps.

> **Learning project.** The cell is fictional. Nothing here has been validated on real hardware or reviewed by a certified safety engineer. Limit values taken from standards come from public summaries and must be checked against the purchased standard before any real use. See [Limitations](#limitations).

## Contents

- [The chain](#the-chain)
- [Result in numbers](#result-in-numbers)
- [Documents](#documents)
- [Quick start](#quick-start)
- [How it works](#how-it-works)
- [Repository layout](#repository-layout)
- [Standards used](#standards-used)
- [Limitations](#limitations)
- [Next steps](#next-steps)

## The chain

Every safety requirement in a safety case should be traceable back to a hazard and forward to a test. This project keeps that chain in plain CSV files and checks it automatically.

```mermaid
flowchart LR
    H["Hazard<br/>(S, F, P rating)"] --> PL["Required PL<br/>(ISO 13849-1 risk graph)"]
    PL --> SF["Safety function<br/>(target PL d, cat. 3)"]
    SF --> SR["Safety requirement"]
    SR --> TC["Test case"]
```

If a safety function has no hazard behind it, a requirement has no test, or a target PL is lower than the PL the hazards demand, the check fails.

## Result in numbers

| | |
|---|---|
| Hazards analysed | 12, across automatic operation, teaching, jam clearing and maintenance |
| Safety functions | 7, each targeted at PL d, category 3 |
| Safety requirements | 20, each with a test case |
| Test cases | 20 (11 test, 5 measurement, 3 inspection, 1 analysis) |
| Hazards handled without a control safety function | 2 (design and information only) |

## Results at a glance

**Every hazard is covered, and every function is at least as strong as the hazards behind it.** Two hazards need no control function at all, because design and information measures are enough.

![Matrix of hazards against safety functions, coloured by required Performance Level](docs/figures/coverage-matrix.svg)

**A stop is not instant, so the speed limit decides how close the arm may come to a protected zone.** At the 250 mm/s collaborative limit the tool travels about 30 mm after the stop command. At full speed it travels more than 500 mm. The model uses assumed values; see [stopping distance](docs/06-stopping-distance.md).

![Stopping distance against tool speed](docs/figures/stopping-distance.svg)

## Documents

Read them in this order if the topic is new to you.

| # | Document | Question it answers |
|---|---|---|
| 1 | [Method](docs/02-hara-method.md) | What do hazard, risk and Performance Level mean, and how is PLr found? Start here if you are new |
| 2 | [Item definition](docs/01-item-definition.md) | What is the machine, who uses it, which assumptions and open points exist? |
| 3 | [HARA table](docs/04-hara-table.md) | Which hazards exist and what PLr does each one need? |
| 4 | [Safety concept](docs/03-safety-concept.md) | Which safety functions reduce the risk, and what is the safe state? |
| 5 | [Traceability matrix](docs/05-traceability-matrix.md) | How does each hazard connect to requirements and tests? |
| 6 | [Stopping distance](docs/06-stopping-distance.md) | How far does the arm travel after a stop command, and what does that mean for the limits? |
| 7 | [Achieved PL](docs/07-achieved-pl.md) | Do the failure rates of the parts add up to the PL the safety function is supposed to reach? |

The HARA table, traceability matrix, figures and stopping distance table are generated from the CSV files in [data/](data/) and the model in [tools/](tools/). Edit the data, not the generated files.

## Quick start

Requires Python 3.10 or newer. There are no packages to install.

```bash
git clone https://github.com/Madmaxcoder2612/cobot-hara-safety-concept.git
cd cobot-hara-safety-concept
```

Run the consistency check. It regenerates both tables in `docs/`:

```bash
python tools/traceability.py
```

Expected output:

```text
12 hazards, 7 safety functions, 20 requirements, 20 test cases
All traceability checks passed.
```

Regenerate the figures and the stopping distance table:

```bash
python tools/figures.py
```

Run the unit tests, which include every path of the ISO 13849-1 risk graph:

```bash
python -m unittest discover tests
```

Ask the risk graph directly for the required PL of a single hazard (severity, frequency, avoidance):

```bash
python tools/plr.py S2 F1 P2
```

Combine the PFHd values of the subsystems in one safety function and compare with the target PL (exit code 1 if the target is missed):

```bash
python tools/achieved_pl.py 2e-7 1.5e-7 3e-7 --target d
```

Calculate the stopping distance at one speed in m/s, optionally with your own reaction time in s and deceleration in m/s²:

```bash
python tools/stopping_distance.py 0.25
python tools/stopping_distance.py 0.25 0.2 4
```

## How it works

| File | Role |
|---|---|
| [data/hazards.csv](data/hazards.csv) | One row per hazard with S, F, P, rationale and measures |
| [data/safety_functions.csv](data/safety_functions.csv) | Trigger, reaction, safe state and target PL of each function |
| [data/requirements.csv](data/requirements.csv) | Requirement text, linked to a safety function |
| [data/test_cases.csv](data/test_cases.csv) | Method, procedure and pass criterion, linked to a requirement |
| [tools/plr.py](tools/plr.py) | The ISO 13849-1 risk graph as code |
| [tools/traceability.py](tools/traceability.py) | Checks the chain and writes the generated tables |
| [tools/stopping_distance.py](tools/stopping_distance.py) | Stopping distance and time after a stop command |
| [tools/figures.py](tools/figures.py) | Draws the SVG figures and writes the stopping distance table |
| [tools/achieved_pl.py](tools/achieved_pl.py) | Adds up subsystem PFHd values and reads off the achieved PL |

The checks it performs:

- IDs are unique in every file
- S, F and P values are valid
- Every hazard has a safety function or at least one design or information measure
- Every safety function is justified by at least one hazard
- No safety function has a target PL below the highest PLr of the hazards it covers
- Every safety function has a requirement, and every requirement has a test case

GitHub Actions runs the check and the tests on every push, and also fails if any generated file in `docs/` is out of date.

## Repository layout

```text
.
├── data/                  CSV source of truth
├── docs/                  Method, item definition, safety concept, generated tables
│   └── figures/           Generated SVG figures and stopping distance table
├── tools/                 Risk graph, traceability check, stopping distance model, figures
├── tests/                 Unit tests
└── .github/workflows/     CI
```

## Standards used

| Standard | Used for |
|---|---|
| ISO 12100 | Risk assessment method and the three-step risk reduction order |
| ISO 13849-1 | Risk graph, required Performance Level, categories |
| ISO 10218-1 / -2 | Robot and robot cell safety requirements |
| ISO/TS 15066 | Contact force limits for power and force limiting |
| ISO 13850 | Emergency stop |
| IEC 61800-5-2 | Names of the drive safety functions (STO, SS1, SLS, SLP, SBC) |
| IEC 60204-1 | Stop categories and electrical equipment |

The standards themselves are copyrighted and are not included here.

## Limitations

- **Fictional cell, no real measurements.** Test cases describe what would be measured; none has been run.
- **Unverified numbers.** The 140 N force limit, the 250 mm/s speed limit and the PL d / category 3 default are listed as assumptions in the [item definition](docs/01-item-definition.md) and need checking against the standards.
- **ISO 10218:2025 not compared clause by clause.** Listed as an open point.
- **Simple stopping model.** Constant deceleration with an assumed reaction time and rate (A-8). Real values come from the robot manufacturer's data and measurement.
- **Target, not proof.** The concept sets a PL target. [Achieved PL](docs/07-achieved-pl.md) adds up PFHd values, but the values in the example are invented, and a real claim also needs category, diagnostic coverage, common cause failure and systematic fault measures.
- **Not covered:** FMEA and FTA of individual safety functions, speed and separation monitoring, transport, installation and decommissioning.

## Next steps

1. Calculate the PFHd of one subsystem from category, MTTFd, DC and CCF (ISO 13849-1, Annex K), instead of taking it as an input.
2. FMEA and FTA of the Safe Torque Off function.
3. Safety logic for the emergency stop and safely limited speed in IEC 61131-3 Structured Text.
4. A Simulink or Stateflow model of the emergency stop and safe standstill logic.

## License

[MIT](LICENSE)
