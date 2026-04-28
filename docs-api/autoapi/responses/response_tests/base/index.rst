responses.response_tests.base
=============================

.. py:module:: responses.response_tests.base


Classes
-------

.. autoapisummary::

   responses.response_tests.base.TestKind
   responses.response_tests.base.ResponseTest


Module Contents
---------------

.. py:class:: TestKind(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Create a collection of name/value pairs.

   Example enumeration:

   >>> class Color(Enum):
   ...     RED = 1
   ...     BLUE = 2
   ...     GREEN = 3

   Access them by:

   - attribute access:

     >>> Color.RED
     <Color.RED: 1>

   - value lookup:

     >>> Color(1)
     <Color.RED: 1>

   - name lookup:

     >>> Color['RED']
     <Color.RED: 1>

   Enumerations can be iterated over, and know how many members they have:

   >>> len(Color)
   3

   >>> list(Color)
   [<Color.RED: 1>, <Color.BLUE: 2>, <Color.GREEN: 3>]

   Methods can be added to enumerations, and members can have their own
   attributes -- see the documentation for details.


   .. py:attribute:: PARAMETRIC


   .. py:attribute:: SURROGATE


.. py:class:: ResponseTest

   Bases: :py:obj:`abc.ABC`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: kind
      :type:  TestKind


   .. py:method:: compute_pvalues(data: response_generator.responses.config.ResponseData) -> numpy.ndarray
      :abstractmethod:



