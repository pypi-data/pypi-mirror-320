#pragma once

#include <sardine/type.hpp>
#include <sardine/type/url.hpp>
#include <sardine/mapping.hpp>

#include <sardine/context.hpp>

#include <memory>

namespace sardine::buffer
{

namespace interface
{

    struct view_t
    {
        virtual ~view_t() = default;

        virtual span_b bytes() = 0;
        virtual url url_of() const = 0;
    };

    struct producer : view_t
    {
        virtual ~producer() = default;

        virtual void   send(host_context&) = 0;
        virtual void   revert(host_context&) = 0;
    };

    struct consumer : view_t
    {
        virtual ~consumer() = default;

        virtual void   recv(host_context&) = 0;
        virtual void   revert(host_context&) = 0;
    };

} // namespace interface

// namespace view
// {

//     struct view_t
//     {
//         interface::view_t* impl;

//         span_b bytes() { return impl->bytes(); }
//         url url_of() const { return impl->url_of(); }
//     };

//     struct producer
//     {
//         interface::producer* impl;

//         void send(host_context& ctx) { impl->send(ctx); }
//         void revert(host_context& ctx) { impl->revert(ctx); }

//         span_b bytes() { return impl->bytes(); }
//         url url_of() const { return impl->url_of(); }
//     };

//     struct consumer
//     {
//         interface::consumer* impl;

//         void recv(host_context& ctx) { impl->recv(ctx); }
//         void revert(host_context& ctx) { impl->revert(ctx); }

//         span_b bytes() { return impl->bytes(); }
//         url url_of() const { return impl->url_of(); }
//     };

// } // namespace view

} // namespace sardine::buffer
