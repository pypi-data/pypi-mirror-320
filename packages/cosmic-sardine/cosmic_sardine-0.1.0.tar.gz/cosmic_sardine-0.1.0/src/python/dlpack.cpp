#include <emu/detail/dlpack_types.hpp>
#include <emu/pybind11/numpy.hpp>

#include <sardine/type.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;


namespace sardine
{

    void register_dlpack_types(py::module_ m) {

        py::enum_<device_type_t>(m, "DeviceType")
            .value("CPU", kDLCPU)
            .value("CUDA", kDLCUDA)
            .value("CUDAHost", kDLCUDAHost)
            .value("OpenCL", kDLOpenCL)
            .value("Vulkan", kDLVulkan)
            .value("Metal", kDLMetal)
            .value("VPI", kDLVPI)
            .value("ROCM", kDLROCM)
            .value("ROCMHost", kDLROCMHost)
            .value("ExtDev", kDLExtDev)
            .value("CUDAManaged", kDLCUDAManaged)
            .value("OneAPI", kDLOneAPI)
            .value("WebGPU", kDLWebGPU)
            .value("Hexagon", kDLHexagon)
            .value("MAIA", kDLMAIA)
            .export_values();

        py::class_<device_t>(m, "Device")
            .def(py::init<device_type_t, int>())
            .def_readwrite("device_type", &device_t::device_type)
            .def_readwrite("device_id", &device_t::device_id);

        py::enum_<data_type_code_t>(m, "DataTypeCode")
            .value("Int", kDLInt)
            .value("UInt", kDLUInt)
            .value("Float", kDLFloat)
            .value("Complex", kDLComplex)
            .value("Bfloat", kDLBfloat)
            .value("OpaqueHandle", kDLOpaqueHandle)
            .value("Bool", kDLBool)
            .export_values();

        py::class_<data_type_t>(m, "DataType")
            .def(py::init<data_type_code_t, int, int>())
            .def(py::init([](py::dtype dtype) {
                using bits_type = decltype(data_type_t::bits);
                auto item_size_bits = dtype.itemsize() * CHAR_BIT;

                static constexpr auto max_bits = std::numeric_limits<bits_type>::max();
                if (item_size_bits > max_bits) {
                    throw std::invalid_argument(fmt::format("dtype.itemsize() is too large: {}, limit is {}", item_size_bits, max_bits));
                }

                return data_type_t{
                    .code = emu::pybind11::numpy::code_from_np_types(dtype.num()),
                    .bits = static_cast<bits_type>(item_size_bits),
                    .lanes = 1
                };
            }))
            .def_readwrite("code", &data_type_t::code)
            .def_readwrite("bits", &data_type_t::bits)
            .def_readwrite("lanes", &data_type_t::lanes)
            .def_property_readonly("dtype", [](const data_type_t& self) {
                return emu::pybind11::numpy::to_dtype(self);
            });

        py::class_<data_type_ext_t>(m, "DataTypeExt")
            .def(py::init<data_type_code_t, int, int>())
            .def(py::init([](py::dtype dtype) {
                //Note: bits is large enough to hold the itemsize in bits. No check is needed.
                return data_type_ext_t{
                    .code = emu::pybind11::numpy::code_from_np_types(dtype.num()),
                    .bits = static_cast<uint64_t>(dtype.itemsize()) * CHAR_BIT,
                    .lanes = 1
                };
            }))
            .def_readwrite("code", &data_type_ext_t::code)
            .def_readwrite("bits", &data_type_ext_t::bits)
            .def_readwrite("lanes", &data_type_ext_t::lanes)
            .def_property_readonly("dtype", [](const data_type_ext_t& self) {
                return emu::pybind11::numpy::to_dtype(self);
            });

    }

} // namespace sardine
