#include "Common.h"

#include <Instrmnt.h>

#include <BandedWG.h>
#include <BlowBotl.h>
#include <BlowHole.h>
#include <Bowed.h>
#include <Brass.h>
#include <Clarinet.h>
#include <Drummer.h>

#include <FM.h>
#include <BeeThree.h>
#include <FMVoices.h>
#include <HevyMetl.h>
#include <PercFlut.h>
#include <Rhodey.h>
#include <TubeBell.h>
#include <Wurley.h>

#include <Flute.h>
#include <Mandolin.h>
#include <Mesh2D.h>

#include <Modal.h>
#include <ModalBar.h>

#include <Plucked.h>
#include <Recorder.h>
#include <Resonate.h>

#include <Sampler.h>
#include <Moog.h>

#include <Saxofony.h>
#include <Shakers.h>
#include <Simple.h>
#include <Sitar.h>
#include <StifKarp.h>
#include <VoicForm.h>
#include <Whistle.h>

namespace controls {
    control_ids bandedwg = {
        {"bow_pressure", 2},
        {"bow_motion", 4},
        // {"strike_position", 8}, (not implemented)
        {"vibrato_frequency", 11},
        {"gain", 1},
        {"bow_velocity", 128},
        {"set_striking", 64},
        {"instrument_presets", 16}
    };

    control_ids blowbotl = {
        {"noise_gain", 4},
        {"vibrato_frequency", 11},
        {"vibrato_gain", 1},
        {"volume", 128}
    };

    control_ids blowhole = {
        {"reed_stiffness", 2},
        {"noise_gain", 4},
        {"vibrato_frequency", 11},
        {"vibrato_gain", 1},
        {"breath_pressure", 128}
    };

    control_ids bowed = {
        {"bow_pressure", 2},
        {"bow_motion", 4},
        {"vibrato_frequency", 11},
        {"vibrato_gain", 1},
        {"bow_velocity", 100},
        {"frequency", 101},
        {"volume", 128},
    };

    control_ids brass = {
        {"lip_tension", 2},
        {"slide_length", 4},
        {"vibrato_frequency", 11},
        {"vibrato_gain", 1},
        {"volume", 128}
    };

    control_ids clarinet = {
        {"reed_stiffness", 2},
        {"noise_gain", 4},
        {"vibrato_frequency", 11},
        {"vibrato_gain", 1},
        {"breath_pressure", 128}
    };

    control_ids beethree = {
        {"operator_4_feedback_gain", 2},
        {"operator_3_gain", 4},
        {"lfo_speed", 11},
        {"lfo_depth", 1},
        {"adsr_2_4_target", 128}
    };

    control_ids fmvoices = {
        {"vowel", 2},
        {"spectral_tilt", 4},
        {"lfo_speed", 11},
        {"lfo_depth", 1},
        {"adsr_2_4_target", 128}
    };

    control_ids hevymetl = {
        {"total_modulator_index", 2},
        {"modulator_crossfade", 4},
        {"lfo_speed", 11},
        {"lfo_depth", 1},
        {"adsr_2_4_target", 128}
    };

    control_ids rhodey = {
        {"modulator_index_one", 2},
        {"crossfade_of_outputs", 4},
        {"lfo_speed", 11},
        {"lfo_depth", 1},
        {"adsr_2_4_target", 128}
    };

    control_ids flute = {
        {"jet_delay", 2},
        {"noise_gain", 4},
        {"vibrato_frequency", 11},
        {"vibrato_gain", 1},
        {"breath_pressure", 128}
    };

    control_ids mandolin = {
        {"body_size", 2},
        {"pluck_position", 4},
        {"string_sustain", 11},
        {"string_detuning", 1},
        {"microphone_position", 128}
    };

    control_ids mesh2d = {
        {"x_dimension", 2},
        {"y_dimension", 4},
        {"mesh_decay", 11},
        {"x_y_input_position", 1}
    };

    control_ids modalbar = {
        {"stick_hardness", 2},
        {"stick_position", 4},
        {"vibrato_gain", 1},
        {"vibrato_frequency", 11},
        {"direct_stick_mix", 8},
        {"volume", 128},
        {"modal_preset", 16}
    };

    control_ids recorder = {
        {"softness", 2},
        {"noise_gain", 4},
        {"noise_cutoff", 16},
        {"vibrato_frequency", 11},
        {"vibrato_gain", 1},
        {"breath_pressure", 128}
    };

    control_ids resonate = {
        {"resonance_frequency", 2},
        {"pole_radii", 4},
        {"notch_frequency", 11},
        {"zero_radii", 1},
        {"envelope_gain", 128}
    };

    control_ids moog = {
        {"filter_q", 2},
        {"filter_sweep_rate", 4},
        {"vibrato_frequency", 11},
        {"vibrato_gain", 1},
        {"gain", 128}
    };

    control_ids saxofony = {
        {"reed_stiffness", 2},
        {"reed_aperture", 26},
        {"noise_gain", 4},
        {"blow_position", 11},
        {"vibrato_frequency", 29},
        {"vibrato_gain", 1},
        {"breath_pressure", 128}
    };

    control_ids shakers = {
        {"shake_energy", 2},
        {"system_decay", 4},
        {"number_of_objects", 11},
        {"resonance_frequency", 1},
        {"shake_energy", 128},
        {"instrument_selection", 1071}
    };

    control_ids simple = {
        {"filter_pole_position", 2},
        {"noise_pitched_crossfade", 4},
        {"envelope_rate", 11},
        {"gain", 128}
    };

    control_ids stifkarp = {
        {"pickup_position", 4},
        {"string_sustain", 11},
        {"string_stretch", 1}
    };

    control_ids voicform = {
        {"voiced_unvoiced_mix", 2},
        {"vowel_phoneme_selection", 4},
        {"vibrato_frequency", 11},
        {"vibrato_gain", 1},
        {"loudness_spectral_tilt", 128}
    };

    control_ids whistle = {
        {"noise_gain", 4},
        {"fipple_modulation_frequency", 11},
        {"fipple_modulation_gain", 1},
        {"blowing_frequency_modulation", 2},
        {"volume", 128}
    };
}

namespace presets {
    control_ids bandedwg = {
        {"uniform_bar", 0},
        {"tuned_bar", 1},
        {"glass_harmonica", 2},
        {"tibetan_bowl", 3}
    };

    const std::map<std::string, StkFloat> drummer = {
        {"bass", midi_to_hz(36)},
        {"snare", midi_to_hz(38)},
        {"tomlo", midi_to_hz(41)},
        {"tommid", midi_to_hz(45)},
        {"tomhi", midi_to_hz(50)},
        {"hat", midi_to_hz(42)},
        {"ride", midi_to_hz(46)},
        {"crash", midi_to_hz(49)},
        {"cowbel", midi_to_hz(56)},
        {"tamb", midi_to_hz(54)},
        {"homer", midi_to_hz(90)}
    };

    control_ids modalbar = {
        {"marimba", 0},
        {"vibraphone", 1},
        {"agogo", 2},
        {"wood1", 3},
        {"reso", 4},
        {"wood2", 5},
        {"beats", 6},
        {"two_fixed", 7},
        {"clump", 8}
    };

    control_ids shakers = {
        {"maraca", 0},
        {"cabasa", 1},
        {"sekere", 2},
        {"tambourine", 3},
        {"sleigh_bells", 4},
        {"bamboo_chimes", 5},
        {"sand_paper", 6},
        {"coke_can", 7},
        {"sticks", 8},
        {"crunch", 9},
        {"big_rocks", 10},
        {"little_rocks", 11},
        {"next_mug", 12},
        {"penny_mug", 13},
        {"nickle_mug", 14},
        {"dime_mug", 15},
        {"quarter_mug", 16},
        {"franc_mug", 17},
        {"peso_mug", 18},
        {"guiro", 19},
        {"wrench", 20},
        {"water_drops", 21},
        {"tuned_bamboo_chimes", 22}
    };
}

mono_frames input_process_mesh2D(Mesh2D& self, const mono_frames& input, const controls_dict& controls) {
    const unsigned int n_channels = self.channelsOut();
    const unsigned long n_samples = input.shape(1);

    const auto data = new StkFloat[n_samples * n_channels];

    nb::capsule owner(data, [](void* p) noexcept {
        delete[] static_cast<StkFloat*>(p);
    });

    for (int n = 0; n < n_samples; n++) {
        for (const auto& [control, value] : controls) {
            self.controlChange(control, value(n));
        }

        data[n * n_channels] = self.inputTick(input(0, n));
    }
    return mono_frames(data, {1, n_samples}, owner);
}

void add_instrmnt_bindings(nb::module_& m) {
    nb::class_<Instrmnt>(m, "Instrmnt")
        .def("channels_out", &Instrmnt::channelsOut)
        .def("tick", &synth_with_controls<Instrmnt>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<BandedWG, Instrmnt>(m, "BandedWG")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::bandedwg)
        .def_ro_static("PRESET_IDS", &presets::bandedwg)
        .def("clear", &BandedWG::clear)
        .def("set_strike_position", &BandedWG::setStrikePosition)
        .def("set_preset", &BandedWG::setPreset)
        .def("set_frequency", &BandedWG::setFrequency)
        .def("start_bowing", &BandedWG::startBowing)
        .def("stop_bowing", &BandedWG::stopBowing)
        .def("pluck", &BandedWG::pluck)
        .def("note_on", &BandedWG::noteOn)
        .def("note_off", &BandedWG::noteOff)
        .def("control_change", &BandedWG::controlChange)
        .def("tick", [](BandedWG& self) { return self.tick(); })
        .def("tick", &synth_with_controls<BandedWG>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<BlowBotl, Instrmnt>(m, "BlowBotl")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::blowbotl)
        .def("clear", &BlowBotl::clear)
        .def("set_frequency", &BlowBotl::setFrequency)
        .def("start_blowing", &BlowBotl::startBlowing)
        .def("stop_blowing", &BlowBotl::stopBlowing)
        .def("note_on", &BlowBotl::noteOn)
        .def("note_off", &BlowBotl::noteOff)
        .def("control_change", &BlowBotl::controlChange)
        .def("tick", [](BlowBotl& self) { return self.tick(); })
        .def("tick", &synth_with_controls<BlowBotl>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<BlowHole, Instrmnt>(m, "BlowHole")
        .def(nb::init<StkFloat>(), "lowest_frequency"_a=8.0)
        .def_ro_static("CONTROL_IDS", &controls::blowhole)
        .def("clear", &BlowHole::clear)
        .def("set_frequency", &BlowHole::setFrequency)
        .def("set_tonehole", &BlowHole::setTonehole)
        .def("set_vent", &BlowHole::setVent)
        .def("start_blowing", &BlowHole::startBlowing)
        .def("stop_blowing", &BlowHole::stopBlowing)
        .def("note_on", &BlowHole::noteOn)
        .def("note_off", &BlowHole::noteOff)
        .def("control_change", &BlowHole::controlChange)
        .def("tick", [](BlowHole& self) { return self.tick(); })
        .def("tick", &synth_with_controls<BlowHole>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Bowed, Instrmnt>(m, "Bowed")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::bowed)
        .def("clear", &Bowed::clear)
        .def("set_frequency", &Bowed::setFrequency)
        .def("set_vibrato", &Bowed::setVibrato)
        .def("start_bowing", &Bowed::startBowing)
        .def("stop_bowing", &Bowed::stopBowing)
        .def("note_on", &Bowed::noteOn)
        .def("note_off", &Bowed::noteOff)
        .def("control_change", &Bowed::controlChange)
        .def("tick", [](Bowed& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Bowed>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Brass, Instrmnt>(m, "Brass")
        .def(nb::init<StkFloat>(), "lowest_frequency"_a=8.0)
        .def_ro_static("CONTROL_IDS", &controls::brass)
        .def("clear", &Brass::clear)
        .def("set_frequency", &Brass::setFrequency)
        .def("set_lip", &Brass::setLip)
        .def("start_blowing", &Brass::startBlowing)
        .def("stop_blowing", &Brass::stopBlowing)
        .def("note_on", &Brass::noteOn)
        .def("note_off", &Brass::noteOff)
        .def("control_change", &Brass::controlChange)
        .def("tick", [](Brass& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Brass>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Clarinet, Instrmnt>(m, "Clarinet")
        .def(nb::init<StkFloat>(), "lowest_frequency"_a=8.0)
        .def_ro_static("CONTROL_IDS", &controls::clarinet)
        .def("clear", &Clarinet::clear)
        .def("set_frequency", &Clarinet::setFrequency)
        .def("start_blowing", &Clarinet::startBlowing)
        .def("stop_blowing", &Clarinet::stopBlowing)
        .def("note_on", &Clarinet::noteOn)
        .def("note_off", &Clarinet::noteOff)
        .def("control_change", &Clarinet::controlChange)
        .def("tick", [](Clarinet& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Clarinet>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Drummer, Instrmnt>(m, "Drummer")
        .def(nb::init<>())
        .def_ro_static("INSTRUMENT_IDS", &presets::drummer)
        .def("note_on", &Drummer::noteOn)
        .def("note_off", &Drummer::noteOff)
        .def("tick", [](Drummer& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Drummer>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<FM, Instrmnt>(m, "FM")
        .def("load_waves", [](FM& self, const std::vector<std::string>& filenames) {
            std::vector<const char*> names(filenames.size());
            for (size_t i = 0; i < filenames.size(); i++) {
                names[i] = filenames[i].c_str();
            }
            self.loadWaves(names.data());
        })
        .def("set_frequency", &FM::setFrequency)
        .def("set_ratio", &FM::setRatio)
        .def("set_gain", &FM::setGain)
        .def("set_modulation_speed", &FM::setModulationSpeed)
        .def("set_modulation_depth", &FM::setModulationDepth)
        .def("set_control1", &FM::setControl1)
        .def("set_control2", &FM::setControl2)
        .def("key_on", &FM::keyOn)
        .def("key_off", &FM::keyOff)
        .def("note_off", &FM::noteOff)
        .def("control_change", &FM::controlChange);

    nb::class_<BeeThree, FM>(m, "BeeThree")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::beethree)
        .def("note_on", &BeeThree::noteOn)
        .def("tick", [](BeeThree& self) { return self.tick(); })
        .def("tick", &synth_with_controls<BeeThree>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<FMVoices, FM>(m, "FMVoices")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::fmvoices)
        .def("set_frequency", &FMVoices::setFrequency)
        .def("note_on", &FMVoices::noteOn)
        .def("control_change", &FMVoices::controlChange)
        .def("tick", [](FMVoices& self) { return self.tick(); })
        .def("tick", &synth_with_controls<FMVoices>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<HevyMetl, FM>(m, "HevyMetl")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::hevymetl)
        .def("note_on", &HevyMetl::noteOn)
        .def("tick", [](HevyMetl& self) { return self.tick(); })
        .def("tick", &synth_with_controls<HevyMetl>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<PercFlut, FM>(m, "PercFlut")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::hevymetl) // same values
        .def("set_frequency", &PercFlut::setFrequency)
        .def("note_on", &PercFlut::noteOn)
        .def("tick", [](PercFlut& self) { return self.tick(); })
        .def("tick", &synth_with_controls<PercFlut>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Rhodey, FM>(m, "Rhodey")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::rhodey)
        .def("set_frequency", &Rhodey::setFrequency)
        .def("note_on", &Rhodey::noteOn)
        .def("tick", [](Rhodey& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Rhodey>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<TubeBell, FM>(m, "TubeBell")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::rhodey) // same values
        .def("note_on", &TubeBell::noteOn)
        .def("tick", [](TubeBell& self) { return self.tick(); })
        .def("tick", &synth_with_controls<TubeBell>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Wurley, FM>(m, "Wurley")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::rhodey) // same values
        .def("set_frequency", &Wurley::setFrequency)
        .def("note_on", &Wurley::noteOn)
        .def("tick", [](Wurley& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Wurley>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Flute, Instrmnt>(m, "Flute")
        .def(nb::init<StkFloat>(), "lowest_frequency"_a=8.0)
        .def_ro_static("CONTROL_IDS", &controls::flute)
        .def("clear", &Flute::clear)
        .def("set_frequency", &Flute::setFrequency)
        .def("set_jet_reflection", &Flute::setJetReflection)
        .def("set_end_reflection", &Flute::setEndReflection)
        .def("set_jet_delay", &Flute::setJetDelay)
        .def("start_blowing", &Flute::startBlowing)
        .def("stop_blowing", &Flute::stopBlowing)
        .def("note_on", &Flute::noteOn)
        .def("note_off", &Flute::noteOff)
        .def("control_change", &Flute::controlChange)
        .def("tick", [](Flute& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Flute>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Mandolin, Instrmnt>(m, "Mandolin")
        .def(nb::init<StkFloat>(), "lowest_frequency"_a=8.0)
        .def_ro_static("CONTROL_IDS", &controls::mandolin)
        .def("clear", &Mandolin::clear)
        .def("set_detune", &Mandolin::setDetune)
        .def("set_body_size", &Mandolin::setBodySize)
        .def("set_pluck_position", &Mandolin::setPluckPosition)
        .def("set_frequency", &Mandolin::setFrequency)
        .def("pluck", nb::overload_cast<StkFloat>(&Mandolin::pluck))
        .def("pluck", nb::overload_cast<StkFloat, StkFloat>(&Mandolin::pluck))
        .def("note_on", &Mandolin::noteOn)
        .def("note_off", &Mandolin::noteOff)
        .def("control_change", &Mandolin::controlChange)
        .def("tick", [](Mandolin& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Mandolin>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Mesh2D, Instrmnt>(m, "Mesh2D")
        .def(nb::init<unsigned short, unsigned short>(), "n_x"_a, "n_y"_a)
        .def_ro_static("CONTROL_IDS", &controls::mesh2d)
        .def("clear", &Mesh2D::clear)
        .def("set_n_x", &Mesh2D::setNX)
        .def("set_n_y", &Mesh2D::setNY)
        .def("set_input_position", &Mesh2D::setInputPosition)
        .def("set_decay", &Mesh2D::setDecay)
        .def("note_on", &Mesh2D::noteOn)
        .def("note_off", &Mesh2D::noteOff)
        .def("energy", &Mesh2D::energy)
        .def("control_change", &Mesh2D::controlChange)
        .def("tick", nb::overload_cast<unsigned int>(&Mesh2D::tick))
        .def("input_tick", &Mesh2D::inputTick)
        .def("tick", &synth_with_controls<Mesh2D>, "n_samples"_a, "controls"_a=controls_dict{})
        .def("tick", &input_process_mesh2D, "input"_a, "controls"_a=controls_dict{});

    nb::class_<Modal, Instrmnt>(m, "Modal")
        .def("clear", &Modal::clear)
        .def("set_frequency", &Modal::setFrequency)
        .def("set_ratio_and_radius", &Modal::setRatioAndRadius)
        .def("set_master_gain", &Modal::setMasterGain)
        .def("set_direct_gain", &Modal::setDirectGain)
        .def("set_mode_gain", &Modal::setModeGain)
        .def("strike", &Modal::strike)
        .def("damp", &Modal::damp)
        .def("note_on", &Modal::noteOn)
        .def("note_off", &Modal::noteOff)
        .def("tick", [](Modal& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Modal>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<ModalBar, Modal>(m, "ModalBar")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::modalbar)
        .def_ro_static("PRESET_IDS", &presets::modalbar)
        .def("clear", &ModalBar::clear)
        .def("set_stick_hardness", &ModalBar::setStickHardness)
        .def("set_strike_position", &ModalBar::setStrikePosition)
        .def("set_preset", &ModalBar::setPreset)
        .def("set_modulation_depth", &ModalBar::setModulationDepth)
        .def("control_change", &ModalBar::controlChange);

    nb::class_<Plucked, Instrmnt>(m, "Plucked")
        .def(nb::init<StkFloat>(), "lowest_frequency"_a=10.0)
        .def("clear", &Plucked::clear)
        .def("set_frequency", &Plucked::setFrequency)
        .def("pluck", &Plucked::pluck)
        .def("note_on", &Plucked::noteOn)
        .def("note_off", &Plucked::noteOff)
        .def("control_change", &Plucked::controlChange)
        .def("tick", [](Plucked& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Plucked>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Recorder, Instrmnt>(m, "Recorder")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::recorder)
        .def("clear", &Recorder::clear)
        .def("set_frequency", &Recorder::setFrequency)
        .def("start_blowing", &Recorder::startBlowing)
        .def("stop_blowing", &Recorder::stopBlowing)
        .def("note_on", &Recorder::noteOn)
        .def("note_off", &Recorder::noteOff)
        .def("control_change", &Recorder::controlChange)
        .def("tick", [](Recorder& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Recorder>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Resonate, Instrmnt>(m, "Resonate")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::resonate)
        .def("set_resonance", &Resonate::setResonance)
        .def("set_notch", &Resonate::setNotch)
        .def("set_equal_gain_zeroes", &Resonate::setEqualGainZeroes)
        .def("key_on", &Resonate::keyOn)
        .def("key_off", &Resonate::keyOff)
        .def("note_on", &Resonate::noteOn)
        .def("note_off", &Resonate::noteOff)
        .def("control_change", &Resonate::controlChange)
        .def("tick", [](Resonate& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Resonate>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Sampler, Instrmnt>(m, "Sampler")
        .def("key_on", &Sampler::keyOn)
        .def("key_off", &Sampler::keyOff)
        .def("note_off", &Sampler::noteOn)
        .def("tick", [](Sampler& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Sampler>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Moog, Sampler>(m, "Moog")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::moog)
        .def("set_frequency", &Moog::setFrequency)
        .def("note_on", &Moog::noteOn)
        .def("set_modulation_speed", &Moog::setModulationSpeed)
        .def("set_modulation_depth", &Moog::setModulationDepth)
        .def("control_change", &Moog::controlChange)
        .def("tick", [](Moog& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Moog>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Saxofony, Instrmnt>(m, "Saxofony")
        .def(nb::init<StkFloat>(), "lowest_frequency"_a=8.0)
        .def_ro_static("CONTROL_IDS", &controls::saxofony)
        .def("clear", &Saxofony::clear)
        .def("set_frequency", &Saxofony::setFrequency)
        .def("set_blow_position", &Saxofony::setBlowPosition)
        .def("start_blowing", &Saxofony::startBlowing)
        .def("stop_blowing", &Saxofony::stopBlowing)
        .def("note_on", &Saxofony::noteOn)
        .def("note_off", &Saxofony::noteOff)
        .def("control_change", &Saxofony::controlChange)
        .def("tick", [](Saxofony& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Saxofony>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Shakers, Instrmnt>(m, "Shakers")
        .def(nb::init<int>(), "type"_a=0)
        .def_ro_static("CONTROL_IDS", &controls::shakers)
        .def_ro_static("PRESET_IDS", &presets::shakers)
        .def("note_on", &Shakers::noteOn)
        .def("note_off", &Shakers::noteOff)
        .def("control_change", &Shakers::controlChange)
        .def("tick", [](Shakers& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Shakers>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Simple, Instrmnt>(m, "Simple")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::simple)
        .def("set_frequency", &Simple::setFrequency)
        .def("key_on", &Simple::keyOn)
        .def("key_off", &Simple::keyOff)
        .def("note_on", &Simple::noteOn)
        .def("note_off", &Simple::noteOff)
        .def("control_change", &Simple::controlChange)
        .def("tick", [](Simple& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Simple>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Sitar, Instrmnt>(m, "Sitar")
        .def(nb::init<StkFloat>(), "lowest_frequency"_a=8.0)
        .def("clear", &Sitar::clear)
        .def("set_frequency", &Sitar::setFrequency)
        .def("note_on", &Sitar::noteOn)
        .def("note_off", &Sitar::noteOff)
        .def("control_change", &Sitar::controlChange)
        .def("tick", [](Sitar& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Sitar>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<StifKarp, Instrmnt>(m, "StifKarp")
        .def(nb::init<StkFloat>(), "lowest_frequency"_a=8.0)
        .def_ro_static("CONTROL_IDS", &controls::stifkarp)
        .def("clear", &StifKarp::clear)
        .def("set_frequency", &StifKarp::setFrequency)
        .def("set_stretch", &StifKarp::setStretch)
        .def("set_pickup_position", &StifKarp::setPickupPosition)
        .def("set_base_loop_gain", &StifKarp::setBaseLoopGain)
        .def("pluck", &StifKarp::pluck)
        .def("note_on", &StifKarp::noteOn)
        .def("note_off", &StifKarp::noteOff)
        .def("control_change", &StifKarp::controlChange)
        .def("tick", [](StifKarp& self) { return self.tick(); })
        .def("tick", &synth_with_controls<StifKarp>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<VoicForm, Instrmnt>(m, "VoicForm")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::voicform)
        .def("clear", &VoicForm::clear)
        .def("set_frequency", &VoicForm::setFrequency)
        .def("set_phoneme", [](VoicForm& self, const std::string& phoneme) {
            return self.setPhoneme(phoneme.c_str());
        })
        .def("set_voiced", &VoicForm::setVoiced)
        .def("set_unvoiced", &VoicForm::setUnVoiced)
        .def("set_filter_sweep_rate", &VoicForm::setFilterSweepRate)
        .def("set_pitch_sweep_rate", &VoicForm::setPitchSweepRate)
        .def("speak", &VoicForm::speak)
        .def("quiet", &VoicForm::quiet)
        .def("note_on", &VoicForm::noteOn)
        .def("note_off", &VoicForm::noteOff)
        .def("control_change", &VoicForm::controlChange)
        .def("tick", [](VoicForm& self) { return self.tick(); })
        .def("tick", &synth_with_controls<VoicForm>, "n_samples"_a, "controls"_a=controls_dict{});

    nb::class_<Whistle, Instrmnt>(m, "Whistle")
        .def(nb::init<>())
        .def_ro_static("CONTROL_IDS", &controls::whistle)
        .def("clear", &Whistle::clear)
        .def("set_frequency", &Whistle::setFrequency)
        .def("start_blowing", &Whistle::startBlowing)
        .def("stop_blowing", &Whistle::stopBlowing)
        .def("note_on", &Whistle::noteOn)
        .def("note_off", &Whistle::noteOff)
        .def("control_change", &Whistle::controlChange)
        .def("tick", [](Whistle& self) { return self.tick(); })
        .def("tick", &synth_with_controls<Whistle>, "n_samples"_a, "controls"_a=controls_dict{});
}