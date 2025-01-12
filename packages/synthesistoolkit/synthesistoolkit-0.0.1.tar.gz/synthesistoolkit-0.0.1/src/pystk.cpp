#include "Common.h"

#include <Guitar.h>
#include <Phonemes.h>
#include <Twang.h>
#include <Voicer.h>

void add_instrmnt_bindings(nb::module_& m);
void add_effects_bindings(nb::module_& m);
void add_filter_bindings(nb::module_& m);
void add_function_bindings(nb::module_& m);
void add_generator_bindings(nb::module_& m);

namespace controls {
    control_ids guitar = {
        {"bridge_coupling_gain", 2},
        {"pluck_position", 4},
        {"loop_gain", 11},
        {"coupling_filter_pole", 1},
        {"pick_filter_pole", 128}
    };
}

NB_MODULE(_pystk_impl, m) {
    m.def("sample_rate", &Stk::sampleRate);
    m.def("set_sample_rate", &Stk::setSampleRate);
    m.def("rawwave_path", &Stk::rawwavePath);
    m.def("set_rawwave_path", &Stk::setRawwavePath);

    add_instrmnt_bindings(m);
    add_effects_bindings(m);
    add_filter_bindings(m);
    add_function_bindings(m);
    add_generator_bindings(m);

    nb::class_<Guitar>(m, "Guitar")
        .def(nb::init<unsigned int, std::string>(), "n_strings"_a=6, "bodyfile"_a="")
        .def_ro_static("CONTROL_IDS", &controls::guitar)
        .def("clear", &Guitar::clear)
        .def("set_body_file", &Guitar::setBodyFile, "bodyfile"_a="")
        .def("set_pluck_position", &Guitar::setPluckPosition, "position"_a, "string"_a=-1)
        .def("set_loop_gain", &Guitar::setLoopGain, "gain"_a, "string"_a=-1)
        .def("set_frequency", &Guitar::setFrequency, "frequency"_a, "string"_a=0)
        .def("note_on", &Guitar::noteOn, "frequency"_a, "amplitude"_a, "string"_a=0)
        .def("note_off", &Guitar::noteOff, "amplitude"_a, "string"_a=0)
        .def("control_change", &Guitar::controlChange, "number"_a, "value"_a, "string"_a=-1)
        .def("last_out", &Guitar::lastOut)
        .def("tick", nb::overload_cast<StkFloat>(&Guitar::tick), "input"_a=0.0)
        .def("tick", synth_with_controls<Guitar>, "n_samples"_a, "controls"_a=controls_dict{})
        .def("tick", process_with_controls<Guitar>, "input"_a, "controls"_a = controls_dict{});

    nb::class_<Phonemes>(m, "Phonemes")
        .def_static("name", [](unsigned int i) { return std::string(Phonemes::name(i)); }, "index"_a)
        .def_static("voice_gain", &Phonemes::voiceGain, "index"_a)
        .def_static("noise_gain", &Phonemes::noiseGain, "index"_a)
        .def_static("formant_frequency", &Phonemes::formantFrequency, "index"_a, "partial"_a)
        .def_static("formant_radius", &Phonemes::formantRadius, "index"_a, "partial"_a)
        .def_static("formant_gain", &Phonemes::formantGain, "index"_a, "partial"_a);

    nb::class_<Twang>(m, "Twang")
        .def(nb::init<StkFloat>(), "lowest_frequency"_a=50.0)
        .def("clear", &Twang::clear)
        .def("set_lowest_frequency", &Twang::setLowestFrequency, "frequency"_a)
        .def("set_frequency", &Twang::setFrequency, "frequency"_a)
        .def("set_pluck_position", &Twang::setPluckPosition, "position"_a)
        .def("set_loop_gain", &Twang::setLoopGain, "gain"_a)
        .def("set_loop_filter", &Twang::setLoopFilter, "coefficients"_a)
        .def("last_out", &Twang::lastOut)
        .def("tick", nb::overload_cast<StkFloat>(&Twang::tick), "input"_a=0.0)
        .def("tick", &process_input<Twang, 1, 1>, "input"_a);

    nb::class_<Voicer>(m, "Voicer")
        .def(nb::init<StkFloat>(), "decay_time"_a=0.2)
        .def("add_instrument", &Voicer::addInstrument, "instrument"_a, "group"_a=0)
        .def("remove_instrument", &Voicer::removeInstrument, "instrument"_a)
        .def("note_on", &Voicer::noteOn, "note_number"_a, "amplitude"_a, "group"_a=0)
        .def("note_off", nb::overload_cast<StkFloat, StkFloat, int>(&Voicer::noteOff), "note_number"_a, "amplitude"_a, "group"_a=0)
        .def("note_off", nb::overload_cast<long, StkFloat>(&Voicer::noteOff), "tag"_a, "amplitude"_a)
        .def("set_frequency", nb::overload_cast<StkFloat, int>(&Voicer::setFrequency), "note_number"_a, "group"_a=0)
        .def("set_frequency", nb::overload_cast<long, StkFloat>(&Voicer::setFrequency), "tag"_a, "note_number"_a)
        .def("pitch_bend", nb::overload_cast<StkFloat, int>(&Voicer::pitchBend), "value"_a, "group"_a=0)
        .def("pitch_bend", nb::overload_cast<long, StkFloat>(&Voicer::pitchBend), "tag"_a, "value"_a)
        .def("control_change", nb::overload_cast<int, StkFloat, int>(&Voicer::controlChange), "number"_a, "value"_a, "group"_a=0)
        .def("control_change", nb::overload_cast<long, int, StkFloat>(&Voicer::controlChange), "tag"_a, "number"_a, "value"_a)
        .def("silence", &Voicer::silence)
        .def("channels_out", &Voicer::channelsOut)
        .def("last_frame", &Voicer::lastFrame)
        .def("last_out", &Voicer::lastOut)
        .def("tick", nb::overload_cast<unsigned int>(&Voicer::tick), "input"_a=0)
        .def("tick", synth_with_controls<Voicer>, "n_samples"_a, "controls"_a=controls_dict{});
}