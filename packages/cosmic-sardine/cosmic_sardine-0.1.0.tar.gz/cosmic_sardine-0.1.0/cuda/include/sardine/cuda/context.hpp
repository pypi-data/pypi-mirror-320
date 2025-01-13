#pragma once

#include <sardine/context.hpp>

#include <cuda/api.hpp>

#include <memory>

namespace sardine::cuda
{

    // cuda_context derive from host_context. That mean that we can provide a cuda_context to a host function
    // it will work as long as we don't try to access data that was updated along the cuda_context
    // In this case, we need to synchronize the stream before calling the host_context function.
    struct cuda_context : host_context {
        std::shared_ptr<cuda::stream_t> stream_;

        cuda_context(cuda::device_t device)
            : stream_{std::make_shared<cuda::stream_t>(cuda::stream::create(device, false))}
        {}

        cuda_context(cuda::stream_t stream)
            : stream_{std::make_shared<cuda::stream_t>(std::move(stream))}
        {}

        cuda::stream_t& stream() const {
            return *stream_;
        }

        cuda::device_t device() const {
            return stream_->device();
        }
    };

} // namespace sardine::cuda
