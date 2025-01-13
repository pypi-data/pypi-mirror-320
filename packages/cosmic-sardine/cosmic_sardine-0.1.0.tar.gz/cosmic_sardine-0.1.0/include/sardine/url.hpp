#pragma once

#include <sardine/type.hpp>
#include <sardine/type/url.hpp>
#include <sardine/utility.hpp>
#include <sardine/mapper.hpp>
#include <sardine/error.hpp>
#include <sardine/package/registry.hpp>

#include <emu/dlpack.hpp>

namespace sardine
{

namespace detail
{

    result<url> url_from_bytes( span_cb bytes );

    // /// Returns bytes from url. Type info for special regions and bytes convertion.
    // result<container_b> bytes_from_url( const url_view& u, device_type_t requested_dt);

    template<typename T>
    auto from_url( const url_view& u ) -> result<T> {
        using type = emu::rm_cvref<T>;

        constexpr auto requested_dt = emu::location_type_of<type>::device_type;

        auto pkg = EMU_UNWRAP( package::url_to_memory_package(u, requested_dt) );

        return sardine::mapper_from_mapping< type >(pkg->mapping())
            .and_then([pkg = std::move(pkg)](auto mapper) -> result<T> {
                auto bytes = pkg->bytes();
                return std::move(mapper).convert(emu::container(bytes, emu::capsule(std::move(pkg))));
            });
    }

    template<typename T>
    auto url_of(T&& value) -> result<url> {
        using type = emu::rm_cvref<T>;

        using mapper_t = sardine::type_mapper< type >;

        auto bytes = mapper_t::as_bytes(value);

        auto url = EMU_UNWRAP(detail::url_from_bytes( bytes ));

        //TODO: is it safe to maybe move value without invalidating bytes ?
        auto mapping = mapper_t::from(value).mapping();

        // managed_tensor_versioned will be deleted immediately after the call of update_url.
        update_url(url, mapping);

        return url;
    }

} // namespace detail

    template<typename T>
    auto from_url( const url_view& u ) {
        if constexpr ( cpts::from_url_aware<T> )
            //TODO: be sure that it returns a result
            return T::from_url(u);
        else
            return detail::from_url<T>(u);
    }


    template<typename T>
    auto from_url_or_throw( const url_view& u ) -> decltype(auto) {
        decltype(auto) res = EMU_UNWRAP_RES_OR_THROW(from_url<T>(u));

        if constexpr (emu::cpts::specialization_of<decltype(res), std::reference_wrapper>)
            return res.get();
        else
            return res;
    }

    template<typename T>
    result<url> url_of(T&& value) {
        if constexpr ( cpts::url_of_aware< emu::rm_cvref<T> > )
            return value.url_of();
        else
            return detail::url_of(EMU_FWD(value));
    }

    template<typename T>
    url url_of_or_throw(T&& value) {
        return EMU_UNWRAP_RES_OR_THROW(url_of(EMU_FWD(value)));
    }

} // namespace sardine
