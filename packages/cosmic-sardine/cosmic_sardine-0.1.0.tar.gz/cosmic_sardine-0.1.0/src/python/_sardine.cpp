#include <sardine/url.hpp>
#include <sardine/error.hpp>
#include <sardine/mapper.hpp>
#include <sardine/python/cast/url.hpp>
#include <sardine/sink.hpp>

#include <emu/pybind11.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/numpy.h>

#include <cstddef>
#include <fmt/core.h>

namespace py = pybind11;

namespace sardine
{
    void register_dlpack_types(py::module_ m);
    void register_context(py::module_ m);
    void register_mapping(py::module_ m);
    void register_buffer(py::module_ m);
    void register_package(py::module_ m);

    void register_shm_managed(py::module_ m);
    void register_shm_sync(py::module_ m);
    void register_region_host(py::module_ m);


} // namespace sardine

PYBIND11_MODULE(_sardine, m) {
    using namespace sardine;

#if !defined(NDEBUG)
    fmt::print("info: sardine is module compiled in debug mode\n");
#endif

    m.doc() = "pybind11 _sardine plugin";

    register_dlpack_types(m);
    register_context(m);
    register_mapping(m);
    register_buffer(m);
    register_package(m);

    auto region = m.def_submodule("region", "region submodule");
    register_region_host(region.def_submodule("host", "host region submodule"));

    register_shm_managed(m.def_submodule("managed", "managed submodule"));
    register_shm_sync(m.def_submodule("sync", "sync submodule"));


    m.def("set_url_view", [](const url_view& url) {
        fmt::print("url: {}\n", url);
    });

    m.def("set_url", [](const url& url) {
        fmt::print("url: {}\n", url);
    });

    m.def("get_url", []() -> url {
        return url("http://localhost:8080");
    });


    // m.def("bytes_from_url", [](url url) -> py::memoryview {
    //     auto [view, capsule] = EMU_UNWRAP_RES_OR_THROW(detail::bytes_from_url(url, emu::dlpack::device_type_t::kDLCPU)).as_pair();

    //     sardine::sink(std::move(capsule));

    //     return py::memoryview::from_buffer( reinterpret_cast<void*>(view.data()), view.size());
    // }, py::arg("url"));

    m.def("url_from_bytes", [](py::memoryview mv) -> url {
        Py_buffer* buffer = PyMemoryView_GET_BUFFER(mv.ptr());

        if (buffer == nullptr)
            throw std::runtime_error("memoryview is not valid");

        container_b container = {static_cast<byte*>(buffer->buf), static_cast<size_t>(buffer->len), emu::capsule(std::move(mv))};

        return EMU_UNWRAP_RES_OR_THROW(detail::url_from_bytes(container));
    }, py::arg("mv"));


    // m.def("numpy_ndarray_from_url", [](url url) -> np_ndarray {
    //     auto view = EMU_UNWRAP_RES_OR_THROW(detail::bytes_from_url(url, emu::dlpack::device_type_t::kDLCPU));

    //     auto mapping = EMU_UNWRAP_RES_OR_THROW(make_mapping(url.params()));

    //     using mapper = sardine::mapper< np_ndarray >;

    //     EMU_CHECK_ERRC_OR_THROW_LOG(mapper::check(mapping), "mapping check failed");

    //     return mapper< np_ndarray >::from_mapping_descriptor(mapping, emu::capsule()).convert(view);

    // }, py::arg("url"));

    // m.def("url_of_numpy_ndarray", [](np_ndarray obj, bool allow_local) -> url {
    //     return EMU_UNWRAP_RES_OR_THROW(sardine::url_of(obj, allow_local));
    // }, py::arg("obj"), py::arg("allow_local") = false);


}
