#pragma once

#include <cstddef>
#include <sardine/utility/sync/spin_lock.hpp>
#include <sardine/utility/sync/barrier.hpp>

namespace sardine::sync
{

    // using lock_vector = region::managed::vector<lock_state>;

    // using unique_locks = region::managed::unique_ptr<lock_state[]>;
    // using lock_iterator = lock_vector::iterator;

    struct WaiterConfig
    {
        bool sleep = false;
        std::ptrdiff_t offset = -1;
    };

    struct NotifierConfig : WaiterConfig
    {
        bool and_wait = false;
    };


    struct Barrier
    {
        region::managed::allocator<lock_state> alloc; size_t nb_waiters;
        region::managed::offset_ptr<lock_state> locks;
        boost::ipc_atomic<size_t> count, notifier_nb;
        boost::ipc_atomic<bool> sleeping_state = true;
        bool sleep = false;

        Barrier(std::span<WaiterConfig> waiters, std::span<NotifierConfig> notifiers, region::managed::allocator<lock_state> alloc)
            : alloc(alloc), nb_waiters(waiters.size())
            , count(notifiers.size()), notifier_nb(notifiers.size())
            , sleep(false)
        {
            for (const auto& n : notifiers)
                if(n.and_wait) nb_waiters++;

            locks = alloc.allocate(nb_waiters);
            for (size_t i = 0; i < nb_waiters; ++i)
                new (locks.get() + i) lock_state(LockState::Locked);

            size_t offset = 0;

            for (auto& w : waiters) {
                sleep |= w.sleep;

                w.offset = offset++;
            }

            for (auto& n : notifiers) {
                sleep |= n.sleep;

                if (n.and_wait) n.offset = offset++;
            }
        }

        Barrier(Barrier&& other)
            : alloc(other.alloc), nb_waiters(other.nb_waiters)
            , locks(std::exchange(other.locks, nullptr)), count(other.count.load()), notifier_nb(other.notifier_nb.load())
            , sleeping_state(other.sleeping_state.load()), sleep(other.sleep)
        {}

        ~Barrier() {
            if (locks)
                alloc.deallocate(locks, nb_waiters);
        }

        bool release() {
            if (count.sub(1, boost::memory_order_release) == 0) {
                // first, unlock all the locks
                release_all_locks();

                // If waiters are sleeping, wake them up
                if (sleep) {
                    auto new_value = not sleeping_state.load(boost::memory_order_acquire);
                    sleeping_state.store(new_value, boost::memory_order_release);

                    // syscall to wake up all the waiters
                    sleeping_state.notify_all();
                }

                count.store(notifier_nb.load(), boost::memory_order_release);

                return true;
            }

            return false;
        }

    private:
        void release_all_locks() {
            for (auto& lock : std::span(locks.get(), nb_waiters))
                lock.store(LockState::Unlocked, boost::memory_order_release);

        }
    };

    struct Waiter
    {
        Barrier* barrier;

        lock_state* state = nullptr;
        bool sleep = false;

        Waiter(Barrier* barrier, lock_state* state, bool sleep)
            : barrier(barrier)
            , state(state)
            , sleep(sleep)
        {}


        Waiter(Barrier* barrier, const WaiterConfig& config)
            : Waiter(barrier, get_state(barrier, config), config.sleep)
        {}

        bool try_acquire()
        {
            return state->exchange(LockState::Locked, boost::memory_order_acquire) != LockState::Locked;
        }

        void acquire()
        {
            if (not try_acquire()) {
                if (sleep)
                    sleep_acquire();
                else
                    spin_acquire();
            }

        }

    private:
        void spin_acquire()
        {
            while (not try_acquire()) {
                /* busy-wait */
            }
        }

        void sleep_acquire()
        {
            auto last_state = barrier->sleeping_state.load();
            // Still use a while loop to avoid spurious wakeups
            // and to reset the state if the thread is woken up
            while(not try_acquire()) {
                // Do not sleep on the waiter's own state.
                barrier->sleeping_state.wait(last_state);
            };
        }

    protected:
        static lock_state* get_state(Barrier* barrier, const WaiterConfig& config) {
            if (config.offset < 0 or config.offset >= barrier->nb_waiters)
                return nullptr;

            return barrier->locks.get() + config.offset;
        }

    public:
        result<url> url_of() const;

        static result<Waiter> from_url(const sardine::url_view& u);

    };


    struct Notifier : private Waiter
    {

        Notifier(Waiter&& w)
            : Waiter(w.barrier, w.state, w.sleep)
        {}

        Notifier(Barrier* barrier, const NotifierConfig& config)
            : Waiter(barrier, config)
        {}

        bool release()
        {
            auto barrier_released = barrier->release();

            // A non null state means that the notifier is also a waiter
            if (state != nullptr) {
                if (not barrier_released) {
                    // If the barrier was not released, we wait for it to be released
                    acquire();
                } else {
                    // If the barrier was released, we reset the state
                    //TODO: check if we need to reset the state
                    state->store(LockState::Locked, boost::memory_order_release);
                }

            }

            return barrier_released;

        }

        using Waiter::url_of;

        static result<Notifier> from_url(const sardine::url_view& u) {
            return Waiter::from_url(u).map([](Waiter&& w) {
                return Notifier(std::move(w));
            });
        }

    };


} // namespace sardine::sync

template<typename Alloc>
struct std::uses_allocator<sardine::sync::Barrier, Alloc> : std::true_type {};
