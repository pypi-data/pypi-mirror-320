#pragma once

#include <sardine/type.hpp>
#include <sardine/type/url.hpp>
#include <sardine/package/interface.hpp>

#include <functional>

namespace sardine::package
{

namespace registry
{

    using buffer_package_factory = std::function<result<s_buffer_package>(const sardine::url_view&, device_type_t requested_dt)>;

    using memory_package_factory = std::function<result<s_memory_package>(const sardine::url_view&, device_type_t requested_dt)>;

    void register_buffer_package_factory(string&& scheme_name, buffer_package_factory&& creator);

    void register_memory_package_factory(string&& scheme_name, memory_package_factory&& creator);

} // namespace registry

    result<s_buffer_package> url_to_buffer_package(const sardine::url_view& u, device_type_t requested_dt);

    inline s_buffer_package url_to_buffer_package_or_throw(const sardine::url_view& u, device_type_t requested_dt) {
        return EMU_UNWRAP_RES_OR_THROW(url_to_buffer_package(u, requested_dt));
    }

    result<s_memory_package> url_to_memory_package(const sardine::url_view& u, device_type_t requested_dt);

    inline s_memory_package url_to_memory_package_or_throw(const sardine::url_view& u, device_type_t requested_dt) {
        return EMU_UNWRAP_RES_OR_THROW(url_to_memory_package(u, requested_dt));
    }

} // namespace sardine::package

#ifndef NDEBUG // Debug mode

#include <fmt/format.h>

/// In debug mode, this macro will print a message to the console when the factory is registered.
/// Hopefully, this will happen when the shared library is loaded.

/// Note: extern "C" is used to prevent name mangling. thus, it is then possible when compiling a static library
/// to force the linker to keep the symbols using the "-Wl,-u,NAME" flag with NAME being the name of the constructor.

#define SARDINE_REGISTER_BUFFER_PACKAGE_FACTORY(NAME, SCHEME, CREATOR)                  \
    extern "C" __attribute__ ((constructor)) void NAME() {                              \
        fmt::print("Registering buffer translator factory: " #NAME "\n");               \
        ::sardine::package::registry::register_buffer_package_factory(SCHEME, CREATOR); \
    }

#define SARDINE_REGISTER_MEMORY_PACKAGE_FACTORY(NAME, SCHEME, CREATOR)                  \
    extern "C" __attribute__ ((constructor)) void NAME() {                              \
        fmt::print("Registering memory translator factory: " #NAME "\n");               \
        ::sardine::package::registry::register_memory_package_factory(SCHEME, CREATOR); \
    }

#else // Release mode

#define SARDINE_REGISTER_BUFFER_PACKAGE_FACTORY(NAME, SCHEME, CREATOR)                  \
    extern "C" __attribute__ ((constructor)) void NAME() {                              \
        ::sardine::package::registry::register_buffer_package_factory(SCHEME, CREATOR); \
    }

#define SARDINE_REGISTER_MEMORY_PACKAGE_FACTORY(NAME, SCHEME, CREATOR)                  \
    extern "C" __attribute__ ((constructor)) void NAME() {                              \
        ::sardine::package::registry::register_memory_package_factory(SCHEME, CREATOR); \
    }

#endif
