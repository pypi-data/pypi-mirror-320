
Installation
============

This assumes you already have a :doc:`WuttJamaican app
<wuttjamaican:narr/install/index>` setup and working.

Install the Wutta-COREPOS package to your virtual environment:

.. code-block:: sh

   pip install Wutta-COREPOS

Edit your :term:`config file` to add CORE-POS DB connection info, and
related settings.  Note that so far, only CORE Office DB connections
are supported.

.. code-block:: ini

   [corepos]
   office.url = http://localhost/fannie/

   [corepos.db.office_op]
   default.url = mysql+mysqlconnector://localhost/core_op

   [corepos.db.office_trans]
   default.url = mysql+mysqlconnector://localhost/core_trans

   [corepos.db.office_arch]
   default.url = mysql+mysqlconnector://localhost/trans_archive

And that's it, the CORE-POS integration is configured.
