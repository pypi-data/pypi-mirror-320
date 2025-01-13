#pragma once

#include <sardine/type.hpp>
#include <sardine/error.hpp>

#include <functional>

namespace sardine
{

namespace registry
{
    using converter_t = std::function<optional<result<container_b>>(bytes_and_device, device_type_t)>;
    using revert_converter_t = std::function<optional<span_b>(span_cb)>;

    void register_converter( converter_t converter, revert_converter_t revert_converter );

} // namespace registry

    result<container_b> convert_bytes( bytes_and_device input, device_type_t requested_dt );
    optional<span_b> revert_convert_bytes( span_cb input );

} // namespace sardine

#ifndef NDEBUG // Debug mode

#include <fmt/format.h>

#define SARDINE_REGISTER_DEVICE_FINDER(NAME, CONVERTER, REVERT_CONVERTER) \
    extern "C" __attribute__ ((constructor)) void NAME() {                \
        fmt::print("Registering device finder: " #NAME "\n");              \
        ::sardine::registry::register_converter(CONVERTER, REVERT_CONVERTER);       \
    }

#else // Release mode

#define SARDINE_REGISTER_DEVICE_FINDER(NAME, CONVERTER, REVERT_CONVERTER) \
    extern "C" __attribute__ ((constructor)) void NAME() {                \
        ::sardine::registry::register_converter(CONVERTER, REVERT_CONVERTER);       \
    }

#endif
