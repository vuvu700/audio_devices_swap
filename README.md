# Audio Device Auto-Swap (Windows)

Small Python utility built with Pycaw to **switch audio output devices on the fly** and automatically select the most relevant input device.

## Overview

This script:
* Cycles to the **next available output device**
* Automatically selects an **input (microphone)** whose *physical device name closely matches* the chosen output device

This is useful for setups where headsets, USB audio interfaces, or Bluetooth devices expose both input/output endpoints with similar names.

---
## How It Works
1. Retrieves all active:
   * Output devices (speakers, headphones)
   * Input devices (microphones)
2. Detects the current default output device
3. Selects the **next output device** in the list (cyclic)
4. Extracts its **physical name**
5. Uses fuzzy matching (`difflib`) to find the closest input device based on:
   * Physical device name similarity
   * Threshold defined by `PHYS_NAME_CLOSENESS`
6. Sets both:
   * New output device
   * Matched input device
     as system defaults

---
## Requirements
* Python 3.10+
* Windows OS
* Dependencies:

```bash
pip install pycaw
```

---
## Usage
Run the script:
```bash
python main.py
```

Each execution will:
* Switch to the next output device
* Automatically align the microphone
* Print the updated device list

---
## Example Output
```
Output devices:
 * Headphones (USB Audio Device)
   Speakers (Realtek Audio)

Input devices:
 * Headset Mic (USB Audio Device)
   Microphone (Realtek Audio)
```

---
## Configuration

### Matching Sensitivity
```python
PHYS_NAME_CLOSENESS = 0.6
```
* Increase → stricter matching
* Decrease → more permissive matching

---
## Limitations
* Relies on **device naming consistency** (not guaranteed across drivers)
* Uses heuristic matching (may fail if names differ significantly)
* Only cycles forward (no reverse or direct selection)
* Depends on Windows Core Audio behavior via Pycaw

---
## License

MIT