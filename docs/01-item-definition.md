# 1. Item definition

Before listing hazards, ISO 12100 asks you to fix the **limits of the machine**: what it is, what it is used for, who comes near it, and over which phases of its life. Hazards found later only make sense against these limits.

## The cell

A six-axis collaborative robot arm stands on a table in front of a CNC milling machine. It picks raw parts from a tray, loads them into the machine, and places finished parts in a second tray. An operator refills and empties the trays while the robot keeps working. There is no fence.

| Property | Value |
|---|---|
| Robot | 6-axis collaborative arm with joint torque sensing |
| Payload | 14 kg rated; workpiece plus gripper about 6 kg |
| Reach | 1.4 m |
| Maximum tool speed | 2 m/s outside the collaborative workspace |
| Tool | Two-finger electric gripper, self-locking on power loss |
| Collaboration method | Power and force limiting (PFL) with safely limited speed |
| Workpieces | Machined aluminium blocks, up to 4 kg, with machined edges |

## Intended use

- Loading and unloading one CNC machine in an industrial workshop
- Indoor, normal lighting, level floor
- One operator at a time in the collaborative workspace

## Reasonably foreseeable misuse

ISO 12100 requires this to be considered, because people do not always follow the manual.

- Operator leans over the table to grab a part instead of waiting
- Operator reaches into the gripper to free a jammed part without pausing the robot
- Gripper or payload changed without updating the safety parameters
- A second person enters the workspace to talk to the operator

## People

| Role | Training | Where they are |
|---|---|---|
| Operator | Instructed in the cell's operation | Inside the collaborative workspace several times per hour |
| Programmer | Trained on the robot | Next to the arm while teaching, occasionally |
| Maintenance electrician | Qualified electrician | At the controller cabinet, occasionally |
| Bystander | None | Should stay outside the marked area |

## Life cycle phases considered

Automatic operation, setting and teaching, cleaning and jam clearing, maintenance.

Transport, installation and decommissioning are **out of scope** for this example.

## Workspace limits

- **Collaborative workspace:** the area over the two trays where operator and robot can be present together. Marked on the floor.
- **Machine side:** inside the CNC enclosure. The operator cannot reach it while the machine door is closed. The CNC machine's own safety (door interlock, spindle) is out of scope.

## Assumptions

Every number that the analysis depends on but that could not be measured is listed here, so a reviewer can challenge it.

| ID | Assumption |
|---|---|
| A-1 | The robot's safety controller offers the safety functions used here as certified functions |
| A-2 | 140 N is the quasi-static force limit for hand and chest in ISO/TS 15066 Annex A. To be verified against the standard |
| A-3 | A 500 ms emergency stop time is achievable at full speed and payload |
| A-4 | 250 mm/s keeps contact forces below the limit. Must be confirmed by force measurement on the real cell |
| A-5 | An upper safety plane at 1.3 m keeps the arm below the head of a standing adult |
| A-6 | 20 mm of sag on brake engagement cannot trap a hand in this layout |
| A-7 | A 24 hour brake test interval matches the diagnostic coverage needed for PL d |

## Open points

| ID | Open point |
|---|---|
| OP-1 | H-01 uses P1 (avoidance possible). If full-speed motion in the collaborative workspace is considered unavoidable, the result becomes PL e. Needs review by an experienced assessor |
| OP-2 | The 2025 edition of ISO 10218 defines requirements per safety function. This concept has not been compared against it clause by clause |
| OP-3 | Contact with the face and head is treated as not permitted at all. SF-04 must therefore exclude it, not merely limit the force |
