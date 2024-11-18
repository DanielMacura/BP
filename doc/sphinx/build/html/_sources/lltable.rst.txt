LL Table
===========

This module constructs a LL(1) table from a provided LL(1) grammar. 

To begin, the FIRST sets are computed by :py:meth:`ComputeFirstSets`, following that FOLLOW sets are computed by :py:meth:`ComputeFollowSets`.

.. autoclass:: lltable.LLTable
   :members:
