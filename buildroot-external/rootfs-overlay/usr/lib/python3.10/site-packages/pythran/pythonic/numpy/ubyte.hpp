#ifndef PYTHONIC_NUMPY_UBYTE_HPP
#define PYTHONIC_NUMPY_UBYTE_HPP

#include "pythonic/include/numpy/ubyte.hpp"

#include "pythonic/utils/functor.hpp"
#include "pythonic/utils/meta.hpp"
#include "pythonic/utils/numpy_traits.hpp"
#include "pythonic/types/numpy_op_helper.hpp"

PYTHONIC_NS_BEGIN

namespace numpy
{

  namespace details
  {

    unsigned char ubyte()
    {
      return {};
    }

    template <class V>
    unsigned char ubyte(V v)
    {
      return v;
    }
  }

#define NUMPY_NARY_FUNC_NAME ubyte
#define NUMPY_NARY_FUNC_SYM details::ubyte
#include "pythonic/types/numpy_nary_expr.hpp"
}
PYTHONIC_NS_END

#endif
