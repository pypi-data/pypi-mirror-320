#include "Common.h"

#include <Function.h>
#include <BowTable.h>
#include <Cubic.h>
#include <JetTable.h>
#include <ReedTable.h>

void add_function_bindings(nb::module_& m) {
    nb::class_<Function>(m, "Function")
        .def("last_out", &Function::lastOut);

    nb::class_<BowTable, Function>(m, "BowTable")
        .def(nb::init<>())
        .def("set_offset", &BowTable::setOffset)
        .def("set_slope", &BowTable::setSlope)
        .def("set_min_output", &BowTable::setMinOutput)
        .def("set_max_output", &BowTable::setMaxOutput)
        .def("tick", nb::overload_cast<StkFloat>(&BowTable::tick))
        .def("tick", &process_input<BowTable, 1, 1>);

    nb::class_<Cubic, Function>(m, "Cubic")
        .def(nb::init<>())
        .def("set_a1", &Cubic::setA1)
        .def("set_a2", &Cubic::setA2)
        .def("set_a3", &Cubic::setA3)
        .def("set_gain", &Cubic::setGain)
        .def("set_threshold", &Cubic::setThreshold)
        .def("tick", nb::overload_cast<StkFloat>(&Cubic::tick))
        .def("tick", &process_input<Cubic, 1, 1>);

    nb::class_<JetTable, Function>(m, "JetTable")
        .def(nb::init<>())
        .def("tick", nb::overload_cast<StkFloat>(&JetTable::tick))
        .def("tick", &process_input<JetTable, 1, 1>);

    nb::class_<ReedTable, Function>(m, "ReedTable")
        .def(nb::init<>())
        .def("set_offset", &ReedTable::setOffset)
        .def("set_slope", &ReedTable::setSlope)
        .def("tick", nb::overload_cast<StkFloat>(&ReedTable::tick))
        .def("tick", &process_input<ReedTable, 1, 1>);
}