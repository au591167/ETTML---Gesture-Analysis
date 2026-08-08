# TODO
## Reset mock model + add output toggle

- [x] Plan and get approval
- [ ] Edit main.cpp: add gEchoInference bool + ECHO_ON/ECHO_OFF commands; gate inference & STATUS prints
- [ ] Delete Product/data/raw/gesture_mock_002.csv (remove mock training data)
- [ ] Run export_model.py to regenerate neutral idle-fallback model
- [ ] Recompile firmware
- [ ] Flash to TinyML_Node1
- [ ] Verify: no false tap3 when stationary; ECHO_OFF stops flooding; ECHO_ON restores
