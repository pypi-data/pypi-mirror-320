#pragma once

#include <sardine/config.hpp>
#include <sardine/type/url.hpp>
#include <sardine/region/managed.hpp>

#include <boost/atomic/ipc_atomic.hpp>

namespace sardine::sync
{
    enum class LockState {Locked, Unlocked};

    using lock_state = boost::ipc_atomic<LockState>;

    struct LockStateFactory {
        LockState init_value = LockState::Locked;

        operator lock_state() const {
            return lock_state(init_value);
        }
    };

    struct SpinLock {

        // boost::ipc_atomic<LockState> state = LockState::Locked;
        lock_state* state = nullptr;
        bool sleep = false;

        SpinLock(lock_state* state, bool sleep)
            : state(state)
            , sleep(sleep)
        {}

        LockState value() const {
            return state->load();
        }

        void lock()
        {
            if (sleep)
                sleep_lock();
            else
                spin_lock();

        }

        void spin_lock()
        {
            while (state->exchange(LockState::Locked, boost::memory_order_acquire) == LockState::Locked) {
                /* busy-wait */
            }
        }

        void sleep_lock()
        {
            try_lock();
            while(state->wait(LockState::Locked) == LockState::Locked) {
                /* sleep */
            };
        }

        bool try_lock()
        {
            return state->exchange(LockState::Locked, boost::memory_order_acquire) != LockState::Locked;
        }

        void unlock()
        {
            state->store(LockState::Unlocked, boost::memory_order_release);
            if (sleep)
                state->notify_one();
        }

        bool is_locked() const
        {
            return state->load(boost::memory_order_acquire) == LockState::Locked;
        }

        result<url> url_of() const;

        static result<SpinLock> from_url(const sardine::url_view& u);
    };

} // namespace sardine::sync
