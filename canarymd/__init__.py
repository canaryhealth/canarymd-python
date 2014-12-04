# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <phil@canary.md>
# date: 2014/12/03
# copy: (C) Copyright 2014-EOT Canary Health, Inc., All Rights Reserved.
#------------------------------------------------------------------------------

'''
This is the Python client library for the Canary Health API.  The
following on-line resources are available if you need further
information than what is available in the pydocs:

* Homepage: https://github.com/canaryhealth/canarymd-python
* Bugs: https://github.com/canaryhealth/canarymd-python/issues

Typical Usage
-------------

.. code-block:: python

   import canarymd
   client = canarymd.Client(principal='{USERNAME}', credential='{PASSWORD}')
   selection = client.select(
     context   = '{CONTEXT}',
     peo       = {
       'transport'   : canarymd.Transport.SITE,
       'purpose'     : canarymd.Purpose.PREPARE,
       'recipient'   : recipient.toHL7(),
       'appointment' : {
         'time'        : '2014-12-02T18:20:06Z',
         'patients'    : [patient.toHL7() for patient in patients],
         'provider'    : provider.toHL7(),
         'type'        : 'new',
         'reason'      : 'us/namcs:5035.0',
         'policy'      : policy.toHL7(),
       },
     },
   )

   # now do something with the HTML message in `selection.content`!...

'''

#------------------------------------------------------------------------------

from .client import *

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
