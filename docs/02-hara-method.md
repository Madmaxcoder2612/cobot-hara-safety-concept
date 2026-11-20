# 2. Method

## The words

| Term | Meaning | Example from this cell |
|---|---|---|
| Hazard | A potential source of harm | The moving arm |
| Hazardous situation | A person is exposed to the hazard | The operator's hand is in the tray while the arm approaches |
| Harm | The injury | Crushed fingers |
| Risk | Severity of the harm combined with how likely it is | |
| Safety function | A function of the control system whose failure increases risk | Stop when contact force exceeds 140 N |

## Risk reduction order (ISO 12100)

Risk is reduced in a fixed order. You may only move to the next step when the previous one is not enough.

1. **Inherently safe design.** Remove the hazard or make it harmless: round edges, lower mass, a gripper that keeps hold without power.
2. **Safeguarding.** Guards and safety functions of the control system. This is where functional safety lives.
3. **Information for use.** Training, signs, protective equipment. Weakest, because it depends on people.

This is why two hazards in the table (H-06 falling workpiece, H-11 electric shock) have no safety function: steps 1 and 3 deal with them.

## From risk to required Performance Level

When a safety function is used, ISO 13849-1 asks how reliable it must be. The answer is the **required Performance Level (PLr)**, from **a** (lowest) to **e** (highest). It comes from three questions:

| Parameter | Question | Low | High |
|---|---|---|---|
| **S** Severity | How bad is the injury? | S1: slight, normally heals | S2: serious, normally permanent, or death |
| **F** Frequency | How often or how long is a person exposed? | F1: seldom, or short | F2: frequent, or long |
| **P** Possibility of avoidance | Can the person get out of the way? | P1: possible under some conditions | P2: scarcely possible |

The three answers lead through the risk graph:

| S | F | P | PLr |
|---|---|---|---|
| S1 | F1 | P1 | a |
| S1 | F1 | P2 | b |
| S1 | F2 | P1 | b |
| S1 | F2 | P2 | c |
| S2 | F1 | P1 | c |
| S2 | F1 | P2 | d |
| S2 | F2 | P1 | d |
| S2 | F2 | P2 | e |

The same table is implemented in [tools/plr.py](../tools/plr.py).

## Two rules that are easy to get wrong

**Estimate the risk without the safety function.** The question is how bad things would be if the function were absent or failed. If you assume the force limit already works, every hazard looks harmless and nothing needs a PL.

**The safety function inherits the highest PLr of the hazards it covers.** Power and force limiting (SF-02) covers four hazards. It must meet the most demanding one.

## What a Performance Level means

A PL is a band of **probability of dangerous failure per hour**. PL d means between one in a million and one in ten million per hour. Whether a real design reaches its PL depends on four things:

- **Category:** the architecture. Category 3 means two channels, so a single fault does not cause loss of the safety function.
- **MTTFd:** mean time to dangerous failure of the components.
- **DC:** diagnostic coverage, the share of dangerous faults that are detected.
- **CCF:** measures against common cause failures that would defeat both channels at once.

This document stops at setting the target. How failure rates of the parts add up to an achieved PL is shown in [Achieved PL](07-achieved-pl.md).
