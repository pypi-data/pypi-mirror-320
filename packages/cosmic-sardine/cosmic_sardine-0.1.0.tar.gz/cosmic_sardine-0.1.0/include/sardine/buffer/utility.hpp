#pragma once

#include <sardine/type.hpp>
#include <sardine/context.hpp>

#include <vector>

namespace sardine::buffer
{

// namespace detail
// {

//     template <typename T>
//     struct adaptor_type {
//         // using value_type = T;
//         // using proxy_type = T;
//         using interface_type = T&;
//     };

//     template <cpts::all_view V>
//     struct adaptor_type< V > {
//         // using value_type = typename V::value_type;
//         // using proxy_type = std::span<value_type>;
//         using interface_type = V;
//     };

// } // namespace detail

//     /// Type returned by producer and consumer.
//     /// For values, result is a reference to the value.
//     /// For views, result is the view itself.
//     template<typename T>
//     using interface_type = typename detail::adaptor_type<T>::interface_type;

    template<typename T>
    struct storage
    {
        using type = emu::rm_cvref<T>;

        type value;

        storage(T value)
            : value(value)
        {}
    };

    template<typename Span>
        requires emu::cpts::span<Span> or emu::host::cpts::span<Span>
    struct storage< Span >
    {
        using value_type = typename Span::element_type;
        //TODO: use unique_ptr instead of vector.
        std::vector< value_type > local_data;

        Span value;

        storage(Span shm_data)
            : local_data(shm_data.begin(), shm_data.end())
            , value(local_data)
        {}
    };

    template<typename MdSpan>
        requires emu::cpts::mdspan<MdSpan> or emu::host::cpts::mdspan<MdSpan>
    struct storage< MdSpan >
    {
        using value_type = typename MdSpan::element_type;

        //TODO: use unique_ptr instead of vector.
        std::vector< value_type > local_data;
        MdSpan value;

        storage(MdSpan shm_data)
            : local_data(shm_data.data_handle(), shm_data.required_span_size())
            , value(local_data.data(), shm_data.mapping)
        {}

    };

namespace detail
{

    template<typename Src, typename Dst, typename Ctx>
    struct copy_impl;

    /**
     * @brief Default implementation of copy.
     *
     * @tparam Src
     * @tparam Dst
     * @tparam Ctx
     */
    template<typename Src, typename Dst>
    struct copy_impl<Src, Dst, host_context>
    {
        static void copy(const Src& src, Dst& dst, host_context& ) {
            dst = src;
        }
    };

    template<typename T, typename Ctx>
    struct copy_impl< std::span<T>, std::span<T>, Ctx >
    {
        static void copy(const std::span<T>& src, std::span<T>& dst, Ctx& ) {
            std::copy(src.begin(), src.end(), dst.begin());
        }
    };

} // namespace detail

    template<typename Src, typename Dst, typename Ctx>
    void copy(const Src& src, Dst& dst, Ctx& ctx) {
        detail::copy_impl<Src, Dst, Ctx>::copy(src, dst, ctx);
    }

} // namespace sardine::buffer
