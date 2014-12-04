===============================
Canary.md Python Client Library
===============================

The `canarymd` python library offers an interface to the Canary Health
API at `canary.md`.


Project
=======

* Homepage: https://github.com/canaryhealth/canarymd-python
* Bugs: https://github.com/canaryhealth/canarymd-python/issues


TL;DR
=====

Install:

.. code-block:: bash

  $ pip install canarymd

Use:

.. code-block:: python

   import canarymd
   client = canarymd.Client(principal='{USERNAME}', credential='{PASSWORD}')
   html = client.select(
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
   ).content

   # now do something with the HTML messages!


TODO: add documentation
