#pragma once

#include <sardine/type.hpp>
#include <sardine/error.hpp>

#include <emu/assert.hpp>

#include <boost/interprocess/mapped_region.hpp>
#include <boost/interprocess/file_mapping.hpp>
#include <boost/interprocess/shared_memory_object.hpp>

namespace sardine::region::host
{
    using m_region = boost::interprocess::mapped_region;

    constexpr auto shm_idenfier = "shm";
    constexpr auto file_idenfier = "file";
    constexpr auto local_idenfier = "local";

    enum class ressource_kind {
        shm,
        file,
        local
    };

    inline auto format_as(ressource_kind r_kind) -> cstring_view {
        switch (r_kind) {
            case ressource_kind::shm  : return   shm_idenfier;
            case ressource_kind::file : return  file_idenfier;
            case ressource_kind::local: return local_idenfier;
        }
        EMU_UNREACHABLE;
    }

    inline auto ressource_kind_from(cstring_view id) -> result<ressource_kind> {
        if (id == shm_idenfier  ) return ressource_kind::shm;
        if (id == file_idenfier ) return ressource_kind::file;
        if (id == local_idenfier) return ressource_kind::local;

        EMU_RETURN_UN_EC_LOG(errc::host_unknow_region_kind,
            "Unknow region kind: {}", id);
    }

    // A handle to a shared memory region.
    struct handle {
        m_region region;
        ressource_kind r_kind;
    };


    // A pointer to a shared memory location.
    struct region_handle {
        cstring_view name;
        size_t offset;
        ressource_kind r_kind;
    };

    inline auto map(const handle &r) -> span_b {
        return {static_cast<byte*>(r.region.get_address()), r.region.get_size()};
    }

} // namespace sardine::region::host
