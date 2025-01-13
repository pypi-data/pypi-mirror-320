#include <sardine/buffer/ring.hpp>

#include <sardine/buffer.hpp>

namespace sardine::ring
{

    index::index(box<size_t&> global_index, size_t buffer_nb, next_policy policy)
        : global_index(std::move(global_index))
        , idx(this->global_index.value)
        , buffer_nb(buffer_nb)
        , policy(policy)
    {}

    index::index(size_t& global_index, size_t buffer_nb, next_policy policy)
        : global_index(global_index)
        , idx(global_index)
        , buffer_nb(buffer_nb)
        , policy(policy)
    {}

    // result<index> open(sardine::url url, size_t buffer_nb, next_policy policy) {
    //     auto global_index = box<size_t, host_context>::open(url);
    //     if (not global_index)
    //         return unexpected(global_index.error());

    //     return index(*global_index, buffer_nb, policy);
    // }


    void index::incr_local() {
        idx = (idx + 1) % buffer_nb;
    }

    void index::decr_local() {
        idx = (idx == 0 ? buffer_nb : idx) - 1;
    }

    bool index::has_next(host_context& ctx) {
        global_index.recv(ctx);
        return global_index.value != idx;
    }

    void index::send(host_context& ctx) {
        save_index = global_index.value;
        global_index.value = idx;
        global_index.send(ctx);

        incr_local();
    }

    void index::recv(host_context& ctx) {
        // Always recv just in case.
        save_index = global_index.value;
        global_index.recv(ctx);
        if (policy == next_policy::next) { // should we check if has_next ?
            incr_local();
        } else if (policy == next_policy::last){
                idx = global_index.value;
        } else { // policy == next_policy::check_next
            if (global_index.value != idx) {
                incr_local();
            }
        }

    }

    void index::revert_send(host_context& ctx) {
        global_index.value = save_index;
        global_index.send(ctx);

        //TODO: check correctness
        decr_local();
    }

    void index::revert_recv(host_context& ctx) {
        if (policy == next_policy::next) {
            decr_local();
        } else { // policy == next_policy::last
            idx = save_index;
        }
    }

    sardine::url view_t::url_of() const {
        sardine::url url(fmt::format("{}://", url_scheme));

        {
            auto param_ref = url.params();

            param_ref.set(data_key  , pkg->data_url.c_str());
            param_ref.set(index_key , idx.url_of().c_str());
            param_ref.set(size_key  , fmt::to_string(size));
            param_ref.set(offset_key, fmt::to_string(offset));
            param_ref.set(stride_key, fmt::to_string(stride));
        }

        return url;
    }


    result< sardine::package::s_memory_package > make_package( const url_view& u, device_type_t requested_dt) {
        auto params = u.params();

        auto size = EMU_UNWRAP_OR_RETURN_UNEXPECTED(urls::try_parse_at<size_t>(params, size_key),
                                                    errc::ring_url_missing_size);

        auto offset = urls::try_parse_at<size_t>(params, offset_key).value_or(0);
        auto stride = urls::try_parse_at<size_t>(params, stride_key).value_or(std::dynamic_extent);

        auto data_url = EMU_UNWRAP_OR_RETURN_UNEXPECTED(urls::try_get_at(params, data_key).map(make<url>),
                                                        errc::ring_url_missing_data);

        auto idx_url = EMU_UNWRAP_OR_RETURN_UNEXPECTED(urls::try_get_at(params, index_key),
                                                        errc::ring_url_missing_index);

        auto pkg = EMU_UNWRAP(sardine::package::url_to_memory_package(data_url, requested_dt));

        auto bytes = pkg->bytes();
        const auto& mapping = pkg->mapping();

        auto idx = EMU_UNWRAP(index::open(url_view(idx_url)));

        return std::make_shared<memory_package>(bytes, mapping, std::move(idx), size, offset, stride, std::move(data_url), emu::capsule(std::move(pkg)));
    }

} // namespace sardine::ring

SARDINE_REGISTER_MEMORY_PACKAGE_FACTORY(
    ring_memory_package,
    sardine::ring::url_scheme,
    sardine::ring::make_package
);
