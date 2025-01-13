#include <sardine/utility/sync/barrier.hpp>
#include <sardine/url.hpp>

#include <emu/charconv.hpp>

namespace sardine::sync
{

    result<url> Waiter::url_of() const {
        return sardine::url_of(*barrier).map([&](auto&& u) {
            if (state != nullptr) {
                auto offset = state - barrier->locks.get();

                u.params().append(urls::param_view("state",fmt::to_string( offset)));
            }
            if (sleep)
                // Empty parameter that indicates that the waiter should sleep
                u.params().append(urls::param_view("sleep", nullptr));

            return u;
        });
    }

    sardine::result<Waiter> Waiter::from_url(const sardine::url_view& u) {
        return sardine::from_url<Barrier&>(u).and_then([&](auto&& barrier) -> result<Waiter> {
            const auto& params = u.params();

            bool sleep = params.contains("sleep");

            std::ptrdiff_t offset = -1;
            if (auto state = params.find("state"); state != params.end()) {
                EMU_TRUE_OR_RETURN_UN_EC_ERRNO_LOG(emu::from_chars((*state).value, offset),
                    "Failed to parse state parameter in url '{}'", u);
            }
            return Waiter(&barrier.get(), WaiterConfig{sleep, offset});
        });
    }

} // namespace sardine::sync
