#include <sardine/url.hpp>

#include <sardine/type.hpp>
#include <sardine/package/registry.hpp>
#include <sardine/region/host.hpp>
#include <sardine/memory_converter.hpp>
#include <sardine/region_register.hpp>

namespace sardine::detail
{

    // // TODO: flatten the optional of result.
    // // I think it's because we could try other regions if detail::bytes_from_url fails.
    // result<container_b> bytes_from_url( const url_view& u, device_type_t requested_dt) {
    //     auto memory_package = EMU_UNWRAP(package::url_to_memory_package( u, requested_dt ));

    //     auto bytes = memory_package->bytes();

    //     return container_b(bytes, std::move(memory_package));
    // }

    result<url> url_from_bytes( span_cb bytes ) {

        if (auto maybe_bytes = revert_convert_bytes(bytes); maybe_bytes)
            bytes = *maybe_bytes; // update the bytes from the reverted bytes and revert the convert_bytes function in bytes_from_url.

        EMU_UNWRAP_RETURN_IF_TRUE(dynamic_url_from_bytes(bytes));

        // always keep host::url_from_bytes as the last resort since it may be able to find the url from the bytes.
        EMU_UNWRAP_RETURN_IF_TRUE(region::host::url_from_bytes(bytes));

        return make_unexpected( errc::url_resource_not_registered );
    }

} // namespace sardine::detail
