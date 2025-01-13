#include <sardine/context.hpp>

#include <emu/pybind11.hpp>

namespace py = pybind11;

namespace sardine
{


    void register_context(py::module_ m) {

        py::class_<sardine::host_context>(m, "HostContext")
            .def(py::init<>())
        ;

    }

} // namespace sardine
