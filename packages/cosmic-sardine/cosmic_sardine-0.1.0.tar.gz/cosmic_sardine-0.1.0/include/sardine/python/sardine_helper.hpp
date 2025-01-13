#pragma once

#include <pybind11/pytypes.h>
#include <sardine/url.hpp>
#include <sardine/python/cast/url.hpp>

#include <emu/type_name.hpp>
#include <emu/utility.hpp>

#include <pybind11/pybind11.h>
#include <type_traits>

PYBIND11_NAMESPACE_BEGIN(PYBIND11_NAMESPACE)
PYBIND11_NAMESPACE_BEGIN(detail)

// stupid "py::detail::is_move_constructible" that check if value_type is move constructible.
template<typename T>
struct is_move_constructible<sardine::type_mapper<T>> : std::true_type {};

PYBIND11_NAMESPACE_END(detail)
PYBIND11_NAMESPACE_END(PYBIND11_NAMESPACE)


namespace sardine
{

    //TODO: change default policy to automatic.
    template<typename RequestedType = emu::use_default, typename T>
    void sardine_register(pybind11::class_<T> cls) {
        namespace py = pybind11;

        using requested_type = emu::not_default_or<RequestedType, T>;

        using mapper_t = sardine::type_mapper<requested_type>;

        py::class_<mapper_t>(cls, "SardineMapper")
            .def_static("check", [](const interface::mapping& mapping) -> void {
                EMU_CHECK_ERRC_OR_THROW_LOG(mapper_t::check(mapping), "mapping check failed");
            })
            .def(py::init(&mapper_t::from_mapping))
            .def(py::init(&mapper_t::from))
            .def_property_readonly("mapping", &mapper_t::mapping)
            .def("from_memoryview", [](mapper_t& mapper, py::memoryview mv) -> T& {
                Py_buffer* buffer = PyMemoryView_GET_BUFFER(mv.ptr());

                if (buffer == nullptr)
                    throw std::runtime_error("memoryview is not valid");

                container_b container = {static_cast<byte*>(buffer->buf), static_cast<size_t>(buffer->len)}; // , emu::capsule(std::move(mv))

                return mapper.convert(std::move(container));
            }, py::return_value_policy::reference, py::keep_alive<0, 2>()) // As long as the returned object is alive, the memoryview is kept alive.
            .def_property_readonly_static("requested_device_type", [](py::object /* self */) -> device_type_t {
                return emu::location_type_of<requested_type>::device_type;
            })
            .def_static("as_memoryview", [](const T& value) -> py::memoryview {
                auto bytes = mapper_t::as_bytes(value);

                return py::memoryview::from_memory( emu::v_ptr_of(bytes), bytes.size());
            })
            .def("url_of", [](const T& value) -> url {
                return sardine::url_of_or_throw(value);
            })
            .def_property_readonly_static("type", [cls](py::object /* self */) -> py::object {
                return cls;
            });
    }

} // namespace sardine
