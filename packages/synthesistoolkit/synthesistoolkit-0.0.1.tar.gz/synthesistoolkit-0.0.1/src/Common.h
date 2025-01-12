#ifndef PYSTKCOMMON_H
#define PYSTKCOMMON_H

#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/map.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>

#include <Stk.h>

namespace nb = nanobind;
using namespace nb::literals;
using namespace stk;

template<int CHANNELS=-1>
using audio_frames = nb::ndarray<nb::numpy, StkFloat, nb::shape<CHANNELS, -1>>;

typedef nb::ndarray<nb::numpy, StkFloat, nb::shape<1, -1>> mono_frames;
typedef nb::ndarray<nb::numpy, StkFloat, nb::shape<2, -1>> stereo_frames;
typedef std::map<int, nb::ndarray<StkFloat, nb::ndim<1>>> controls_dict;
typedef const std::map<std::string, int> control_ids;

inline StkFloat midi_to_hz(int midi) {
    return 220.0 * pow(2.0, (midi - 57.0) / 12.0);
}

template<typename T>
mono_frames synth_with_controls(T& self, const unsigned long n_samples, const controls_dict& controls) {
    const auto data = new StkFloat[n_samples];

    nb::capsule owner(data, [](void* p) noexcept {
        delete[] static_cast<StkFloat*>(p);
    });

    for (int n = 0; n < n_samples; n++) {
        for (const auto& [control, value] : controls) {
            self.controlChange(control, value(n));
        }
        data[n] = self.tick();
    }
    return mono_frames(data, {1, n_samples}, owner);
}

template<typename T>
mono_frames process_with_controls(T& self, const mono_frames& input, const controls_dict& controls) {
    unsigned long n_samples = input.shape(1);
    const auto data = new StkFloat[n_samples];

    nb::capsule owner(data, [](void* p) noexcept {
        delete[] static_cast<StkFloat*>(p);
    });

    for (int n = 0; n < n_samples; n++) {
        for (const auto& [control, value] : controls) {
            self.controlChange(control, value(n));
        }
        data[n] = self.tick(input(1, n));
    }
    return mono_frames(data, {1, n_samples}, owner);
}

template<int OUT=-1>
audio_frames<OUT> stkframes_to_numpy(StkFrames& frames) {
    unsigned long n_channels = OUT;
    if (n_channels == -1) n_channels = frames.channels();

    const auto data = new StkFloat[frames.frames() * n_channels];

    nb::capsule owner(data, [](void* p) noexcept {
        delete[] static_cast<StkFloat*>(p);
    });

    for (int n = 0; n < frames.frames(); n++) {
        for (int c = 0; c < n_channels; c++) {
            data[n * n_channels + c] = frames(n, c);
        }
    }
    return audio_frames<OUT>(data, {n_channels, frames.frames()}, owner);
}

template<typename T>
audio_frames<1> generate(T& self, int n_samples) {
    StkFrames frames(n_samples, 1);
    self.tick(frames);
    return stkframes_to_numpy<1>(frames);
}

template<typename T, int IN=1, int OUT=1>
audio_frames<OUT> process_input(T& self, const audio_frames<IN>& input) {
    int n_samples = input.shape(1);
    StkFrames frames(n_samples, std::max(IN, OUT));
    for (int n = 0; n < n_samples; n++) {
        for (int i = 0; i < IN; i++) {
            frames(n, i) = input(i, n);
        }
    }
    self.tick(frames);
    return stkframes_to_numpy<OUT>(frames);
}

#endif //PYSTKCOMMON_H
