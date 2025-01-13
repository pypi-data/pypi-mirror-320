#include <sardine/region/managed.hpp>
#include <sardine/python/managed_helper.hpp>

#include <emu/cstring_view.hpp>
#include <emu/pybind11/cast/cstring_view.hpp>
#include <emu/pybind11/cast/span.hpp>

#include <pybind11/pybind11.h>

#include <boost/preprocessor/stringize.hpp>
#include <boost/callable_traits.hpp>

#include <functional>
#include <type_traits>

namespace py = pybind11;

namespace sardine
{

namespace detail
{

    /**
     * @brief Take a method and change the first argument `this` to another type.
     *
     * The new function will have exactly the same signature (it won't be polymorphic)
     * and will be internally cast from the new type to the old type using operator *.
     *
     *
     * @tparam Fn
     * @tparam the new `this` type.
     */
    template <typename T, auto Met>
    auto adapt_method() {
        // Gets Method domain.
        using args = boost::callable_traits::args_t<decltype(Met)>;

        return []<typename This, typename... Args>(std::type_identity<std::tuple<This, Args...>>) {
            // This lambda which is returned have the exact same domain than `Met` except that
            // the first argument is `T` instead of `This`.
            return [] (T& t, Args... args) {
                // Call the original method with the provided args. We suppose '*t' returns `this`.
                return std::invoke(Met, *t, EMU_FWD(args)...);
            };
        }(std::type_identity<args>{});
    }

} // namespace detail


    void register_shm_managed(py::module_ m)
    {
        using namespace py::literals;
        using region::managed_t;


        py::class_<region::managed::named_value_t>(m, "named_value")
            .def_property_readonly("name", &region::managed::named_value_t::name);

        py::class_<region::managed::named_range>(m, "named_range")
            .def("__len__", &region::managed::named_range::size)
            .def("__iter__", [](region::managed::named_range& range) {
                    return py::make_iterator(range.begin(), range.end());
                }, py::keep_alive<0, 1>())
        ;

        py::class_<managed_t> managed(m, "Managed");

        managed
            .def_property_readonly("named", [](managed_t& managed) {
                return managed.named();
            }, py::keep_alive<0, 1>())
            .def("__repr__", [](managed_t& managed) {
                auto total = managed.shm().get_size();
                auto used = total - managed.shm().get_free_memory();
                return fmt::format("sardine.shm.managed: used {}/{}", used, total);
            })
            .def_property_readonly("memory_available", [](managed_t& managed) { return managed.shm().get_free_memory();})
            .def_property_readonly("memory_total",     [](managed_t& managed) { return managed.shm().get_size(); })
            .def_property_readonly("memory_used",      [](managed_t& managed) {
                return managed.shm().get_size() - managed.shm().get_free_memory();
            })
        ;

        m.def("open",           &region::managed::open,           "name"_a                       );
        m.def("create",         &region::managed::create,         "name"_a, "initial_count"_a = 1);
        m.def("open_or_create", &region::managed::open_or_create, "name"_a, "initial_count"_a = 1);

    }

} // namespace sardine
