#include "Common.h"

#include <Filter.h>
#include <BiQuad.h>
#include <Delay.h>
#include <DelayA.h>
#include <DelayL.h>
#include <Fir.h>
#include <FormSwep.h>
#include <Iir.h>
#include <OnePole.h>
#include <OneZero.h>
#include <PoleZero.h>
#include <TapDelay.h>
#include <TwoPole.h>
#include <TwoZero.h>

void add_filter_bindings(nb::module_& m) {
    nb::class_<Filter>(m, "Filter")
        .def("channels_in", &Filter::channelsIn)
        .def("channels_out", &Filter::channelsOut)
        .def("clear", &Filter::clear)
        .def("set_gain", &Filter::setGain)
        .def("get_gain", &Filter::getGain)
        .def("phase_delay", &Filter::phaseDelay)
        .def("last_frame", &Filter::lastFrame);

    nb::class_<BiQuad, Filter>(m, "BiQuad")
        .def(nb::init<>())
        .def("ignore_sample_rate_change", &BiQuad::ignoreSampleRateChange)
        .def("set_coefficients", &BiQuad::setCoefficients)
        .def("set_b0", &BiQuad::setB0)
        .def("set_b1", &BiQuad::setB1)
        .def("set_b2", &BiQuad::setB2)
        .def("set_a1", &BiQuad::setA1)
        .def("set_a2", &BiQuad::setA2)
        .def("set_resonance", &BiQuad::setResonance)
        .def("set_notch", &BiQuad::setNotch)
        .def("set_lowpass", &BiQuad::setLowPass)
        .def("set_highpass", &BiQuad::setHighPass)
        .def("set_bandpass", &BiQuad::setBandPass)
        .def("set_bandreject", &BiQuad::setBandReject)
        .def("set_allpass", &BiQuad::setAllPass)
        .def("set_equal_gain_zeroes", &BiQuad::setEqualGainZeroes)
        .def("last_out", &BiQuad::lastOut)
        .def("tick", nb::overload_cast<StkFloat>(&BiQuad::tick))
        .def("tick", &process_input<BiQuad, 1, 1>);

    nb::class_<Delay, Filter>(m, "Delay")
        .def(nb::init<unsigned long, unsigned long>(), "delay"_a = 0, "max_delay"_a = 4095)
        .def("get_maximum_delay", &Delay::getMaximumDelay)
        .def("set_maximum_delay", &Delay::setMaximumDelay)
        .def("set_delay", &Delay::setDelay)
        .def("get_delay", &Delay::getDelay)
        .def("tap_out", &Delay::tapOut)
        .def("tap_in", &Delay::tapIn)
        .def("add_to", &Delay::addTo)
        .def("last_out", &Delay::lastOut)
        .def("next_out", &Delay::nextOut)
        .def("energy", &Delay::energy)
        .def("tick", nb::overload_cast<StkFloat>(&Delay::tick))
        .def("tick", &process_input<Delay, 1, 1>);

    nb::class_<DelayA, Filter>(m, "DelayA")
        .def(nb::init<StkFloat, unsigned long>(), "delay"_a = 0.5, "max_delay"_a = 4095)
        .def("clear", &DelayA::clear)
        .def("get_maximum_delay", &DelayA::getMaximumDelay)
        .def("set_maximum_delay", &DelayA::setMaximumDelay)
        .def("set_delay", &DelayA::setDelay)
        .def("get_delay", &DelayA::getDelay)
        .def("tap_out", &DelayA::tapOut)
        .def("tap_in", &DelayA::tapIn)
        .def("last_out", &DelayA::lastOut)
        .def("next_out", &DelayA::nextOut)
        .def("tick", nb::overload_cast<StkFloat>(&DelayA::tick))
        .def("tick", &process_input<DelayA, 1, 1>);

    nb::class_<DelayL, Filter>(m, "DelayL")
        .def(nb::init<StkFloat, unsigned long>(), "delay"_a = 0.0, "max_delay"_a = 4095)
        .def("get_maximum_delay", &DelayL::getMaximumDelay)
        .def("set_maximum_delay", &DelayL::setMaximumDelay)
        .def("set_delay", &DelayL::setDelay)
        .def("get_delay", &DelayL::getDelay)
        .def("tap_out", &DelayL::tapOut)
        .def("tap_in", &DelayL::tapIn)
        .def("last_out", &DelayL::lastOut)
        .def("next_out", &DelayL::nextOut)
        .def("tick", nb::overload_cast<StkFloat>(&DelayL::tick))
        .def("tick", &process_input<DelayL, 1, 1>);

    nb::class_<Fir, Filter>(m, "Fir")
        .def(nb::init<>())
        .def(nb::init<std::vector<StkFloat>&>(), "coefficients"_a)
        .def("set_coefficients", &Fir::setCoefficients)
        .def("last_out", &Fir::lastOut)
        .def("tick", nb::overload_cast<StkFloat>(&Fir::tick))
        .def("tick", &process_input<Fir, 1, 1>);

    nb::class_<FormSwep, Filter>(m, "FormSwep")
        .def(nb::init<>())
        .def("ignore_sample_rate_change", &FormSwep::ignoreSampleRateChange)
        .def("set_resonance", &FormSwep::setResonance)
        .def("set_states", &FormSwep::setStates)
        .def("set_targets", &FormSwep::setTargets)
        .def("set_sweep_rate", &FormSwep::setSweepRate)
        .def("set_sweep_time", &FormSwep::setSweepTime)
        .def("last_out", &FormSwep::lastOut)
        .def("tick", nb::overload_cast<StkFloat>(&FormSwep::tick))
        .def("tick", &process_input<FormSwep, 1, 1>);

    nb::class_<Iir, Filter>(m, "Iir")
        .def(nb::init<>())
        .def(nb::init<std::vector<StkFloat>&, std::vector<StkFloat>&>(), "b_coefficients"_a, "a_coefficients"_a)
        .def("set_coefficients", &Iir::setCoefficients)
        .def("set_numerator", &Iir::setNumerator)
        .def("set_denominator", &Iir::setDenominator)
        .def("last_out", &Iir::lastOut)
        .def("tick", nb::overload_cast<StkFloat>(&Iir::tick))
        .def("tick", &process_input<Iir, 1, 1>);

    nb::class_<OnePole, Filter>(m, "Filter")
        .def(nb::init<StkFloat>(), "the_pole"_a = 0.9)
        .def("set_b0", &OnePole::setB0)
        .def("set_a1", &OnePole::setA1)
        .def("set_coefficients", &OnePole::setCoefficients)
        .def("set_pole", &OnePole::setPole)
        .def("last_out", &OnePole::lastOut)
        .def("tick", nb::overload_cast<StkFloat>(&OnePole::tick))
        .def("tick", &process_input<OnePole, 1, 1>);

    nb::class_<OneZero, Filter>(m, "OneZero")
        .def(nb::init<StkFloat>(), "the_zero"_a = -1.0)
        .def("set_b0", &OneZero::setB0)
        .def("set_b1", &OneZero::setB1)
        .def("set_coefficients", &OneZero::setCoefficients)
        .def("set_zero", &OneZero::setZero)
        .def("last_out", &OneZero::lastOut)
        .def("tick", nb::overload_cast<StkFloat>(&OneZero::tick))
        .def("tick", &process_input<OneZero, 1, 1>);

    nb::class_<PoleZero, Filter>(m, "PoleZero")
        .def(nb::init<>())
        .def("set_b0", &PoleZero::setB0)
        .def("set_b1", &PoleZero::setB1)
        .def("set_a1", &PoleZero::setA1)
        .def("set_coefficients", &PoleZero::setCoefficients)
        .def("set_allpass", &PoleZero::setAllpass)
        .def("set_block_zero", &PoleZero::setBlockZero)
        .def("last_out", &PoleZero::lastOut)
        .def("tick", nb::overload_cast<StkFloat>(&PoleZero::tick))
        .def("tick", &process_input<PoleZero, 1, 1>);

    nb::class_<TapDelay, Filter>(m, "TapDelay")
        .def(nb::init<std::vector<unsigned long>, unsigned long>(), "taps"_a = std::vector<unsigned long>(1, 0), "max_delay"_a = 4095)
        .def("set_maximum_delay", &TapDelay::setMaximumDelay)
        .def("set_tap_delays", &TapDelay::setTapDelays)
        .def("get_tap_delays", &TapDelay::getTapDelays)
        .def("last_out", &TapDelay::lastOut)
        .def("tick", [](TapDelay& self, StkFloat input) {
            StkFrames frames(1, self.getTapDelays().size());
            self.tick(input, frames);
            return stkframes_to_numpy<-1>(frames);
        })
        .def("tick", [](TapDelay& self, const audio_frames<1>& input) {
            StkFrames frames(input.shape(1), self.getTapDelays().size());
            self.tick(frames);
            return stkframes_to_numpy<-1>(frames);
        });

    nb::class_<TwoPole, Filter>(m, "TwoPole")
        .def(nb::init<>())
        .def("ignore_sample_rate_change", &TwoPole::ignoreSampleRateChange)
        .def("set_b0", &TwoPole::setB0)
        .def("set_a1", &TwoPole::setA1)
        .def("set_a2", &TwoPole::setA2)
        .def("set_coefficients", &TwoPole::setCoefficients)
        .def("set_resonance", &TwoPole::setResonance)
        .def("last_out", &TwoPole::lastOut)
        .def("tick", nb::overload_cast<StkFloat>(&TwoPole::tick))
        .def("tick", &process_input<TwoPole, 1, 1>);

    nb::class_<TwoZero, Filter>(m, "TwoZero")
        .def(nb::init<>())
        .def("ignore_sample_rate_change", &TwoZero::ignoreSampleRateChange)
        .def("set_b0", &TwoZero::setB0)
        .def("set_b1", &TwoZero::setB1)
        .def("set_b2", &TwoZero::setB2)
        .def("set_coefficients", &TwoZero::setCoefficients)
        .def("set_notch", &TwoZero::setNotch)
        .def("last_out", &TwoZero::lastOut)
        .def("tick", nb::overload_cast<StkFloat>(&TwoZero::tick))
        .def("tick", &process_input<TwoZero, 1, 1>);
}