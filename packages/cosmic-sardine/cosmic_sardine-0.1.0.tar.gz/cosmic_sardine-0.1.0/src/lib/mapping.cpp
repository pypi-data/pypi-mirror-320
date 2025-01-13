#include <sardine/mapping.hpp>

namespace sardine
{

    void update_url(url& u, const interface::mapping& desc) {
        auto params = u.params();

        auto dtype = desc.data_type();
        params.set(data_type_code_key, fmt::to_string(dtype.code));
        params.set(bits_key, fmt::to_string(dtype.bits));
        // if dtype is not vectorized, do not bother specifying lanes number.
        if (dtype.lanes != 1)
            params.set(lanes_key, fmt::to_string(dtype.lanes));

        auto extents = desc.extents();

        if (extents.size() > 0) {
            params.set(extent_key, fmt::format("[{}]", fmt::join(extents, ",")));

            if (desc.is_strided())
                params.set(stride_key, fmt::format("[{}]", fmt::join(desc.strides(), ",")));
        }

        if(desc.is_const())
            // set the key with no value.
            params.append({is_const_key, nullptr});

    }

    default_mapping::default_mapping(
        std::vector<size_t> extents, std::vector<size_t> strides, data_type_ext_t data_type, size_t offset, bool is_const
    )
        : extents_(std::move(extents))
        , strides_(std::move(strides))
        // , device_(device)
        , data_type_(data_type)
        , offset_(offset)
        , is_const_(is_const)
    {}

    result<default_mapping> make_mapping(urls::params_view params) {
        using vector_t = std::vector<size_t>;

        auto extents = urls::try_parse_at<vector_t>(params, extent_key).value_or(vector_t{});

        auto strides = urls::try_parse_at<vector_t>(params, stride_key).value_or(vector_t{});

        using namespace emu::dlpack;

        uint8_t code = EMU_UNWRAP(urls::try_parse_number_at<uint8_t>(params, data_type_code_key));
        uint64_t bits = EMU_UNWRAP(urls::try_parse_number_at<uint64_t>(params, bits_key));
        uint16_t lanes = EMU_UNWRAP(urls::try_parse_number_at(params, lanes_key, uint16_t(1)));

        data_type_ext_t data_type{code, bits, lanes};

        auto offset = urls::try_parse_at<size_t>(params, offset_key).value_or(0);
        auto is_const = urls::try_parse_at<bool>(params, is_const_key).value_or(false);

        return {in_place, std::move(extents), std::move(strides)/* , device*/, data_type, offset, is_const};
    }


} // namespace sardine
