#include <sardine/mapping.hpp>
#include <emu/pybind11/numpy.hpp>
#include <sardine/python/cast/url.hpp>

#include <emu/pybind11.hpp>
#include <emu/pybind11/cast/span.hpp>

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace sardine
{

    void register_mapping(py::module_ m)
    {

        py::class_<interface::mapping>(m, "Mapping")
            .def_property_readonly("extents", &interface::mapping::extents)
            .def_property_readonly("is_strided", &interface::mapping::is_strided)
            .def_property_readonly("strides", &interface::mapping::strides)
            .def_property_readonly("data_type", &interface::mapping::data_type)
            .def_property_readonly("dtype", [](const interface::mapping& m) {
                return emu::pybind11::numpy::to_dtype(m.data_type());
            })
            .def_property_readonly("offset", &interface::mapping::offset)
            .def_property_readonly("is_const", &interface::mapping::is_const)
            .def_property_readonly("item_size", &interface::mapping::item_size);

        py::class_<default_mapping, interface::mapping>(m, "DefaultMapping")
            .def(py::init<std::vector<size_t>, std::vector<size_t>, data_type_ext_t, size_t, bool>());

        m.def("update_url", [](const url_view& u, const interface::mapping& m) -> url {
            url res(u);
            update_url(res, m);
            return res;
        }, "Update url with mapping",
              py::arg("url"), py::arg("mapping"));
    }

} // namespace sardine
