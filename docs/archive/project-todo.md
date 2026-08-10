# TODO

## Completed 2026-08-10

- [x] Remove mock training data.
- [x] Add explicit DEBUG, TRAINING, and LIVE modes.
- [x] Add ECHO_ON/ECHO_OFF plus MODE?/STATUS/HELP commands.
- [x] Repair framed 50-sample idle capture and collect 15 real idle trials.
- [x] Make training/export reject missing configured classes.
- [x] Make export fail closed and replace artifacts atomically.
- [x] Train and export the real five-class MLP (75 balanced windows).
- [x] Implement 0.2 s LIVE stride, three-window smoothing, and 300 ms debounce.
- [x] Compile and flash TinyML_Node1.
- [x] Verify mode transitions, sensor health, inference timing, and a short stationary LIVE run.

## Remaining validation

- [ ] Run controlled LIVE trials for all four active gestures and record LED/EVENT results.
- [ ] Run at least five minutes stationary and report false events per minute.
- [ ] Add a Python/C++ golden-vector preprocessing and score parity test.
- [ ] Collect more session- and user-varied trials, especially tap2/tap3.
