# PySTK: Python bindings for the Synthesis ToolKit

Python bindings for the [Synthesis ToolKit in C++ (STK)](https://ccrma.stanford.edu/software/stk/) by Perry R. Cook and Gary P. Scavone, powered by [nanobind](https://github.com/wjakob/nanobind).

The bindings allow access to all classes that implement synthesis algorithms:

- `stk::Effect` and all derived classes
- `stk::Filter` and all derived classes
- `stk::Function` and all derived classes
- `stk::Generator` and all derived classes
- `stk::Guitar`
- `stk::Instrmnt` and all derived classes
- `stk::Phonemes`
- `stk::Twang`
- `stk::Voicer`

A lot of the functionality of other classes (File IO, Networking) can likely be substituted by common Python libraries, but might be added to the bindings as needed.

## Installation

The bindings are available as prebuilt wheels for Linux, Windows and MacOS:

```
pip install synthesistoolkit
```

Alternatively, you can build the bindings from source:

```
git clone --recurse-submodules git@github.com:dsuedholt/pystk.git
cd pysdt && pip install .
```

## Usage

Documentation for the Python bindings is not yet available, but the API is almost identical to the C++ API documented [here](https://ccrma.stanford.edu/software/stk/).

The `rawwaves` folder is included in the distribution and its path is set in `__init__.py`.

`tick(...)` methods that deal with `stk::StkFrames` return a `numpy.ndarray` with the audio data.

```python
import synthesistoolkit as stk
import numpy as np

# important: initialize sample rate before doing anything else
sr = 44100
stk.set_sample_rate(sr)

clnt = stk.Clarinet()
clnt.set_frequency(220)

# for classes that support control changes: see available control change numbers
print(stk.Clarinet.CONTROL_IDS)
# {'breath_pressure': 128,
#  'noise_gain': 4,
#  'reed_stiffness': 2,
#  'vibrato_frequency': 11,
#  'vibrato_gain': 1}

# control changes can be set directly
clnt.control_change(stk.Clarinet.CONTROL_IDS['reed_stiffness'], 1.8)

# or passed as a dictionary of audio rate parameters
controls = {
    stk.Clarinet.CONTROL_IDS['breath_pressure']: np.linspace(80, 40, num=sr),
    stk.Clarinet.CONTROL_IDS['vibrato_gain']: np.linspace(0, 90, num=sr),
}

audio = clnt.tick(sr, controls=controls)
print(audio.shape) # (1, 44100)

# can now use the audio in any way you like, for example:
import soundfile as sf
sf.write('clarinet.wav', audio[0, :], sr)
```