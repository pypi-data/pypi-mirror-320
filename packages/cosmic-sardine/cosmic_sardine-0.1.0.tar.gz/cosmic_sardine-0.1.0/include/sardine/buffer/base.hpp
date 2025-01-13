#pragma once

#include <sardine/type.hpp>
#include <sardine/context.hpp>
#include <sardine/mapper.hpp>
#include <sardine/mapper/proxy.hpp>
#include <sardine/buffer/utility.hpp>
#include <sardine/buffer/interface.hpp>
#include <sardine/package/interface.hpp>
#include <sardine/buffer/native.hpp>

#include <emu/concepts.hpp>

namespace sardine
{

    template<typename T>
    struct box : mapper::proxy< T, box< T > >, buffer::storage<T>
    {
        static_assert(not emu::is_ptr<T>, "T must not be a pointer");
        static_assert(not emu::is_const<T>, "T must not be const");

        using base_t = mapper::proxy< T, box >;
        using storage_base = buffer::storage<T>;

        using mapper_t = base_t::mapper_t;
        using base_t::mapper;

        package::s_buffer_package pkg;
        buffer::interface::producer* prod;
        buffer::interface::consumer* cons;

        box( mapper_t t_mapper, package::s_buffer_package&& pkg )
            : base_t(std::move(t_mapper))
            , storage_base(this->convert(pkg->consumer().bytes()))
            , pkg(std::move(pkg))
            , prod(&this->pkg->producer())
            , cons(&this->pkg->consumer())
        {}

        box(T view)
            : box(mapper_t::from(view), *buffer::native::make_package(view))
        {}



        void send(host_context& ctx) {
            // TODO: move the copy out of the accessor and add the Ctx as a parameter.
            buffer::copy(this->value, this->convert(prod->bytes()), ctx);
            prod->send(ctx);
        }
        void recv(host_context& ctx) {
            cons->recv(ctx);
            // this is bad… maybe let the package do the copy?
            //
            buffer::copy(this->convert(cons->bytes()), this->value, ctx);
        }

        void revert(host_context& ctx) {
            prod->revert(ctx);
            cons->revert(ctx);
        }

        sardine::url url_of() const {
            auto u = cons->url_of();
            update_url(u, mapper());
            return u;
        }

        template<typename NT>
        auto clone_with_new_mapper(sardine::type_mapper<NT> new_accessor) const -> box<NT> {
            return box<NT>( new_accessor, prod, cons );
        }

        // static auto load(url_view u/* , map_t parameter = map_t() */) -> result<box>;
        static auto open(const url_view& u) -> result<box>;
    };

    template<typename T>
    struct view_t : mapper::proxy < T, view_t <T> >
    {
        using base_t = mapper::proxy< T, view_t >;
        using mapper_t = base_t::mapper_t;
        using base_t::mapper;

        package::s_buffer_package pkg;
        buffer::interface::view_t* view_;

        view_t(base_t::mapper_t t_mapper, package::s_buffer_package&& pkg)
            : base_t(std::move(t_mapper))
            , pkg(std::move(pkg))
            , view_(&this->pkg->consumer()) // cast consumer into view_t.
        {}

        view_t(T view) : view_t(mapper_t::from(view), *buffer::native::make_package(view))
        {}

        auto view() const -> T {
            return this->convert(view_->bytes());
        }

        sardine::url url_of() const {
            auto url = view_->url_of();
            update_url(url, mapper());
            return url;
        }

        template<typename NT>
        auto clone_with_new_mapper(sardine::type_mapper<NT> new_accessor) const -> view_t<NT> {
            return view_t<NT>( new_accessor, package::s_buffer_package(pkg) );
        }

    };

    template <typename T>
    struct producer : mapper::proxy< T, producer< T > >
    {
        using base_t = mapper::proxy< T, producer >;
        using mapper_t = base_t::mapper_t;
        using base_t::mapper;

        package::s_buffer_package pkg;
        buffer::interface::producer* prod;

        producer(base_t::mapper_t t_mapper, package::s_buffer_package&& pkg)
            : base_t(std::move(t_mapper))
            , pkg(std::move(pkg))
            , prod(&this->pkg->producer())
        {}

        producer(T view) : producer(mapper_t::from(view), *buffer::native::make_package(view))
        {}

        auto view() const -> T {
            return this->convert(prod->bytes());
        }

        void send(host_context& ctx) { prod->send(ctx); }
        void revert(host_context& ctx) { prod->revert(ctx); }

        sardine::url url_of() const {
            auto url = prod->url_of();
            update_url(url, mapper());
            return url;
        }

        template<typename NT>
        auto clone_with_new_mapper(sardine::type_mapper<NT> new_accessor) const -> producer<NT> {
            return producer<NT>( new_accessor, package::s_buffer_package(pkg) );
        }

        static auto open(const url_view& u) -> result<producer>;
    };

    template <typename T>
    struct consumer : mapper::proxy< T, consumer< T > >
    {
        using base_t = mapper::proxy< T, consumer >;
        using mapper_t = base_t::mapper_t;
        using base_t::mapper;

        package::s_buffer_package pkg;
        buffer::interface::consumer* cons;

        consumer(base_t::mapper_t t_mapper, package::s_buffer_package&& pkg)
            : base_t(std::move(t_mapper))
            , pkg(std::move(pkg))
            , cons(&this->pkg->consumer())
        {}

        consumer(T view) : consumer(mapper_t::from(view), buffer::native::make_package(view))
        {}

        auto view() const -> T {
            return this->convert(cons->bytes());
        }

        void recv(host_context& ctx) { cons->recv(ctx); }
        void revert(host_context& ctx) { cons->revert(ctx); }

        sardine::url url_of() const {
            auto url = cons->url_of();
            update_url(url, mapper());
            return url;
        }

        template<typename NT>
        auto clone_with_new_mapper(sardine::type_mapper<NT> new_accessor) const -> consumer<NT> {
            return consumer<NT>( new_accessor, package::s_buffer_package(pkg) );
        }

        static auto open(const url_view& u) -> result<consumer>;

    };

} // namespace sardine
