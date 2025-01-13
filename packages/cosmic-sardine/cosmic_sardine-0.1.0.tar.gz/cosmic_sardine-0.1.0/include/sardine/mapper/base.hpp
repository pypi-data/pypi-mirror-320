#pragma once

// #include <sardine/type.hpp>
// #include <sardine/type/url.hpp>
// #include <sardine/error.hpp>

// #include <sardine/mapping/base.hpp>

// #include <emu/concepts.hpp>
// #include <emu/span.hpp>
// #include <emu/mdspan.hpp>
// #include <type_traits>


#include <sardine/type.hpp>
#include <sardine/error.hpp>
#include <sardine/mapping.hpp>
#include <sardine/sink.hpp>

#include <emu/type_traits.hpp>
#include <emu/concepts.hpp>
#include <emu/cstring_view.hpp>
#include <emu/capsule.hpp>
#include <emu/numeric_type.hpp>
#include <emu/type_name.hpp>

#include <ranges>
#include <system_error>

namespace sardine
{

namespace mapper_cpts
{

    // A view is a non owning type that wrap over a pointer. It includes C++ reference and pointers.
    template<typename T>
    concept view = (emu::cpts::pointer<T> or emu::cpts::ref<T>)
        or (emu::cpts::any_view<T> and not emu::cpts::any_owning<T>)
        or (emu::cpts::any_string_view<T>);

    // Similar to a view, it also accept a emu::capsule that allow to extend value lifetime.
    // Only supported by emu library, under the any_owning concept.
    template<typename T>
    concept capsule_container = emu::cpts::any_owning<T>;

    // A copy container is a owning type that cannot old any external pointer.
    // It includes regular POD types, vector and string.
    template<typename T>
    concept copy_container = (not view<T> and not capsule_container<T>);

    template<typename T>
    concept contiguous = std::ranges::contiguous_range<T>;

    // Includes all types that use mapping to access data. For now, only md[span/container] model this concept.
    template<typename T>
    concept mapped = emu::cpts::any_mdspan<T>;

    // Concept that describe a single value type.
    template<typename T>
    concept scalar = (not contiguous<T>) and (not mapped<T>);

} // namespace mapper_cpts

namespace detail
{

namespace cpts
{

    /**
     * @brief Concept to check if a type T has a static member function `more_check`
     * that takes a constant reference to `interface::mapping` and returns
     * a `std::error_code`.
     *
     * @tparam T The type to be checked.
     */
    template<typename T>
    concept has_more_check = requires(const interface::mapping& md) {
        { T::more_check(md) } -> std::same_as<std::error_code>;
    };

} // namespace cpts

    template<typename Derived>
    struct default_type_mapper
    {
        using mapper_t = Derived;

        static std::error_code check(const interface::mapping& md) {

            using value_type = typename mapper_t::value_type;
            using element_type = typename mapper_t::element_type;

            EMU_TRUE_OR_RETURN_EC_LOG(md.item_size() == sizeof(value_type), errc::mapper_item_size_mismatch,
                "incompatible item size between mapping : {} and requested type {} : {}", md.item_size(), emu::type_name<value_type>, sizeof(value_type));

            EMU_TRUE_OR_RETURN_EC_LOG(emu::is_const<element_type> or (not md.is_const()), errc::mapper_const,
                "Mapping constness ({}) is incompatible with requested type {}", md.is_const(), emu::type_name<value_type>);

            // test if Derived has a "more_check" method.
            if constexpr (cpts::has_more_check<Derived>)
                return Derived::more_check(md);

            return success;
        }
    };

} // namespace detail

    template<typename T>
    struct type_mapper : detail::default_type_mapper< type_mapper<T> >
    {
        using type = T;
        // Remove reference and pointer.
        using element_type = emu::rm_ptr<emu::rm_ref<type>>;
        // Remove constness.
        using value_type = emu::rm_const<element_type>;

        size_t offset_ = 0;

        type_mapper(size_t offset) : offset_(offset) {}

        static std::error_code more_check(const interface::mapping& md) {
            EMU_TRUE_OR_RETURN_EC_LOG(md.extents().size() == 0, errc::mapper_not_scalar,
                "mapping is not scalar, extents are {}", md.extents());

            return success;
        }

        static type_mapper from_mapping(const interface::mapping& md) {
            return type_mapper{md.offset()};
        }

        static type_mapper from(const type&) {
            //TODO: consider capturing T in a capsule. NO !
            return type_mapper{0};
        }

        type_mapper() = default;
        type_mapper(type_mapper&&) = default;
        type_mapper(const type_mapper&) = default;

        type_mapper& operator=(const type_mapper&) = default;
        type_mapper& operator=(type_mapper&&) = default;

        ~type_mapper() = default;

        size_t size() const { return 1; }
        size_t offset() const { return offset_; }
        size_t lead_stride() const { return 1; }

        auto convert(const container_b& buffer) const -> decltype(auto) {
            //Note: We do nothing with the capsule here, since we don't have "scalar" types that takes it.
            EMU_ASSERT_MSG(buffer.size() >= sizeof(value_type), "Buffer size is invalid.");
            auto addr = reinterpret_cast<value_type*>(buffer.data()) + offset_;
            if constexpr (emu::is_ptr<T>)
                return addr;
            else
                return *addr;
        }

        template<typename TT>
        static auto as_bytes(TT&& value) {
            return emu::as_auto_bytes(std::span{&value, 1});
        }

        default_mapping mapping() const {
            return default_mapping(
                  /* extents = */ std::vector<size_t>{},
                  /* strides = */ std::vector<size_t>{},
                  /* data_type = */ emu::dlpack::data_type_ext<T>,
                  /* offset = */ offset_,
                  /* is_const = */ emu::is_const<T>
            );
        }

    };

    template<mapper_cpts::contiguous T>
    struct type_mapper< T > : detail::default_type_mapper<type_mapper<T>>
    {

        using type = T;
        // only consistent way to know if range element is const or not.
        using element_type = emu::rm_ref<std::ranges::range_reference_t<T>>;
        using value_type = emu::rm_const<element_type>;

        size_t offset_ = 0;
        size_t size_ = 0;

        type_mapper(size_t offset, size_t size) : offset_(offset), size_(size) {}

    public:
        static std::error_code more_check(const interface::mapping& md) {
            EMU_TRUE_OR_RETURN_EC_LOG(md.item_size() == sizeof(value_type), errc::mapper_item_size_mismatch,
                "incompatible item size between mapping : {} and requested type {} : {}", md.item_size(), emu::type_name<value_type>, sizeof(value_type));

            EMU_TRUE_OR_RETURN_EC_LOG(not md.is_strided(), errc::mapper_incompatible_stride,
                "mapping is strided, type_mapper does not support it. strides are {}", md.strides());

            EMU_TRUE_OR_RETURN_EC_LOG(emu::is_const<T> or (not md.is_const()), errc::mapper_const,
                "Mapping to const data, but type_mapper requires mutable data type {}", emu::type_name<element_type>);

            return success;
        }

        static type_mapper from_mapping(const interface::mapping& md) {
            // We accept n dimension mapping as long as it is contiguous.
            size_t size = 1; for (auto e : md.extents()) size *= e;

            return type_mapper{md.offset(), size};
        }

        static type_mapper from(const T& value) {
            return type_mapper{0, std::ranges::size(value)};
        }

        type_mapper() = default;
        type_mapper(type_mapper&&) = default;
        type_mapper(const type_mapper&) = default;

        type_mapper& operator=(const type_mapper&) = default;
        type_mapper& operator=(type_mapper&&) = default;


        ~type_mapper() = default;

        size_t size() const { return size_; }
        size_t offset() const { return offset_; }
        size_t lead_stride() const { return 1; }

        T convert(const container_b& buffer) const {
            EMU_ASSERT_MSG(buffer.size() >= size() * sizeof(value_type), "Buffer size is invalid.");

            auto view = emu::as_t<element_type>(buffer).subspan(offset_, size_);

            if constexpr (mapper_cpts::capsule_container<T>)
                return T(view.begin(), view.end(), buffer.capsule());
            else
                return T(view.begin(), view.end());
        }

        T convert(container_b&& buffer) const {
            // Mapper will be destroyed after this call, so we need to keep the capsule alive.
            if constexpr (not mapper_cpts::capsule_container<T>)
                sink(emu::capsule(buffer.capsule()));

            return static_cast<const type_mapper*>(this)->convert(buffer);
        }

        template<typename TT>
        static auto as_bytes(TT&& value) {
            return emu::as_auto_bytes(std::span{value});
        }

        type_mapper<element_type> close_lead_dim() const {
            return {offset()};
        }

        default_mapping mapping() const {
            return default_mapping(
                  /* extents = */ std::vector<size_t>{size_},
                  /* strides = */ std::vector<size_t>{},
                  /* data_type = */ emu::dlpack::data_type_ext<value_type>,
                  /* offset = */ offset_,
                  /* is_const = */ emu::is_const<element_type>
            );
        }

        type_mapper subspan(size_t new_offset, size_t new_size) const {
            EMU_ASSERT_MSG(new_offset + new_size <= size_, "Subspan is out of bound.");

            std::span<const byte> fake_span{reinterpret_cast<const byte*>(offset_), size_};

            // let span do the computation to get the new subspan.
            auto sv = fake_span.subspan(new_offset, new_size);

            // sv.data() is the new offset and sv.size() is the new size.
            return {reinterpret_cast<size_t>(sv.data()), sv.size()};
        }
    };


    template<mapper_cpts::mapped T>
    struct type_mapper< T > : detail::default_type_mapper<type_mapper<T>>
    {
        using type = T;

        using element_type = typename T::element_type;
        using value_type = typename T::value_type;

        using extents_type = typename T::extents_type;
        using layout_type      = typename T::layout_type;
        using accessor_type    = typename T::accessor_type;
        using mapping_type = typename T::mapping_type;

        size_t offset_ = 0;
        mapping_type mapping_ = {};

        type_mapper(size_t offset, const mapping_type& mapping)
            : offset_(offset)
            , mapping_(mapping)
        {}

        static std::error_code more_check(const interface::mapping& md) {
            EMU_TRUE_OR_RETURN_EC_LOG(md.item_size() == sizeof(value_type), errc::mapper_item_size_mismatch,
                "incompatible item size between mapping : {} and requested type {} : {}", md.item_size(), emu::type_name<value_type>, sizeof(value_type));

            EMU_TRUE_OR_RETURN_EC_LOG(emu::is_const<T> or (not md.is_const()), errc::mapper_const,
                "incompatible constness between mapping : {} and requested type {}", md.is_const(), emu::type_name<value_type>);

            EMU_TRUE_OR_RETURN_EC_LOG(md.extents().size() == extents_type::rank(), errc::mapper_rank_mismatch,
                "incompatible rank between mapping : {} and requested type {}", md.extents().size(), emu::type_name<value_type>);

            if constexpr (not std::same_as<layout_type, emu::layout_stride>)
                EMU_TRUE_OR_RETURN_EC_LOG(md.is_strided(), errc::mapper_incompatible_stride,
                    "mapping is strided, type_mapper does not support it. strides are {}", md.strides());

            return success;
        }

        static type_mapper from_mapping(const interface::mapping& md) {
            return type_mapper{md.offset(), create_mapping<mapping_type>(md)};
        }

        static type_mapper from(const T& mdspan) {
            return type_mapper{0, mdspan.mapping()};
        }

        type_mapper() = default;
        type_mapper(type_mapper&&) = default;
        type_mapper(const type_mapper&) = default;

        type_mapper& operator=(const type_mapper&) = default;
        type_mapper& operator=(type_mapper&&) = default;


        ~type_mapper() = default;

        size_t size() const { return mapping_.required_span_size(); }
        size_t offset() const { return offset_; }
        size_t lead_stride() const { return mapping_.stride(0); } // what about layout_f ?

        auto close_lead_dim() const {
            return submdspan(0);
        }

        T convert(const container_b& buffer) const {
            auto view = emu::as_t<element_type>(buffer).subspan(offset_);

            EMU_ASSERT_MSG(view.size() >= mapping_.required_span_size(), "Buffer size is invalid.");

            if constexpr (mapper_cpts::capsule_container<T>)
                return T(view.data(), mapping_);
            else
                return T(view.data(), mapping_);
        }

        T convert(container_b&& buffer) {
            // Mapper will be destroyed after this call, so we need to keep the capsule alive.
            if constexpr (not mapper_cpts::capsule_container<T>)
                sink(emu::capsule(buffer.capsule()));

            return static_cast<const type_mapper*>(this)->convert(buffer);
        }

        template<typename TT>
        static auto as_bytes(TT&& value) {
            return emu::as_auto_bytes(std::span{value.data_handle(), value.mapping().required_span_size()});
        }

        default_mapping mapping() const {
            std::vector<size_t> extents; extents.resize(extents_type::rank());
            for (size_t i = 0; i < extents_type::rank(); ++i)
                extents[i] = mapping_.extents().extent(i);

            std::vector<size_t> strides;
            if constexpr (not mapping_type::is_always_exhaustive())
                if (not mapping_.is_exhaustive()) {
                    strides.resize(extents_type::rank());
                    for (size_t i = 0; i < extents_type::rank(); ++i)
                        strides[i] = mapping_.stride(i);
                }


            return default_mapping(
                  /* extents = */ std::move(extents),
                  /* strides = */ std::move(strides),
                  /* data_type = */ emu::dlpack::data_type_ext<value_type>,
                  /* offset = */ offset_,
                  /* is_const = */ emu::is_const<element_type>
            );
        }

        template<class... SliceSpecifiers>
        auto submdspan(SliceSpecifiers... specs) const
        {

            // Create a fake mdspan from offset and size. Use deduction guide.
            // considere the offset as a pointer to the first element of the mdspan.
            // byte is 1 byte long, so the offset is in bytes.
            emu::mdspan fake_mdspan(reinterpret_cast< const byte* >(offset_), this->mapping_);


            // let mdspan do the computation to get the new submdspan.
            auto sv = emu::submdspan(fake_mdspan, specs...);

            using new_mapping_t = typename decltype(sv)::mapping_type;
            using new_mdspan_t = emu::mdspan<element_type, typename new_mapping_t::extents_type, typename new_mapping_t::layout_type>;

            // The pointer returned by data_handle is the new offset.
            return sardine::type_mapper<new_mdspan_t>{reinterpret_cast<size_t>(sv.data_handle()), sv.mapping()};
        }

    };

} // namespace sardine
