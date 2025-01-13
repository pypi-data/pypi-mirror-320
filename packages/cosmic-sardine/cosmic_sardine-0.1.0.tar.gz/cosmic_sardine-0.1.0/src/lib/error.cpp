#include <sardine/error.hpp>

namespace sardine
{

    std::string error_category::message( int ev ) const {
        switch (static_cast<errc>(ev)) {
            case errc::success:
                return "success";

            case errc::converter_not_found:
                return "no converter found for device type";

            case errc::local_url_invalid_host:
                return "local url invalid host";
            case errc::local_url_invalid_path:
                return "local url invalid path";

            case errc::json_parse_reference:
                return "json parse reference";
            case errc::json_no_conversion:
                return "type is not parsable from json";
            case errc::json_invalid_json:
                return "could not parse json into requested type";

            case errc::url_resource_not_registered:
                return "resource not registered, cannot generate url";
            case errc::url_unknown_scheme:
                return "url unknown scheme";
            case errc::url_param_not_found:
                return "url does not have the requested parameter";

            case errc::mapper_rank_mismatch:
                return "mapper rank mismatch";
            case errc::mapper_not_scalar:
                return "mapper not scalar";
            case errc::mapper_not_range:
                return "mapper not range";
            case errc::mapper_not_contiguous:
                return "mapper not contiguous";
            case errc::mapper_missing_item_size:
                return "mapper missing item size";
            case errc::mapper_item_size_mismatch:
                return "mapper item size mismatch";
            case errc::mapper_incompatible_stride:
                return "mapper does not support provided stride";
            case errc::mapper_const:
                return "mapper is const";

            case errc::host_type_not_supported:
                return "host type not supported";
            case errc::host_url_invalid_path:
                return "host url invalid path";
            case errc::host_url_offset_overflow:
                return "host url offset overflow";
            case errc::host_url_size_overflow:
                return "host url size overflow";
            case errc::host_incompatible_shape:
                return "host opening with a shape that is incompatible with region "
                    "size";
            case errc::host_unknown_region:
                return "host unknown region";
            case errc::host_unknow_region_kind:
                return "host unknown region kind";
            case errc::host_non_local_region:
                return "host non local region";

            case errc::managed_invalid_url_segment_count:
                return "managed invalid url segment count, expected 2";
            case errc::managed_unknown_region:
                return "managed unknown region";

            case errc::embedded_type_not_handled:
                return "the requested type can not be constructed from json";
            case errc::embedded_url_missing_json:
                return "embedded url is missing the json parameter";

            case errc::cuda_module_not_build:
                return "sardine cuda module is not build. Recompile with "
                    "SARDINE_CUDA";
            case errc::cuda_invalid_memory_type:
                return "cuda invalid memory type";
            case errc::cuda_type_not_supported:
                return "cuda type not supported";
            case errc::cuda_url_invalid_path:
                return "cuda url invalid path";
            case errc::cuda_url_offset_overflow:
                return "cuda url offset overflow";
            case errc::cuda_url_size_overflow:
                return "cuda url size overflow";

            case errc::ring_missing_size:
                return "ring missing size";
            case errc::ring_url_missing_size:
                return "ring url missing size";
            case errc::ring_url_missing_data:
                return "ring url missing data";
            case errc::ring_url_missing_index:
                return "ring url missing index";
            case errc::ring_url_missing_buffer_nb:
                return "ring url missing buffer nb";
            case errc::ring_url_missing_policy:
                return "ring url missing policy";
            case errc::ring_url_invalid_policy:
                return "ring url invalid policy";

            case errc::location_cuda_unsupported_source_memory:
                return "location cuda unsupported source memory";
            case errc::location_cuda_device_region_not_registered:
                return "location cuda device region not registered";
            case errc::location_conversion_not_handle:
                return "no conversion know to the requested device type";
            case errc::python_type_not_supported:
                return "python type is not supported by url";
            case errc::location_could_get_device_pointer:
                return "Could not get the device pointer of the registered region";

            case errc::buffer_translator_not_found:
                return "buffer translator not found";
            case errc::memory_translator_not_found:
                return "memory translator not found";
        }
        return "unknown";
    }

    const char * error_category::name() const noexcept {
        return "sardine";
    }

    const std::error_category& error_category::instance() {
        static const error_category instance;
        return instance;
    }

    std::error_code make_error_code( errc e ) {
        return { static_cast<int>(e), error_category::instance() };
    }

    emu::unexpected<std::error_code> make_unexpected( errc e ) {
        return emu::unexpected<std::error_code>( make_error_code(e) );
    }

} // namespace sardine
