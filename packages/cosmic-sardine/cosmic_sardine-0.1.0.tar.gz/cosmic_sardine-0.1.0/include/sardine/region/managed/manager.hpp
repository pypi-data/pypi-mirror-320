#pragma once

#include <sardine/type.hpp>
#include <sardine/region/managed/utility.hpp>

#include <emu/associative_container.hpp>

namespace sardine::region::managed
{

    struct manager : protected emu::unordered_map<std::string, shared_memory>
    {
        using base = emu::unordered_map<std::string, shared_memory>;

        static manager& instance();

    private:
        manager() = default;

    public:
        manager(const manager&) = delete;
        manager(manager&&) = delete;

        shared_memory& open(std::string name);
        shared_memory& create(std::string name, size_t file_size);
        shared_memory& open_or_create(std::string name, size_t file_size);

        shared_memory& at(cstring_view name);

        optional<shm_handle> find_handle(const byte* ptr);

        using base::find;
        using base::begin;
        using base::end;
    };

} // namespace sardine::region::managed
