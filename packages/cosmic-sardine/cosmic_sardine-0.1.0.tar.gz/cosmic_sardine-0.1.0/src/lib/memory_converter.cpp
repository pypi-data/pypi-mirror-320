#include <sardine/memory_converter.hpp>

#include <list>

namespace sardine
{

namespace registry
{
    using converter_list = std::list<converter_t>;
    using revert_converter_list = std::list<revert_converter_t>;

    converter_list& instance() {
        static converter_list list;
        return list;
    }

    revert_converter_list& revert_instance() {
        static revert_converter_list list;
        return list;
    }

    void register_converter( converter_t converter, revert_converter_t revert_converter ) {
        instance().push_back(std::move(converter));
        revert_instance().push_back(std::move(revert_converter));
    }

} // namespace registry

    result<container_b> convert_bytes( bytes_and_device input, device_type_t requested_dt )
    {
        if ( requested_dt == input.device.device_type  // The device type match
          or requested_dt == device_type_t::kDLExtDev) // the requested device type is unspecified
                return container_b(input.data, std::move(input.region.capsule()));

        for (auto& converter : registry::instance())
            // converter return optional. nullopt expresses it did nothing so we try with the next one.
            EMU_UNWRAP_RETURN_IF_TRUE(converter(std::move(input), requested_dt));

        return make_unexpected(errc::location_conversion_not_handle);
    }

    optional<span_b> revert_convert_bytes( span_cb input )
    {
        for (auto& r_converter : registry::revert_instance())
            EMU_UNWRAP_RETURN_IF_TRUE(r_converter(input));

        return nullopt;
    }

} // namespace sardine
