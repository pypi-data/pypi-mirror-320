#include <pybind11/attr.h>
#include <pybind11/pytypes.h>
#include <sardine/package/interface.hpp>
#include <sardine/package/registry.hpp>

#include <sardine/python/cast/url.hpp>

#include <emu/pybind11.hpp>
#include <emu/pybind11/cast/span.hpp>

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace sardine
{

    void register_package(py::module_ m)
    {

        using buffer_pkg = package::interface::buffer_package;
        using memory_pkg = package::interface::memory_package;

        py::class_<
            package::interface::buffer_package,
            package::s_buffer_package
        >(m, "BufferPackage")
            .def(py::init(&package::url_to_buffer_package_or_throw))
            .def_property_readonly("producer", &package::interface::buffer_package::producer)
            .def_property_readonly("consumer", &package::interface::buffer_package::consumer)
            .def_property_readonly("mapping", &package::interface::buffer_package::mapping);

        py::class_<
            package::interface::memory_package,
            package::interface::buffer_package,
            package::s_memory_package
        >(m, "MemoryPackage")
            .def(py::init(&package::url_to_memory_package_or_throw))
            .def_property_readonly("bytes", [](package::interface::memory_package& pkg) -> py::memoryview {
                auto bytes = pkg.bytes();
                return py::memoryview::from_memory(emu::v_ptr_of(bytes), bytes.size());
            }, py::keep_alive<0, 1>());

    }

} // namespace sardine
