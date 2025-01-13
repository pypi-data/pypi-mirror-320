#include <sardine/buffer/interface.hpp>

#include <sardine/python/cast/url.hpp>

#include <emu/pybind11.hpp>
#include <emu/pybind11/cast/span.hpp>

#include <pybind11/pybind11.h>

namespace sardine
{

    void register_buffer(py::module_ m)
    {
        namespace py = pybind11;

        using namespace sardine::buffer::interface;

        py::class_<view_t>(m, "View")
            .def_property_readonly("bytes", [](view_t& v) -> py::memoryview {
                auto bytes = v.bytes();
                return py::memoryview::from_memory( reinterpret_cast<void*>(bytes.data()), bytes.size());
            })
            .def_property_readonly("url_of", &view_t::url_of);

        py::class_<producer, view_t>(m, "Producer")
            .def("send", &producer::send)
            .def("revert", &producer::revert);

        py::class_<consumer, view_t>(m, "Consumer")
            .def("recv", &consumer::recv)
            .def("revert", &consumer::revert);
    }

} // namespace sardine
