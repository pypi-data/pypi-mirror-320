#pragma once

#include <sardine/type.hpp>
#include <sardine/type/url.hpp>

#include <filesystem>

namespace sardine::region::host
{
    namespace fs = std::filesystem;

    constexpr auto url_scheme = "host";

    span_b open_shm(string name, bool read_only = false);

    span_b create_shm(string name, size_t size, bool read_only = false);

    span_b open_or_create_shm(string name, size_t size, bool read_only = false);

    template<typename T>
    span<T> open_shm(string name, bool read_only = false) {
        return emu::as_t<T>(open_shm(std::move(name), read_only));
    }

    template<typename T>
    span<T> create_shm(string name, size_t size, bool read_only = false) {
        return emu::as_t<T>(create_shm(std::move(name), size * sizeof(T), read_only));
    }

    template<typename T>
    span<T> open_or_create_shm(string name, size_t size, bool read_only = false) {
        return emu::as_t<T>(open_or_create_shm(std::move(name), size * sizeof(T), read_only));
    }

    span_b open_file(fs::path path, bool read_only = false);

    span_b create_file(fs::path path, size_t size, bool read_only = false);

    span_b open_or_create_file(fs::path path, size_t size, bool read_only = false);

    template<typename T>
    span<T> open_file(fs::path path, bool read_only = false) {
        return emu::as_t<T>(open_file(std::move(path), read_only));
    }

    template<typename T>
    span<T> create_file(fs::path path, size_t size, bool read_only = false) {
        return emu::as_t<T>(create_file(std::move(path), size * sizeof(T), read_only));
    }

    template<typename T>
    span<T> open_or_create_file(fs::path path, size_t size, bool read_only = false) {
        return emu::as_t<T>(open_or_create_file(std::move(path), size * sizeof(T), read_only));
    }

    optional<result<url>> url_from_bytes(span_cb data);

    result<container_b> bytes_from_url(const url_view& u, device_type_t requested_dt);

} // namespace sardine::region::host
