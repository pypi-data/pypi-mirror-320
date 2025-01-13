#include <emu/assert.hpp>
#include <sardine/region/host.hpp>
#include <sardine/region/host/manager.hpp>

#include <emu/pybind11/cast/span.hpp>
#include <emu/pybind11/cast/cstring_view.hpp>

#include <pybind11/stl.h>

// #include <pybind11/stl/string.h>
// #include <pybind11/pybind11.h>
// #include <pybind11/numpy.h>

namespace py = pybind11;

namespace sardine
{

    void register_region_host(py::module_ m)
    {
        //TODO: returns data as memoryview instead.

        {
            auto shm = m.def_submodule("shm", "shm submodule");


            shm.def("open", [](std::string name, bool read_only) -> py::memoryview {
                auto data = region::host::open_shm(name, read_only);
                return py::memoryview::from_memory(
                    reinterpret_cast<void*>(data.data()),
                    static_cast<py::ssize_t>(data.size()),
                    read_only
                );
            }, py::arg("name"), py::arg("read_only") = false);

            shm.def("create", [](std::string name, std::size_t size, bool read_only) -> py::memoryview {
                auto data = region::host::create_shm(name, size, read_only);
                return py::memoryview::from_memory(
                    reinterpret_cast<void*>(data.data()),
                    static_cast<py::ssize_t>(data.size()),
                    read_only
                );
            }, py::arg("name"), py::arg("size"), py::arg("read_only") = false);

            shm.def("open_or_create", [](std::string name, std::size_t size, bool read_only) -> py::memoryview {
                auto data = region::host::open_or_create_shm(name, size, read_only);
                return py::memoryview::from_memory(
                    reinterpret_cast<void*>(data.data()),
                    static_cast<py::ssize_t>(data.size()),
                    read_only
                );
            }, py::arg("name"), py::arg("size"), py::arg("read_only") = false);


            // shm.def("open_shm", [](std::string name, py::object data_type) -> np_ndarray {
            //     auto dtype = py::dtype::from_args(data_type);
            //     auto bytes = region::host::open_shm(name);

            //     return np_ndarray(
            //         /* dtype = */ dtype,
            //         /* shape = */ std::vector<py::ssize_t>(1, bytes.size() / dtype.itemsize() ),
            //         /* ptr = */ v_ptr_of(bytes),
            //         py::str() // dummy handle to avoid copying the data.
            //     );
            // }, py::arg("name"), py::arg("dtype"));

            // shm.def("create", [](std::string name, std::vector<py::ssize_t> shape, py::object data_type) -> np_ndarray {
            //     auto dtype = py::dtype::from_args(data_type);
            //     size_t bytes_size = dtype.itemsize(); for (auto e : shape) bytes_size *= e;

            //     auto bytes = region::host::create_shm(name, bytes_size);

            //     return np_ndarray(
            //         /* dtype = */ dtype,
            //         /* shape = */ move(shape),
            //         /* ptr = */ v_ptr_of(bytes),
            //         py::str() // dummy handle to avoid copying the data.
            //     );
            // }, py::arg("name"), py::arg("shape"), py::arg("dtype"));

            // shm.def("open_or_create", [](std::string name, std::vector<py::ssize_t> shape, py::object data_type) -> np_ndarray {
            //     auto dtype = py::dtype::from_args(data_type);
            //     size_t bytes_size = dtype.itemsize(); for (auto e : shape) bytes_size *= e;

            //     auto bytes = region::host::open_or_create_shm(name, bytes_size);

            //     // In case of opening an exiting host shm.
            //     EMU_TRUE_OR_THROW(bytes_size == bytes.size(), errc::host_incompatible_shape);

            //     return np_ndarray(
            //         /* dtype = */ dtype,
            //         /* shape = */ move(shape),
            //         /* ptr = */ v_ptr_of(bytes),
            //         py::str() // dummy handle to avoid copying the data.
            //     );
            // }, py::arg("name"), py::arg("shape"), py::arg("dtype"));
        }
        {
            auto file = m.def_submodule("file", "file submodule");

            file.def("open", [](std::string name, bool read_only) -> py::memoryview {
                auto data = region::host::open_file(name, read_only);
                return py::memoryview::from_memory(
                    reinterpret_cast<void*>(data.data()),
                    static_cast<py::ssize_t>(data.size()),
                    read_only
                );
            }, py::arg("name"), py::arg("read_only"));

            file.def("create", [](std::string name, std::size_t size, bool read_only) -> py::memoryview  {
                auto data = region::host::create_file(name, size, read_only);
                return py::memoryview::from_memory(
                    reinterpret_cast<void*>(data.data()),
                    static_cast<py::ssize_t>(data.size()),
                    read_only
                );
            }, py::arg("name"), py::arg("size"), py::arg("read_only"));

            file.def("open_or_create", [](std::string name, std::size_t size, bool read_only) -> py::memoryview  {
                auto data = region::host::open_or_create_file(name, size, read_only);
                return py::memoryview::from_memory(
                    reinterpret_cast<void*>(data.data()),
                    static_cast<py::ssize_t>(data.size()),
                    read_only
                );
            }, py::arg("name"), py::arg("size"), py::arg("read_only"));


            // file.def("open_shm", [](std::string name, py::object data_type) -> np_ndarray {
            //     auto dtype = py::dtype::from_args(data_type);
            //     auto bytes = region::host::open_file(name);

            //     return np_ndarray(
            //         /* dtype = */ dtype,
            //         /* shape = */ std::vector<py::ssize_t>(1, bytes.size() / dtype.itemsize() ),
            //         /* ptr = */ v_ptr_of(bytes),
            //         py::str() // dummy handle to avoid copying the data.
            //     );
            // }, py::arg("name"), py::arg("dtype"));

            // file.def("create", [](std::string name, std::vector<py::ssize_t> shape, py::object data_type) -> np_ndarray {
            //     auto dtype = py::dtype::from_args(data_type);
            //     size_t bytes_size = dtype.itemsize(); for (auto e : shape) bytes_size *= e;

            //     auto bytes = region::host::create_file(name, bytes_size);

            //     return np_ndarray(
            //         /* dtype = */ dtype,
            //         /* shape = */ move(shape),
            //         /* ptr = */ v_ptr_of(bytes),
            //         py::str() // dummy handle to avoid copying the data.
            //     );
            // }, py::arg("name"), py::arg("shape"), py::arg("dtype"));

            // file.def("open_or_create", [](std::string name, std::vector<py::ssize_t> shape, py::object data_type) -> np_ndarray {
            //     auto dtype = py::dtype::from_args(data_type);
            //     size_t bytes_size = dtype.itemsize(); for (auto e : shape) bytes_size *= e;

            //     auto bytes = region::host::open_or_create_file(name, bytes_size);

            //     // In case of opening an exiting host shm.
            //     EMU_TRUE_OR_THROW(bytes_size == bytes.size(), errc::host_incompatible_shape);

            //     return np_ndarray(
            //         /* dtype = */ dtype,
            //         /* shape = */ move(shape),
            //         /* ptr = */ v_ptr_of(bytes),
            //         py::str() // dummy handle to avoid copying the data.
            //     );
            // }, py::arg("name"), py::arg("shape"), py::arg("dtype"));
        }

    }

} // namespace sardine
