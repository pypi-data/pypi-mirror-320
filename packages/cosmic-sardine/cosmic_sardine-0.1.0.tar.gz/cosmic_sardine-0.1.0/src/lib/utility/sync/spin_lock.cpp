#include <sardine/utility/sync/spin_lock.hpp>
#include <sardine/url.hpp>

namespace sardine::sync
{

    result<url> SpinLock::url_of() const {
        return sardine::url_of(*state).map([&](auto&& u){
            using namespace std::string_view_literals;
            if (sleep)
                //this API is so stupid…
                u.params().append(urls::param_view("sleep", "", false));
            return u;
        });
    }

    result<SpinLock> SpinLock::from_url(const sardine::url_view& u) {
        return sardine::from_url<lock_state&>(u).map([&](auto&& state){
            bool sleep = u.params().contains("sleep");
            return SpinLock(&(state.get()), sleep);
        });
    }

} // namespace sardine::sync
