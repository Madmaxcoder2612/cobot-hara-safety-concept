# 3. Safety concept

The safety concept answers one question per safety function: **what triggers it, what does the robot do, and what state counts as safe?**

## Safe state

For this cell the safe state is **standstill**. There are two kinds, and choosing between them is a design decision:

| State | Drive function | Torque | Used when |
|---|---|---|---|
| Monitored standstill | SOS (after SS2) | On, position held and monitored | Short stops where the robot should continue afterwards |
| Torque off | STO (after SS1, or directly) | Off, brakes applied | Emergency stop, faults, and whenever a person's hands are in the tool |

Standstill is not automatically safe. An arm that stops while clamping a hand is still hurting someone, which is why SF-02 also requires that no clamping force is held (SR-07), and why SF-07 exists for the moment torque disappears.

## Safety functions

| ID | Function | Trigger | Reaction | Target |
|---|---|---|---|---|
| SF-01 | Emergency stop | E-stop device pressed | Controlled stop, then torque off (SS1 → STO) | PL d, cat. 3 |
| SF-02 | Power and force limiting | Contact force or joint torque above limit | Protective stop, arm can be pushed away | PL d, cat. 3 |
| SF-03 | Safely limited speed | Tool speed above limit | Protective stop | PL d, cat. 3 |
| SF-04 | Safely limited position | Arm approaches a safety plane | Stop before the plane | PL d, cat. 3 |
| SF-05 | Safe standstill, no unexpected start-up | Joint moves while paused | Torque off (STO) | PL d, cat. 3 |
| SF-06 | Enabling device in manual mode | Enabling device released or pressed fully | Protective stop | PL d, cat. 3 |
| SF-07 | Safe brake control and brake test | Torque removed, power lost, or brake test failed | Brakes applied; operation blocked | PL d, cat. 3 |

The exact requirement wording is in [data/requirements.csv](../data/requirements.csv), and the link back to hazards is in the [traceability matrix](05-traceability-matrix.md).

## Why every function is PL d

The risk graph gives PL d for most hazards and PL c for two (H-05 and H-10). All functions are still targeted at PL d because:

- ISO 10218-1 has historically required PL d with category 3 for a robot's safety-related control system unless the risk assessment justifies otherwise.
- One safety controller implements all functions, so a lower target for two of them saves nothing.

Choosing a higher PL than required is always allowed. Choosing a lower one never is.

## How the functions work together

Power and force limiting alone is not enough. The force in a collision depends on how fast the arm was moving, so the force limit only holds if the speed is limited too. That gives a chain:

1. **SF-04** keeps the arm away from the head, where no contact is acceptable.
2. **SF-03** keeps speed low enough that a collision stays within the force limit.
3. **SF-02** detects the contact and stops.
4. **SF-07** holds the arm once torque is gone.
5. **SF-01** is there for whatever the others did not foresee.

SF-05 and SF-06 cover the two situations where a person deliberately puts their hands near the tool: clearing a jam and teaching.

## Architecture

Category 3 for each function means, in principle:

- **Two independent channels** from sensor to actuator. For example, two position encoders per joint, two processors in the safety controller, and two ways of removing torque.
- **Cross-monitoring** between the channels, so a disagreement is detected and leads to the safe state.
- **A single fault does not cause loss of the safety function.**

This concept assumes the robot manufacturer supplies these functions as certified functions of the safety controller (assumption A-1). The integrator's job is then to configure them correctly, protect the configuration (SR-08), and validate the result on the real cell.

## Parameter integrity

Hazard H-12 is the one that is easiest to overlook. Every limit in this concept is a number someone types into the safety configuration. If the payload is entered as 2 kg when it is 6 kg, force estimation is wrong and SF-02 no longer protects anyone, even though every component works.

The concept therefore requires password protection and a checksum for the safety configuration (SR-08), plus a validation checklist after every change.

## Validation approach

Each requirement has one test case with a method:

| Method | Meaning | Count |
|---|---|---|
| Test | Trigger the function and observe the reaction | 11 |
| Measurement | Record a physical value with a calibrated instrument | 5 |
| Inspection | Compare configuration or documents with the specification | 3 |
| Analysis | Calculation or reasoning | 1 |

Force measurement (TC-05) is the one that decides whether the cell is acceptable. The speed limit of 250 mm/s is a starting value and must be lowered if the measured forces are too high.
