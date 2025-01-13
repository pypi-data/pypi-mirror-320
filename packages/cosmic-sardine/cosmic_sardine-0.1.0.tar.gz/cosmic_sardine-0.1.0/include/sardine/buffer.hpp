#pragma once

#include <sardine/buffer/base.hpp>
#include <sardine/buffer/native.hpp>
#include <sardine/buffer/interface.hpp>
#include <sardine/package/registry.hpp>

#include <emu/info.hpp>

namespace sardine
{

    template<typename T>
    auto box<T>::open(const url_view& u) -> result<box> {
        auto pkg = EMU_UNWRAP(package::url_to_buffer_package(u, emu::location_type_of<T>::device_type));
        auto type_mapper = EMU_UNWRAP(sardine::mapper_from_mapping<T>(pkg->mapping()));

        return box{ type_mapper, std::move(pkg) };
    }

    template<typename T>
    auto producer<T>::open(const url_view& u) -> result<producer> {
        auto pkg = EMU_UNWRAP(package::url_to_buffer_package(u, emu::location_type_of<T>::device_type));
        auto type_mapper = EMU_UNWRAP(sardine::mapper_from_mapping<T>(pkg->mapping()));

        return producer{ type_mapper, std::move(pkg) };
    }

    template<typename T>
    auto consumer<T>::open(const url_view& u) -> result<consumer> {
        auto pkg = EMU_UNWRAP(package::url_to_buffer_package(u, emu::location_type_of<T>::device_type));
        auto type_mapper = EMU_UNWRAP(sardine::mapper_from_mapping<T>(pkg->mapping()));

        return consumer{ type_mapper, std::move(pkg) };
    }

} // namespace sardine

template<typename T, typename CharT>
struct fmt::formatter<sardine::box<T>, CharT> {

    constexpr auto parse(format_parse_context& ctx) {
        return ctx.begin();
    }

    template<typename FormatContext>
    auto format(const sardine::box<T>& box, FormatContext& ctx) {
        return fmt::format_to(ctx.out(), "value({})", emu::info(box.value));
    }
};

template<typename T, typename CharT>
struct fmt::formatter<sardine::producer<T>, CharT> {

    constexpr auto parse(format_parse_context& ctx) {
        return ctx.begin();
    }

    template<typename FormatContext>
    auto format(const sardine::producer<T>& value, FormatContext& ctx) {
        return fmt::format_to(ctx.out(), "producer({})", emu::info(value.view()));
    }
};

template<typename T, typename CharT>
struct fmt::formatter<sardine::consumer<T>, CharT> {

    constexpr auto parse(format_parse_context& ctx) {
        return ctx.begin();
    }

    template<typename FormatContext>
    auto format(const sardine::consumer<T>& value, FormatContext& ctx) {
        return fmt::format_to(ctx.out(), "consumer({})", emu::info(value.view()));
    }
};
