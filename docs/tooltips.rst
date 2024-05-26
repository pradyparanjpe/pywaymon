.. _tooltips:

#########
Tooltips
#########

Modules provided by *pywaymon* have evolved to display computer-monitoring tooltips.

******************
Tooltip structure
******************

Tooltips may be composed of following parts.

Title
===============
A highlighted title for the tooltip.

Plain Text
=================
Some free flowing unstructured plain text.

.. _TABLE:

Table
=================
A structured table.
The table has following components.

row_names
-------------
Names for table-rows.

col_names
-------------
Names for table-cols.

table
-------------
Table cells.

.. _COMBINE:

************
Combination
************
Two types of tooltips can be combined (**A** + **B**).
Order does matter as is described below.

Title
========
When combined, title of **A**, if available, else, title of **B** becomes title of the combined tooltip.

Plain Text
===============
Plain text of **A** and plain text of **B**, with a new-line added in between.

Table
=======
Tables are suitably padded and combined horizontally.
The table-separator defaults to ``│`` if not :ref:`configured<SEPCONF>`.
Respective row_names and col_names are desplayed.
