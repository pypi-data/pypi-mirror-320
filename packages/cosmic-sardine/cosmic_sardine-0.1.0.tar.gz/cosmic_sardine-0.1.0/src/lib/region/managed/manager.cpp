#include <sardine/region/managed/manager.hpp>

#include <sardine/type.hpp>
#include <sardine/utility.hpp>

#include  <stdexcept>

namespace sardine::region::managed
{

    manager& manager::instance() {
        static manager obj;
        return obj;
    }

    shared_memory& manager::open(std::string name) {
        return find_or_emplace(static_cast<base&>(*this), name, [name] {
            return shared_memory(bi::open_only, name.c_str());
        })->second;
    }

    shared_memory& manager::create(std::string name, size_t file_size) {
        return emplace_or_throw(static_cast<base&>(*this), name, [name, file_size] {
            return shared_memory(bi::create_only, name.c_str(), file_size);
        })->second;
    }

    shared_memory& manager::open_or_create(std::string name, size_t file_size) {
        return find_or_emplace(static_cast<base&>(*this), name, [name, file_size] {
            return shared_memory(bi::open_or_create, name.c_str(), file_size);
        })->second;
    }

    shared_memory& manager::at(cstring_view name) {
#ifdef __cpp_lib_generic_unordered_lookup
        auto it = base::find(name);
#else
        auto it = base::find(std::string(name));
#endif

        EMU_TRUE_OR_THROW_LOG(it != base::end(), errc::managed_unknown_region,
            "No region named {} exists.", name);

        return it->second;
    }

    optional<shm_handle> manager::find_handle(const byte* ptr) {
        for (auto& [name, shm] : *this) {
            if (shm.belongs_to_segment(ptr))
                return shm_handle{cstring_view(name), &shm, shm.get_handle_from_address(ptr)};
        }
        return nullopt;
    }


} // namespace sardine::region::managed
