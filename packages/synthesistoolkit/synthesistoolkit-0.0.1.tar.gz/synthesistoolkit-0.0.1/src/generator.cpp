#include "Common.h"

#include <Generator.h>
#include <ADSR.h>
#include <Asymp.h>
#include <Blit.h>
#include <BlitSaw.h>
#include <BlitSquare.h>
#include <Envelope.h>
#include <Granulate.h>
#include <Modulate.h>
#include <Noise.h>
#include <SineWave.h>
#include <SingWave.h>

void add_generator_bindings(nb::module_& m) {
    nb::class_<Generator>(m, "Generator")
        .def("channels_out", &Generator::channelsOut)
        .def("last_frame", &Generator::lastFrame);

    nb::class_<ADSR, Generator>(m, "ADSR")
        .def(nb::init<>())
        .def("key_on", &ADSR::keyOn)
        .def("key_off", &ADSR::keyOff)
        .def("set_attack_rate", &ADSR::setAttackRate)
        .def("set_attack_target", &ADSR::setAttackTarget)
        .def("set_decay_rate", &ADSR::setDecayRate)
        .def("set_sustain_level", &ADSR::setSustainLevel)
        .def("set_release_rate", &ADSR::setReleaseRate)
        .def("set_attack_time", &ADSR::setAttackTime)
        .def("set_decay_time", &ADSR::setDecayTime)
        .def("set_release_time", &ADSR::setReleaseTime)
        .def("set_all_times", &ADSR::setAllTimes)
        .def("set_target", &ADSR::setTarget)
        .def("get_state", &ADSR::getState)
        .def("set_value", &ADSR::setValue)
        .def("last_out", &ADSR::lastOut)
        .def("tick", nb::overload_cast<>(&ADSR::tick))
        .def("tick", &generate<ADSR>);

    nb::class_<Asymp, Generator>(m, "Asymp")
        .def(nb::init<>())
        .def("key_on", &Asymp::keyOn)
        .def("key_off", &Asymp::keyOff)
        .def("set_tau", &Asymp::setTau)
        .def("set_time", &Asymp::setTime)
        .def("set_t60", &Asymp::setT60)
        .def("set_target", &Asymp::setTarget)
        .def("set_value", &Asymp::setValue)
        .def("get_state", &Asymp::getState)
        .def("last_out", &Asymp::lastOut)
        .def("tick", nb::overload_cast<>(&Asymp::tick))
        .def("tick", &generate<Asymp>);

    nb::class_<Blit, Generator>(m, "Blit")
        .def(nb::init<StkFloat>(), "frequency"_a=220.0)
        .def("reset", &Blit::reset)
        .def("set_phase", &Blit::setPhase)
        .def("get_phase", &Blit::getPhase)
        .def("set_frequency", &Blit::setFrequency)
        .def("set_harmonics", &Blit::setHarmonics)
        .def("last_out", &Blit::lastOut)
        .def("tick", nb::overload_cast<>(&Blit::tick))
        .def("tick", &generate<Blit>);

    nb::class_<BlitSaw, Generator>(m, "BlitSaw")
        .def(nb::init<StkFloat>(), "frequency"_a=220.0)
        .def("reset", &BlitSaw::reset)
        .def("set_frequency", &BlitSaw::setFrequency)
        .def("set_harmonics", &BlitSaw::setHarmonics)
        .def("last_out", &BlitSaw::lastOut)
        .def("tick", nb::overload_cast<>(&BlitSaw::tick))
        .def("tick", &generate<BlitSaw>);

    nb::class_<BlitSquare, Generator>(m, "BlitSquare")
        .def(nb::init<StkFloat>(), "frequency"_a=220.0)
        .def("reset", &BlitSquare::reset)
        .def("set_phase", &BlitSquare::setPhase)
        .def("get_phase", &BlitSquare::getPhase)
        .def("set_frequency", &BlitSquare::setFrequency)
        .def("set_harmonics", &BlitSquare::setHarmonics)
        .def("last_out", &BlitSquare::lastOut)
        .def("tick", nb::overload_cast<>(&BlitSquare::tick))
        .def("tick", &generate<BlitSquare>);

    nb::class_<Envelope, Generator>(m, "Envelope")
        .def(nb::init<>())
        .def("key_on", &Envelope::keyOn)
        .def("key_off", &Envelope::keyOff)
        .def("set_rate", &Envelope::setRate)
        .def("set_time", &Envelope::setTime)
        .def("set_target", &Envelope::setTarget)
        .def("set_value", &Envelope::setValue)
        .def("get_state", &Envelope::getState)
        .def("last_out", &Envelope::lastOut)
        .def("tick", nb::overload_cast<>(&Envelope::tick))
        .def("tick", &generate<Envelope>);

    nb::class_<Granulate, Generator>(m, "Granulate")
        .def(nb::init<>())
        .def(nb::init<unsigned int, std::string, bool>(), "n_voices"_a, "file_name"_a, "type_raw"_a=false)
        .def("open_file", &Granulate::openFile, "file_name"_a, "type_raw"_a=false)
        .def("reset", &Granulate::reset)
        .def("set_voices", &Granulate::setVoices, "n_voices"_a=1)
        .def("set_stretch", &Granulate::setStretch, "stretch_factor"_a=1)
        .def("set_grain_parameters", &Granulate::setGrainParameters, "duration"_a=30, "ramp_percent"_a=50, "offset"_a=0, "delay"_a=0)
        .def("set_random_factor", &Granulate::setRandomFactor, "randomness"_a=0.1)
        .def("last_out", &Granulate::lastOut, "channel"_a)
        .def("tick", nb::overload_cast<unsigned int>(&Granulate::tick), "channel"_a)
        .def("tick", [](Granulate& self, const audio_frames<1>& input) {
            StkFrames frames(input.shape(1), self.channelsOut());
            self.tick(frames);
            return stkframes_to_numpy<-1>(frames);
        });

    nb::class_<Modulate, Generator>(m, "Modulate")
        .def(nb::init<>())
        .def("reset", &Modulate::reset)
        .def("set_vibrato_rate", &Modulate::setVibratoRate)
        .def("set_vibrato_gain", &Modulate::setVibratoGain)
        .def("set_random_rate", &Modulate::setRandomRate)
        .def("set_random_gain", &Modulate::setRandomGain)
        .def("last_out", &Modulate::lastOut)
        .def("tick", nb::overload_cast<>(&Modulate::tick))
        .def("tick", &generate<Modulate>);

    nb::class_<Noise, Generator>(m, "Noise")
        .def(nb::init<unsigned int>(), "seed"_a=0)
        .def("set_seed", &Noise::setSeed, "seed"_a=0)
        .def("last_out", &Noise::lastOut)
        .def("tick", nb::overload_cast<>(&Noise::tick))
        .def("tick", &generate<Noise>);

    nb::class_<SineWave, Generator>(m, "SineWave")
        .def(nb::init<>())
        .def("reset", &SineWave::reset)
        .def("set_rate", &SineWave::setRate)
        .def("set_frequency", &SineWave::setFrequency)
        .def("add_time", &SineWave::addTime)
        .def("add_phase", &SineWave::addPhase)
        .def("add_phase_offset", &SineWave::addPhaseOffset)
        .def("last_out", &SineWave::lastOut)
        .def("tick", nb::overload_cast<>(&SineWave::tick))
        .def("tick", &generate<SineWave>);

    nb::class_<SingWave, Generator>(m, "SingWave")
        .def(nb::init<std::string, bool>(), "file_name"_a, "type_raw"_a=false)
        .def("reset", &SingWave::reset)
        .def("normalize", nb::overload_cast<StkFloat>(&SingWave::normalize), "peak"_a=1.0)
        .def("set_frequency", &SingWave::setFrequency)
        .def("set_vibrato_rate", &SingWave::setVibratoRate)
        .def("set_vibrato_gain", &SingWave::setVibratoGain)
        .def("set_random_gain", &SingWave::setRandomGain)
        .def("set_sweep_rate", &SingWave::setSweepRate)
        .def("set_gain_rate", &SingWave::setGainRate)
        .def("set_gain_target", &SingWave::setGainTarget)
        .def("note_on", &SingWave::noteOn)
        .def("note_off", &SingWave::noteOff)
        .def("last_out", &SingWave::lastOut)
        .def("tick", nb::overload_cast<>(&SingWave::tick))
        .def("tick", &generate<SingWave>);
}