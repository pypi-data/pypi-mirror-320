#include <sardine/factory_register.hpp>
#include <sardine/buffer/impl.hpp>

#include <sardine/milk/array.hpp>

namespace sardine::milk
{

    template<typename Ctx>
    struct view_t
    {
        ArrayBase array;

        span_b bytes() {
            return array.bytes();
        }

        url_view url_of() const { return array.url_of(); }
    };

    template<typename Ctx>
    struct producer : view_t
    {

        using view_t::view_t;

        uint64_t last_index;

        producer(view_t view)
            : view_t(std::move(view))
        {
            // producer always set index to the next buffer.
            array.next();
            last_index = array.current_index(); // avoid weird behavior if revert is called before send.
        }

        void send(Ctx&) {
            last_index = array.current_index();

            array.send(); // notify and increment the local index.
        }

        void revert(Ctx&) {
            array.set_index(last_index);
        }

    };

    template<typename Ctx>
    struct consumer : view_t
    {

        using view_t::view_t;

        uint64_t last_index;

        consumer(view_t view)
            : view_t(std::move(view))
            , last_index(array.current_index()) // avoid weird behavior if revert is called before recv.
        {}

        void recv(Ctx&) {
            last_index = array.current_index();

            array.recv();
        }

        void revert(Ctx&) {
            array.set_index(last_index);
        }

    };

    template<typename Ctx>
    struct factory : buffer::interface::factory<Ctx>
    {
        ArrayBase array;
        default_mapping_descriptor mapping_descriptor_;

        factory(ArrayBase&& array, default_mapping_descriptor&& mapping)
            : array(std::move(array))
            , mapping(std::move(mapping))
        {}

        const sardine::interface::mapping& mapping() const {
            return mapping_descriptor_;
        }

        result<buffer::s_producer<Ctx>> create_producer() override {
            return buffer::make_s_producer<Ctx>(array_producer_consumer<Ctx>{std::move(array)});
        }

        result<buffer::s_consumer<Ctx>> create_consumer() override {
            return buffer::make_s_consumer<Ctx>(array_producer_consumer<Ctx>{std::move(array)});
        }

        static result<buffer::s_factory<Ctx>> create(url_view u, emu::dlpack::device_type_t requested_dt) {
            auto array = open(u, requested_dt);


            return buffer::make_s_factory<Ctx>(milk_factory<Ctx>{std::move(array), default_mapping_descriptor{}});
        }
    };

} // namespace sardine::milk
