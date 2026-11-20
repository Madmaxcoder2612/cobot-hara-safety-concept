# 7. Achieved Performance Level

The safety concept sets a **target** PL for every safety function (PL d). This document shows the next step: given the failure rates of the parts, which PL does the function actually **achieve**, and is that enough?

## The idea

A safety function is a chain: a sensor or input, a logic unit, and an output that brings the arm to its safe state. If any part fails dangerously, the whole function fails. For parts in series, the average probabilities of dangerous failure per hour (PFHd) simply add up:

```text
PFHd_total = PFHd_input + PFHd_logic + PFHd_output
```

ISO 13849-1 then maps the total to a Performance Level:

| PL | PFHd per hour |
|---|---|
| a | 1e-5 to below 1e-4 |
| b | 3e-6 to below 1e-5 |
| c | 1e-6 to below 3e-6 |
| d | 1e-7 to below 1e-6 |
| e | 1e-8 to below 1e-7 |

The code is [tools/achieved_pl.py](../tools/achieved_pl.py).

## Worked example: safely limited speed (SF-03)

The target of SF-03 is PL d, so the three parts together must stay below 1e-6 per hour. The values below are **invented for illustration**. They are not from any data sheet.

| Subsystem | Role | PFHd (assumed) |
|---|---|---|
| Joint encoders | Measure joint speed | 2.0e-7 |
| Safety controller | Compares speed with the limit | 1.5e-7 |
| Drive safety function | Brakes and holds the arm | 3.0e-7 |
| **Total** | | **6.5e-7** |

```bash
python tools/achieved_pl.py 2e-7 1.5e-7 3e-7 --target d
```

```text
subsystems: 3, total PFHd = 6.5e-07 1/h
achieved PL (from PFHd alone): d
target PL d: met
```

The total is inside the PL d band (1e-7 to 1e-6), so the target is met. The margin is small: the total can only grow by a factor of about 1.5 before PL d is lost.

## What the numbers teach

1. **The chain is only as good as its sum.** Three parts that are each PL d can add up to PL c. With four parts of 4e-7 each, the total is 1.6e-6 and the function drops to PL c.
2. **One weak part decides.** Replacing one subsystem with a PL c component (1.5e-6) makes the whole chain PL c, however good the others are.
3. **Spend effort where the largest share is.** Improving a 1e-8 part changes nothing when another part contributes 3e-7.

## Limitations

- **PFHd is necessary, not sufficient.** A real PL d claim also needs the required category (here category 3), diagnostic coverage, common cause failure measures, and measures against systematic faults. This tool combines PFHd values. It does not check any of these.
- **The PFHd of each subsystem has to come from somewhere.** In practice it is the manufacturer's data sheet value, or a calculation from MTTFd, DC and category (ISO 13849-1, Annex K). That calculation is not implemented here.
- **Values are assumed.** The example numbers are not measured and are not from a real product.
- **Band limits from public summaries.** Check them against the purchased standard before any real use.
- **Series only.** Redundant structures inside a subsystem are already reflected in the PFHd that the subsystem reports. Combining subsystems in parallel is not modelled.
