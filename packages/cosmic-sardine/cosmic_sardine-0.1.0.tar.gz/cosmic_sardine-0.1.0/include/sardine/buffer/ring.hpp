#pragma once

#include "emu/capsule.hpp"
#include <sardine/concepts.hpp>
#include <sardine/context.hpp>
#include <sardine/buffer/base.hpp>
#include <sardine/buffer/interface.hpp>
#include <sardine/mapping.hpp>
// #include <sardine/buffer/adaptor.hpp>
#include <sardine/package/registry.hpp>
#include <sardine/context.hpp>

namespace sardine::ring
{

    constexpr auto url_scheme = "ring";

    constexpr auto data_key       = "r_data";
    constexpr auto index_key      = "r_index";
    constexpr auto offset_key     = "r_offset";
    constexpr auto size_key       = "r_size";
    constexpr auto stride_key     = "r_stride";
    constexpr auto buffer_nb_key  = "r_buffer_nb";
    constexpr auto policy_key     = "r_policy";

    enum class next_policy {
        last, next, check_next
    };

    inline auto format_as(next_policy p) {
        switch (p) {
            case next_policy::last : return "last";
            case next_policy::next : return "next";
            case next_policy::check_next : return "check_next";
        }
        EMU_UNREACHABLE;
    }

    inline result< next_policy > parse_policy( std::string_view s) {
        if (s == "last") return next_policy::last;
        if (s == "next") return next_policy::next;
        if (s == "check_next") return next_policy::check_next;

        EMU_RETURN_UN_EC_LOG(errc::ring_url_invalid_policy,
            "Invalid policy: {}", s);
    }

    struct index
    {

        box<size_t&> global_index; // move to 2 values to be able to detect full vs empty.
        size_t idx;
        size_t buffer_nb;
        next_policy policy;

        size_t save_index = {};

        index(box<size_t&> global_index, size_t buffer_nb, next_policy policy);
        index(size_t& global_index, size_t buffer_nb, next_policy policy);

        void incr_local();
        void decr_local();

        // check if the next index is available
        bool has_next(host_context& ctx);

        void send(host_context& ctx);
        void recv(host_context& ctx);

        void revert_send(host_context& ctx);
        void revert_recv(host_context& ctx);

        sardine::url url_of() const {
            sardine::url u = global_index.url_of();

            auto param_ref = u.params();

            param_ref.set(buffer_nb_key, fmt::to_string(buffer_nb));
            param_ref.set(policy_key, fmt::to_string(policy));

            return u;
        }

        static result<index> open(const url_view& url) {
            auto params = url.params();

            auto buffer_nb = urls::try_parse_at<size_t>(params, buffer_nb_key);
            EMU_TRUE_OR_RETURN_UN_EC(buffer_nb, errc::ring_url_missing_buffer_nb);

            auto opt_policy = urls::try_get_at(params, policy_key);
            EMU_TRUE_OR_RETURN_UN_EC(opt_policy, errc::ring_url_missing_policy);
            auto policy = parse_policy(*move(opt_policy));
            EMU_TRUE_OR_RETURN_ERROR(policy);

            auto global_index = EMU_UNWRAP(box<size_t&>::open(url));

            return index(std::move(global_index), *buffer_nb, *policy);

            // return box<size_t&>::open(url).map([&](auto global_index) -> index {
            //     return index(std::move(global_index), *buffer_nb, *policy);
            // });
        }

    };

    struct memory_package;

    struct view_t
    {
        memory_package* pkg;

        span_b shm_data;
        index idx;

        size_t size;   // size of the buffer
        size_t offset; // distance from the start of the buffer
        size_t stride; // distance between buffers


        view_t(memory_package* pkg, span_b shm_data, index idx, size_t size, size_t offset, size_t stride)
            : pkg(pkg)
            , shm_data(shm_data)
            , idx(std::move(idx))
            , size(size)
            , offset(offset)
            , stride((stride == std::dynamic_extent) ? size : stride)
        {}

        view_t(const view_t&) = default;

        span_b bytes() {
            return shm_data.subspan(idx.idx * stride + offset, size);
        }

        sardine::url url_of() const;

    };

    struct producer : view_t, buffer::interface::producer
    {

        using base_t = ring::view_t;

        producer(base_t view)
            : base_t(std::move(view))
        {
            // producer always set index to the next buffer.
            this->idx.incr_local();
        }

        void send(host_context& ctx) override {
            idx.send(ctx);
        }

        void revert(host_context& ctx) override {
            idx.revert_send(ctx);
        }

        span_b bytes() override { return base_t::bytes(); }
        url url_of() const override { return base_t::url_of(); }

    };

    struct consumer : view_t, buffer::interface::consumer
    {
        using base_t = ring::view_t;

        consumer(base_t view)
            : base_t(std::move(view))
        {}

        void recv(host_context& ctx) override {
            idx.recv(ctx);
        }

        void revert(host_context& ctx) override {
            idx.revert_recv(ctx);
        }

        span_b bytes() override { return base_t::bytes(); }
        url url_of() const override { return base_t::url_of(); }

    };


    struct memory_package : sardine::package::interface::memory_package
    {
        span_b shm_data;
        const interface::mapping* mapping_;

        ring::producer prod;
        ring::consumer cons;

        url data_url;

        emu::capsule keep_alive;

        memory_package(
            span_b shm_data, const interface::mapping& mapping,
            index idx,
            size_t size, size_t offset, size_t stride,
            url&& data_url, emu::capsule&& capsule
        )
            : shm_data(shm_data)
            , mapping_(&mapping)
            , prod(view_t(this, this->shm_data, idx, size, offset, stride))
            , cons(view_t(this, this->shm_data, std::move(idx), size, offset, stride))
            , data_url(std::move(data_url))
            , keep_alive(std::move(capsule))
        {}

        const sardine::interface::mapping& mapping() const { return *mapping_; }

        buffer::interface::producer& producer() override { return prod; }
        buffer::interface::consumer& consumer() override { return cons; }

        span_b bytes() override {
            return shm_data;
        }

    };

namespace detail
{

    template<typename T>
    using closed_mapper_t = decltype(std::declval< sardine::type_mapper<T> >().close_lead_dim());

    template<typename T>
        requires cpts::closable_lead_dim< sardine::type_mapper< T > >
    auto make_package(T& data, index idx, size_t offset)
        -> result<std::pair<closed_mapper_t< emu::rm_ref<T> >, package::s_buffer_package>>
    {

        using mapper_t = sardine::type_mapper< emu::rm_ref<T> >;
        using value_type = typename mapper_t::value_type;

        auto mapper = mapper_t::from(data);

        auto view = mapper_t::as_bytes(data);

        auto closed_mapper = mapper.close_lead_dim();

        offset += closed_mapper.offset();

        constexpr static size_t t_size = sizeof(typename decltype(closed_mapper)::value_type);

        auto data_url = EMU_UNWRAP(sardine::detail::url_from_bytes(view));

        auto closed_mapping = closed_mapper.mapping();
        update_url(data_url, closed_mapping);

        // copy the mapping but put the object in a capsule and use the address of the object.
        auto [capsule, mapping] = emu::make_capsule_and_keep_addr<default_mapping>(std::move(closed_mapping));

        package::s_buffer_package pkg = std::make_shared<memory_package>(
            view, *mapping, std::move(idx),
            closed_mapper.size() * sizeof(value_type),
            offset * sizeof(value_type),
            closed_mapper.lead_stride() * sizeof(value_type),
            std::move(data_url), std::move(capsule)
        );

        return std::make_pair( std::move(closed_mapper), std::move(pkg) );

    }

} // namespace detail

    template<typename T>
    auto make_view(T& data, index idx, size_t offset = 0) {
        return detail::make_package(EMU_FWD(data), std::move(idx), offset).map([&](auto pair) {
            auto [mapper, pkg] = std::move(pair);
            using data_view_t = typename decltype(mapper)::type;
            return sardine::view_t<data_view_t>(mapper, std::move(pkg));
        });
    }


    template<typename T>
    auto make_producer(T& data, index idx, size_t offset = 0) {
        return detail::make_package(EMU_FWD(data), std::move(idx), offset).map([&](auto pair) {
            auto [mapper, pkg] = std::move(pair);
            using data_view_t = typename decltype(mapper)::type;
            return sardine::producer<data_view_t>(mapper, std::move(pkg));
        });
    }

    template<typename T>
    auto make_consumer(T& data, index idx, size_t offset = 0) {
        return detail::make_package(EMU_FWD(data), std::move(idx), offset).map([&](auto pair) {
            auto [mapper, pkg] = std::move(pair);
            using data_view_t = typename decltype(mapper)::type;
            return sardine::consumer<data_view_t>(mapper, std::move(pkg));
        });
    }

} // namespace sardine::ring
