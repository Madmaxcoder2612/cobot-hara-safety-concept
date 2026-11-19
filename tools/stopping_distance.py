"""Stopping distance of the robot tool after a stop command.

Model: after the stop is triggered, nothing happens for a reaction time
(detection, safety controller, drive), then the arm decelerates at a constant
rate until it stands still.

    distance = v * t_react + v**2 / (2 * decel)
    time     = t_react + v / decel

This is a deliberately simple model. The two parameters below are ASSUMED
values for this fictional cell (assumption A-8 in docs/01-item-definition.md).
For a real robot, use the stopping time and stopping distance data that the
manufacturer publishes for each payload, speed and pose, and confirm them by
measurement.

Usage:
    python tools/stopping_distance.py              # table with default values
    python tools/stopping_distance.py 0.25         # one speed in m/s
    python tools/stopping_distance.py 0.25 0.2 4   # speed, reaction time s, decel m/s^2
"""

import math
import sys

DEFAULT_T_REACT = 0.10  # s, assumed
DEFAULT_DECEL = 6.0  # m/s^2, assumed
STOP_TIME_LIMIT = 0.5  # s, requirement SR-04


def stopping_distance(v, t_react=DEFAULT_T_REACT, decel=DEFAULT_DECEL):
    """Distance in metres travelled after the stop command at speed v (m/s)."""
    _check(v, t_react, decel)
    return v * t_react + v * v / (2 * decel)


def stopping_time(v, t_react=DEFAULT_T_REACT, decel=DEFAULT_DECEL):
    """Time in seconds from the stop command to standstill at speed v (m/s)."""
    _check(v, t_react, decel)
    return t_react + v / decel


def max_speed(distance, t_react=DEFAULT_T_REACT, decel=DEFAULT_DECEL):
    """Highest speed (m/s) that still stops within the given distance (m)."""
    _check(0.0, t_react, decel)
    if distance < 0:
        raise ValueError("distance must not be negative")
    return decel * (-t_react + math.sqrt(t_react**2 + 2 * distance / decel))


def _check(v, t_react, decel):
    if v < 0 or t_react < 0:
        raise ValueError("speed and reaction time must not be negative")
    if decel <= 0:
        raise ValueError("deceleration must be positive")


def main(argv):
    t_react, decel = DEFAULT_T_REACT, DEFAULT_DECEL
    if len(argv) >= 3:
        t_react = float(argv[2])
    if len(argv) >= 4:
        decel = float(argv[3])
    speeds = [float(argv[1])] if len(argv) >= 2 else [0.1, 0.25, 0.5, 1.0, 1.5, 2.0]

    print(f"Reaction time {t_react} s, deceleration {decel} m/s^2 (assumed values)")
    print(f"{'speed [m/s]':>12} {'distance [mm]':>14} {'time [ms]':>10}  SR-04 (<= 500 ms)")
    for v in speeds:
        t = stopping_time(v, t_react, decel)
        verdict = "ok" if t <= STOP_TIME_LIMIT else "FAILS"
        print(f"{v:>12.2f} {stopping_distance(v, t_react, decel) * 1000:>14.0f} "
              f"{t * 1000:>10.0f}  {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
