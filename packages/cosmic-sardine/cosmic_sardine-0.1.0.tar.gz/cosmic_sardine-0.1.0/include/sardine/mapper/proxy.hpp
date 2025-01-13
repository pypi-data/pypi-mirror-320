#pragma once

#include <sardine/concepts.hpp>
#include <sardine/mapper/base.hpp>

namespace sardine::mapper
{

    /**
     * A proxy interacts easily with mapper. It provides a common interface to select a sub region of a buffer.
     *
     * It requires some CRTP boilerplate to work properly.
     *
     * For instance, Using a class that inherits from proxy<span<int>, Derived> will provide the following methods:
     * - close_lead_dim() // The type returned will be another specialization of Derived but will now inherit from proxy<int, Derived>.
     * - subspan(std::size_t new_offset, std::size_t new_size = std::dynamic_extent)
     *
     */

    /**
     * @brief
     *
     * @tparam T
     * @tparam Derived
     */
    template <typename T, typename Derived>
    struct proxy : sardine::type_mapper<T>
    {
        using mapper_t = sardine::type_mapper<T>;

        proxy(const mapper_t & a) : mapper_t(a) {}
        proxy(const proxy &) = default;

        sardine::type_mapper<T>       & mapper()       { return *this; }
        sardine::type_mapper<T> const & mapper() const { return *this; }

    private:
        const Derived& self() const { return *static_cast<const Derived *>(this); }
    };

    template <mapper_cpts::contiguous V, typename Derived>
    struct proxy< V, Derived > : sardine::type_mapper< V >
    {
        using mapper_t = sardine::type_mapper< V >;

        using element_type = typename mapper_t::element_type;

        proxy(const mapper_t & a) : mapper_t(a) {}
        proxy(const proxy &) = default;

        mapper_t       & mapper()       { return *this; }
        mapper_t const & mapper() const { return *this; }

        auto close_lead_dim() const
        {
            using new_mapper_t = sardine::type_mapper<element_type>;

            // using new_type = proxy<element_type, Derived>;
            return self().clone_with_new_mapper(new_mapper_t(this->offset()));
        }

        auto subspan(size_t new_offset, size_t new_size = dynamic_extent) const {
            // mapper is unaware of the element type, so we need to multiply by the size of the element
            return self().clone_with_new_mapper(mapper_t::subspan(
                new_offset,
                new_size
            ));
        }

    private:
        const Derived &self() const { return *static_cast<const Derived *>(this); }
    };

    template <mapper_cpts::mapped V, typename Derived>
    struct proxy< V, Derived > : sardine::type_mapper< V >
    {
        using mapper_t = sardine::type_mapper< V >;

        using element_type = typename V::element_type;

        proxy(const mapper_t & a) : mapper_t(a) {}
        proxy(const proxy &) = default;

        mapper_t       & mapper()       { return *this; }
        mapper_t const & mapper() const { return *this; }

        template<typename = void> // lazy compilation to avoid recursive type instantiation. TODO: check if this is necessary
        auto close_lead_dim() const requires (V::rank() > 0) {
            return submdspan(0);
        }

        template<class... SliceSpecifiers>
        auto submdspan(SliceSpecifiers... specs) const {
            return self().clone_with_new_mapper(mapper_t::submdspan(specs...));
        }

    private:
        const Derived &self() const { return *static_cast<const Derived *>(this); }
    };

} // namespace sardine::mapper
