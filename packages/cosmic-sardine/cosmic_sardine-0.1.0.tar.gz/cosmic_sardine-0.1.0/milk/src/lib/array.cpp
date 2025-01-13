#include <sardine/milk/error.hpp>
#include <sardine/milk/array.hpp>

#include <sardine/url.hpp>

namespace sardine::milk
{

    constexpr auto non_blocking_key = "nblk";

    void remove_array(cstring_view name) {
        array::remove(name);
    }

    ArrayBase::ArrayBase(s_image_t&& h, bool blocking)
        : handle_(std::move(h))
        , data_(handle_->base_buffer())
        , local_index(handle().index())
        , sem_index(handle().lock_sem_index())
        , blocking(blocking)
    {}

    ArrayBase::ArrayBase(const ArrayBase & array)
        : handle_(array.handle_)
        , data_(array.data_)
        , local_index(array.local_index)
        // The created ArrayBase share the handle but get an unique semaphore index
        , sem_index(handle().lock_sem_index())
        , blocking(array.blocking)
    {}

    ArrayBase& ArrayBase::operator=(const ArrayBase & array)
    {
        handle_ = array.handle_;
        data_ = array.data_;
        local_index = array.local_index;
        // The created ArrayBase share the handle but get an unique semaphore index
        sem_index = handle().lock_sem_index();
        blocking = array.blocking;

        return *this;
    }

    result<ArrayBase> ArrayBase::convert_to(emu::dlpack::device_type_t requested_dt) const {
        EMU_THROW_ERROR_LOG(emu::errc::not_implemented, "milk array memory converter not implemented");
    }


    auto ArrayBase::handle() -> image_t& {
        return *handle_;
    }

    auto ArrayBase::handle() const -> const image_t& {
        return *handle_;
    }

    void ArrayBase::recv() {
        if (blocking)
            local_index = handle().wait_on(sem_index.value);
        else
            local_index = handle().index();
    }

    void ArrayBase::send() {
        handle().set_index_and_notify(local_index);
        next();
    }

    bool ArrayBase::available() const {
        return handle().available(sem_index.value);
    }

    void ArrayBase::next() {
        local_index = handle().next_index();
    }

    uint64_t ArrayBase::index() const {
        return local_index;
    }

    uint64_t ArrayBase::next_index() const {
        return handle().next_index();
    }

    void ArrayBase::set_index(uint64_t index) {
        local_index = index;
    }

    size_t ArrayBase::buffer_nb() const {
        return handle().buffer_nb();
    }


    size_t ArrayBase::rank() const {
        return handle().rank();
    }

    size_t ArrayBase::size() const {
        return handle().size();
    }

    size_t ArrayBase::size_byte() const {
        return size() * item_size();
    }

    span<const size_t> ArrayBase::extents() const {
        return handle().extents();
    }

    span_b ArrayBase::base_bytes() const {
        return data_;
    }

    span_b ArrayBase::bytes() const {
        return base_bytes().subspan( local_index * size_byte(), size_byte());
    }

    int ArrayBase::location() const {
        return handle().location();
    }

    dtype_t ArrayBase::dtype() const {
        return handle().dtype();
    }

    size_t ArrayBase::item_size() const {
        return handle().item_size();
    }

    cstring_view ArrayBase::name() const {
        return handle().name();
    }

    url ArrayBase::url_of() const {
        auto url = handle().url_of();

        // blocking is the default, so we only need to add the parameter if it is non-blocking
        if (not blocking) url.params().append({non_blocking_key, nullptr});

        return url;
    }

    sardine::url ArrayBase::url_of_current() const {
        return handle().url_of_at(local_index);
    }


    ArrayBase from_url(url_view u) {
        bool blocking = not u.params().contains(non_blocking_key);

        return {array::image_t::from_url(u), blocking};
    }

    ArrayBase open(string name, bool blocking) {
        return {array::image_t::open(name), blocking};
    }

    ArrayBase create(string name, span<const size_t> shape, size_t buffer_nb, dtype_t dtype, int location, bool blocking) {
        return {array::image_t::create(name, shape, buffer_nb, dtype, location), blocking};
    }

    ArrayBase open_or_create(string name, span<const size_t> shape, size_t buffer_nb, dtype_t dtype, int location, bool blocking) {
        auto img = array::image_t::open_or_create(name, shape, buffer_nb, dtype, location);
        auto base_data = img->base_buffer();

        // If location is different from the requested location, we need to try convert the data.
        EMU_TRUE_OR_THROW_LOG(location == img->location(), errc::array_open_location_mismatch,
            "Location mismatch: expected {}, got {}", location, img->location());

        return {std::move(img), blocking};
    }

namespace host
{

    ArrayBase open(string name, bool blocking) {
        return sardine::milk::open(name, blocking);
    }

    ArrayBase create(string name, span<const size_t> shape, size_t buffer_nb, dtype_t dtype, bool blocking) {
        return sardine::milk::create(name, shape, buffer_nb, dtype, -1, blocking);
    }

    ArrayBase open_or_create(string name, span<const size_t> shape, size_t buffer_nb, dtype_t dtype, bool blocking) {
        return sardine::milk::open_or_create(name, shape, buffer_nb, dtype, -1, blocking);
    }

} // namespace host

namespace cuda
{

    ArrayBase open(string name, bool blocking) {
        return sardine::milk::open(name, blocking);
    }

    ArrayBase create(string name, span<const size_t> shape, size_t buffer_nb, dtype_t dtype, int location, bool blocking) {
        return sardine::milk::create(name, shape, buffer_nb, dtype, location, blocking);
    }

    ArrayBase open_or_create(string name, span<const size_t> shape, size_t buffer_nb, dtype_t dtype, int location, bool blocking) {
        return sardine::milk::open_or_create(name, shape, buffer_nb, dtype, location, blocking);
    }

} // namespace cuda

} // namespace sardine::milk
