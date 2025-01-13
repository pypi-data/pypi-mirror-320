#include <sardine/utility/component_info.hpp>

// #include <sardine/python/url_helper.hpp>
#include <sardine/python/managed_helper.hpp>

#include <emu/pybind11/cast/cstring_view.hpp>

#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_NAMESPACE_BEGIN(PYBIND11_NAMESPACE)

namespace detail
{
    template <>
    struct type_caster<sardine::region::managed::string>
        : string_caster<sardine::region::managed::string> {};

} // namespace detail

PYBIND11_NAMESPACE_END(PYBIND11_NAMESPACE)


void register_compoenet_info(py::module_ m) {

    using namespace sardine;

    py::enum_<Command>(m, "Command")
        .value("pause", Command::pause)
        .value("run", Command::run)
        .value("step", Command::step)
        .value("exit", Command::exit)
        .export_values();

    py::enum_<Status>(m, "Status")
        .value("none", Status::none)
        .value("acquired", Status::acquired)
        .value("running", Status::running)
        .value("pausing", Status::pausing)
        .value("exited", Status::exited)
        .value("crashed", Status::crashed)
        .export_values();

    py::class_<ComponentInfo> ci(m, "ComponentInfo");

    ci
        .def_property("status",
            &ComponentInfo::status, &ComponentInfo::set_status
        )
        .def_property("cmd",
            &ComponentInfo::cmd, &ComponentInfo::set_cmd
        )
        .def_readonly("pid", &ComponentInfo::pid)
        .def("acquire", &ComponentInfo::acquire)
        .def("release", &ComponentInfo::release)
    ;

    // sardine::register_url(ci);

    py::class_<ComponentInfoManager>(m, "ComponentInfoManager")
        .def_static("create", [] () -> ComponentInfoManager& {
            auto managed = sardine::region::managed::open_or_create("baldr_component_manager", 10*1024*1024);

            return managed.force_create<ComponentInfoManager>(sardine::region::managed::unique_instance);
        }, pybind11::return_value_policy::reference)
        .def("create_component_info", &ComponentInfoManager::create_component_info, pybind11::return_value_policy::reference)
        .def("values", [](ComponentInfoManager& manager) {
            return py::make_value_iterator(manager.components.begin(), manager.components.end());
        }, py::keep_alive<0, 1>())
        .def("keys", [](ComponentInfoManager& manager) {
            return py::make_key_iterator(manager.components.begin(), manager.components.end());
        }, py::keep_alive<0, 1>())
        .def("items", [](ComponentInfoManager& manager) {
            return py::make_iterator(manager.components.begin(), manager.components.end());
        }, py::keep_alive<0, 1>())
    ;


}
