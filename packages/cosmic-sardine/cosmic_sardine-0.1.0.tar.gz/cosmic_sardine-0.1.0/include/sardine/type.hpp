#pragma once

#include <sardine/config.hpp>
#include <sardine/logger.hpp>
#include <sardine/error.hpp>

#include <emu/capsule.hpp>
#include <emu/type_traits.hpp>
#include <emu/expected.hpp>
#include <emu/optional.hpp>
#include <emu/cstring_view.hpp>
#include <emu/span.hpp>
#include <emu/container.hpp>
#include <emu/detail/dlpack_types.hpp>

#include <cstddef>
#include <string>
#include <string_view>

namespace sardine
{
    using std::size_t, std::byte, std::string, std::string_view, std::dynamic_extent;

    using emu::span, emu::cstring_view;

    using emu::optional, emu::nullopt, emu::in_place, emu::unexpected;

    using emu::dlpack::data_type_code_t;
    using emu::dlpack::device_t, emu::dlpack::device_type_t;
    using emu::dlpack::data_type_t, emu::dlpack::data_type_ext_t;

    using span_b = std::span<std::byte>;
    using span_cb = std::span<const std::byte>;

    using container_b = emu::container<byte>;
    using container_cb = emu::container<const byte>;

    struct bytes_and_device {
        container_b region;
        span_b data;
        emu::dlpack::device_t device;
    };

} // namespace sardine
