#pragma once

#include <sardine/buffer/interface.hpp>
#include <sardine/url.hpp>

namespace sardine::buffer::native
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

        native::producer prod;
        native::consumer cons;

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

    inline url producer::url_of() const { return pkg->u; }
    inline url consumer::url_of() const { return pkg->u; }

    inline sardine::package::s_memory_package make_package(container_b data, default_mapping&& mapping, url&& u) {
        return std::make_shared<memory_package>(std::move(data), std::move(mapping), std::move(u));

    }

    template<typename T>
    result<sardine::package::s_memory_package> make_package(T && value) {
        using mapper_t = sardine::type_mapper< emu::rm_ref<T> >;

        auto type_mapper = mapper_t::from(value);

        auto data = type_mapper.as_bytes(value);
        auto mapping = type_mapper.mapping();
        auto url = EMU_UNWRAP(sardine::detail::url_from_bytes(data));

        return make_package(data, std::move(mapping), std::move(url));
    }

} // namespace sardine::buffer::native
