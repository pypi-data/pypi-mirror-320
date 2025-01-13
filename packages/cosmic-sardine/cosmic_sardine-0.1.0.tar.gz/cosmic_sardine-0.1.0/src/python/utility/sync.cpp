#include <sardine/utility/sync/sync.hpp>
#include <sardine/utility/sync/spin_lock.hpp>
#include <sardine/utility/sync/barrier.hpp>
#include <sardine/cache.hpp>
#include <sardine/python/sardine_helper.hpp>
#include <sardine/python/managed_helper.hpp>

#include <emu/pybind11/cast/span.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace sardine
{

    void register_shm_sync(py::module m)
    {
        using namespace pybind11::literals;

        using namespace sync;

        // #############
        // # Semaphore #
        // #############

        py::class_<semaphore_t> semaphore(m, "Semaphore");

        semaphore
            .def("release", [](semaphore_t& sem, std::size_t count){
                for (std::size_t i = 0; i < count; ++i)
                    sem.post();
            }, py::arg("count") = 1)
            .def("acquire", [](semaphore_t& sem, bool blocking) -> bool {
                if (blocking) {
                    sem.wait();
                    return true;
                }
                else
                    return sem.try_wait();
            }, py::arg("blocking") = 0) // should be false be that provoke a segfault. No idea why
        ;

        sardine_register(semaphore);
        register_managed(semaphore)
            .add_init([](create_proxy proxy, int init_value) -> semaphore_t& {
                return proxy.create<semaphore_t>(init_value);
            }, "init_value"_a = 0);

        // #########
        // # Mutex #
        // #########

        py::class_<mutex_t> mutex(m, "Mutex");

        mutex
            .def("release", [](mutex_t& mut){
                    mut.unlock();
            })
            .def("acquire", [](mutex_t& mut, bool blocking) -> bool {
                if (blocking) {
                    mut.lock();
                    return true;
                }
                else
                    return mut.try_lock();
            }, py::arg("blocking") = true)
        ;

        sardine_register(mutex);
        register_managed(mutex)
            .add_default();

        // ############
        // # SpinLock #
        // ############

        py::enum_<LockState>(m, "LockState")
            .value("Locked", LockState::Locked)
            .value("Unlocked", LockState::Unlocked)
            .export_values();

        py::class_<SpinLock> spin_lock(m, "SpinLock");

        spin_lock
            .def("lock", &SpinLock::lock)
            .def("try_lock", &SpinLock::try_lock)
            .def("unlock", &SpinLock::unlock)
            .def_property_readonly("value", &SpinLock::value)
        ;

        sardine_register(spin_lock);
        register_managed(spin_lock)
            .add_init([](create_proxy proxy, LockState init_value, bool sleep) -> SpinLock {
                return SpinLock(&proxy.create<lock_state>(init_value), sleep);
            }, "init_value"_a = LockState::Locked, "sleep"_a = false);

        // ###########
        // # Barrier #
        // ###########

        py::class_<WaiterConfig>(m, "WaiterConfig")
            .def(py::init<bool, int>(), "sleep"_a = false, "offset"_a = -1)
            .def_readwrite("sleep", &WaiterConfig::sleep)
            .def_readwrite("offset", &WaiterConfig::offset)
            .def("__repr__", [](const WaiterConfig& self) {
                return fmt::format("WaiterConfig(sleep={}, offset={})", self.sleep, self.offset);
            });

        py::class_<NotifierConfig, WaiterConfig>(m, "NotifierConfig")
            .def(py::init<bool, int, bool>(), "sleep"_a = false, "offset"_a = -1, "and_wait"_a = false)
            .def_readwrite("and_wait", &NotifierConfig::and_wait)
            .def("__repr__", [](const NotifierConfig& self) {
                return fmt::format("NotifierConfig(sleep={}, offset={}, and_wait={})", self.sleep, self.offset, self.and_wait);
            });

        py::class_<Barrier> barrier(m, "Barrier");

        barrier
            // .def("get_waiter", &Barrier::get_waiter)
            // .def("get_notifier", &Barrier::get_notifier)
            // .def("notify_all", &Barrier::notify_all)
        ;

        sardine_register(barrier);
        register_managed(barrier)
            .add_init([](create_proxy proxy, py::list py_waiters, py::list py_notifiers) -> Barrier& {
                auto waiters = py::cast<std::vector<WaiterConfig>>(py_waiters);
                auto notifiers = py::cast<std::vector<NotifierConfig>>(py_notifiers);

                auto& res = proxy.create<Barrier>(std::span(waiters), std::span(notifiers));

                // update the waiters and notifiers with the actual offset
                for (size_t i = 0; i < waiters.size(); ++i)
                    py_waiters[i] = py::cast(waiters[i]);

                for (size_t i = 0; i < notifiers.size(); ++i)
                    py_notifiers[i] = py::cast(notifiers[i]);

                return res;
            }, "waiters_config"_a, "notifiers_config"_a);

        py::class_<Waiter> waiter(m, "Waiter");

        waiter
            .def(py::init<Barrier*, WaiterConfig>(), "barrier"_a, "config"_a)
            .def("acquire", &Waiter::acquire)
            .def("try_acquire", &Waiter::try_acquire)
        ;

        sardine_register(waiter);

        py::class_<Notifier> notifier(m, "Notifier");

        notifier
            .def(py::init<Barrier*, NotifierConfig>(), "barrier"_a, "config"_a)
            .def("release", &Notifier::release)
        ;

        sardine_register(notifier);
    }


} // namespace sardine
