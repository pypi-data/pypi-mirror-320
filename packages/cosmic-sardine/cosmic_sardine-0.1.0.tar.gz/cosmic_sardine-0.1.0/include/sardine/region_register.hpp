#pragma once

#include <sardine/type.hpp>
#include <sardine/type/url.hpp>

#include <functional>

namespace sardine
{

namespace registry
{
    // A function that converts a region of bytes to a url.
    // Since there is no way to know which function can actually convert the bytes to a url,
    // optional nullopt indicates that the function did not convert the bytes to a url.
    // The result error state indicates that it was the correct function but it failed.
    using bytes_to_url_t = std::function<optional<result<url>>(span_cb)>;

    void register_url_region_converter( string scheme_name, bytes_to_url_t btu);


} // namespace registry

    optional<result<url>> dynamic_url_from_bytes( span_cb data );

} // namespace sardine

#ifndef NDEBUG // Debug mode

#include <fmt/format.h>

#define SARDINE_REGISTER_URL_CONVERTER(NAME, SCHEME, BTU)      \
    extern "C" __attribute__ ((constructor)) void NAME() {  \
        fmt::print("Registering url converter: " #NAME "\n"); \
        ::sardine::registry::register_url_region_converter(SCHEME, BTU); \
    }

#else // Release mode

#define SARDINE_REGISTER_URL_CONVERTER(NAME, SCHEME, BTU)      \
    extern "C" __attribute__ ((constructor)) void NAME() {  \
        ::sardine::registry::register_url_region_converter(SCHEME, BTU); \
    }

#endif
