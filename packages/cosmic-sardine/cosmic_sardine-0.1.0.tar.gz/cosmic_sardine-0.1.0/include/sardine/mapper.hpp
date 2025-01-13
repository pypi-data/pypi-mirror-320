#pragma once

#include <sardine/type.hpp>
#include <sardine/type/url.hpp>
#include <sardine/mapper/base.hpp>

namespace sardine
{

    template<typename T>
    auto mapper_from_mapping( const interface::mapping& md ) -> result< type_mapper<T> >
    {
        EMU_CHECK_ERRC_OR_RETURN_LOG(type_mapper<T>::check(md), "mapping check failed");

        return type_mapper<T>::from_mapping(md);
    }

    template<typename T>
    auto mapper_from(T && value) -> type_mapper< emu::rm_ref<T> > {
        return type_mapper< emu::rm_ref<T> >::from(EMU_FWD(value));
    }

    template<typename T>
    auto as_bytes(T && value) {
        return type_mapper< emu::rm_ref<T> >::as_bytes(EMU_FWD(value));
    }

    template<typename T>
    void update_url(url& u, const type_mapper<T>& mapper) {
        auto m = mapper.mapping();

        update_url(u, m);
    }

} // namespace sardine
