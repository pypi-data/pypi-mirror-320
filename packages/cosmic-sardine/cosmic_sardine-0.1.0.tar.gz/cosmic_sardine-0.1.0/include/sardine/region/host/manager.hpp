#pragma once

#include <sardine/type.hpp>
#include <sardine/region/host/utility.hpp>

#include <emu/associative_container.hpp>

namespace sardine::region::host
{

    struct manager : protected emu::unordered_map<string, handle>
    {
        using base = emu::unordered_map<string, handle>;

        static manager &instance();

    private:
        manager() = default;

    public:
        manager(const manager &) = delete;
        manager(manager &&) = delete;

        span_b open_shm(string name);
        span_b create_shm(string name, size_t size);
        span_b open_or_create_shm(string name, size_t size);

        span_b open_file(string path);
        span_b create_file(string path, size_t size);
        span_b open_or_create_file(string path, size_t size);

        span_b at(cstring_view name);

        optional<region_handle> find_handle(const byte* ptr);
    };

} // namespace sardine::region::host
