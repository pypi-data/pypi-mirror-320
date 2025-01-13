#include <sardine/region/host.hpp>
#include <sardine/package/interface.hpp>

#include <sardine/package/registry.hpp>

namespace sardine::region::host
{
    struct memory_package;

    struct producer : buffer::interface::producer
    {
        memory_package* pkg;
        span_b shm_data;

        producer(memory_package* pkg, span_b shm_data)
            : pkg(pkg), shm_data(shm_data)
        {}

        void send(host_context&) override {}
        void revert(host_context&) override {}

        span_b bytes() override { return shm_data; }
        url url_of() const override;

    };

    struct consumer : buffer::interface::consumer
    {
        memory_package* pkg;
        span_b shm_data;

        consumer(memory_package* pkg, span_b shm_data)
            : pkg(pkg), shm_data(shm_data)
        {}

        void recv(host_context&) {}
        void revert(host_context&) {}

        span_b bytes() override { return shm_data; }
        url url_of() const override;

    };

    struct memory_package : sardine::package::interface::memory_package
    {
        container_b shm_data;
        default_mapping mapping_;
        url u;

        host::producer prod;
        host::consumer cons;

        memory_package(container_b&& data, default_mapping&& mapping, url&& u)
            : shm_data(std::move(data)), mapping_(std::move(mapping)), u(std::move(u))
            , prod(this, shm_data), cons(this, shm_data)
        {}

        span_b bytes() override {
            return shm_data;
        }

        buffer::interface::producer& producer() override {
            return prod;
        }

        buffer::interface::consumer& consumer() override {
            return cons;
        }

        const sardine::interface::mapping& mapping() const override {
            return mapping_;
        }

    };

    url producer::url_of() const { return pkg->u; }
    url consumer::url_of() const { return pkg->u; }

    result<sardine::package::s_memory_package> make_package(const url_view& u, device_type_t requested_dt) {
        auto bytes = EMU_UNWRAP(bytes_from_url(u, requested_dt));
        auto mapping = EMU_UNWRAP(make_mapping(u.params()));

        // Generate a new minimal url without unexpected parameters. Maybe useless…
        if(auto url = url_from_bytes(bytes); url)
            return std::make_shared<memory_package>(std::move(bytes), std::move(mapping), EMU_UNWRAP(*std::move(url)));

        return make_unexpected(errc::host_unknow_region_kind);
    }

} // namespace sardine::region::host

SARDINE_REGISTER_MEMORY_PACKAGE_FACTORY(
    sardine_region_host_package,
    sardine::region::host::url_scheme,
    sardine::region::host::make_package
);
