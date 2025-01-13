#include <sardine/region/managed.hpp>
#include <sardine/error.hpp>

#include <sardine/region/managed/manager.hpp>

#include <string>
#include <charconv>

namespace sardine::region
{

    managed::shared_memory& managed_t::shm() const {
        return *shm_;
    }

    managed::segment_manager& managed_t::segment_manager() const {
        return *shm_->get_segment_manager();
    }

    managed::named_range managed_t::named() const {
        return managed::named_range(shm_);
    }

namespace managed
{

    managed_t open(std::string name) {
        return {&manager::instance().open(name.c_str())};
    }

    managed_t create(std::string name, std::size_t file_size) {
        return {&manager::instance().create(name.c_str(), file_size)};
    }

    managed_t open_or_create(std::string name, std::size_t file_size) {
        return {&manager::instance().open_or_create(name.c_str(), file_size)};
    }

} // namespace managed

} // namespace sardine::region
