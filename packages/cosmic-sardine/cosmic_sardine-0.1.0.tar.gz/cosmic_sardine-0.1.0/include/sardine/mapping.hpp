#pragma once

#include <sardine/type.hpp>
#include <sardine/type/url.hpp>

#include <fmt/format.h>
#include <fmt/ranges.h>

namespace sardine
{

    constexpr auto extent_key = "extent";
    constexpr auto stride_key = "stride";

    constexpr auto data_type_code_key = "dtc";
    constexpr auto bits_key = "bits";
    constexpr auto lanes_key = "lanes";

    constexpr auto offset_key = "offset";
    constexpr auto is_const_key = "const";

namespace interface
{

    struct mapping
    {
        virtual ~mapping() = default;

        virtual span<const size_t> extents() const = 0;

        virtual bool is_strided() const { return false; }
        virtual span<const size_t> strides() const { return {}; }

        virtual data_type_ext_t data_type() const = 0;

        virtual size_t offset() const = 0;
        virtual bool is_const() const { return false; }

        size_t item_size() const {
            auto dt = data_type();
            return dt.bits * dt.lanes / CHAR_BIT;
        }

    };

} // namespace interface

    void update_url(url& u, const interface::mapping& desc);

    struct default_mapping : interface::mapping
    {
        std::vector<size_t> extents_;
        std::vector<size_t> strides_;

        // device_t device_;
        data_type_ext_t data_type_;

        size_t offset_;
        bool is_const_;

        default_mapping() = default;

        default_mapping(
            std::vector<size_t> extents, std::vector<size_t> strides, data_type_ext_t data_type, size_t offset, bool is_const
        );

        default_mapping(const default_mapping&) = default;

        default_mapping& operator=(const default_mapping&) = default;

        ~default_mapping() = default;

        span<const size_t> extents() const override { return extents_; }
        bool is_strided() const override { return not strides_.empty(); }
        span<const size_t> strides() const override { return strides_; }

        // device_t device() const override { return device_; }
        data_type_ext_t data_type() const override { return data_type_; }

        size_t offset() const override { return offset_; }
        bool is_const() const override { return is_const_; }
    };

    result<default_mapping> make_mapping(urls::params_view params);

    template<typename Mapping>
    auto create_mapping(const interface::mapping& descriptor) -> Mapping {
        using Extent = typename Mapping::extents_type;
        using Layout = typename Mapping::layout_type;

        using array_t = std::array<size_t, Extent::rank()>;

        array_t extents; std::ranges::copy(descriptor.extents(), extents.begin());

        constexpr static auto rank = Mapping::extents_type::rank();

        if constexpr ( std::same_as<Layout, emu::layout_right>
                    or std::same_as<Layout, emu::layout_left> ) {
            return Mapping(extents);

        } else if constexpr (std::same_as<Layout, emu::layout_stride> ) {

            if (not descriptor.is_strided())
                // not having stride if fine, we can compute it.
                return Mapping(extents);
            else {
                array_t strides; std::ranges::copy(descriptor.strides(), strides.begin());

                if (strides.size() != rank)
                    return make_unexpected(errc::mapper_rank_mismatch);

                return Mapping(extents, strides);
            }

        } else
            static_assert(emu::dependent_false<Mapping>, "Layout is not supported.");
    }


} // namespace sardine
