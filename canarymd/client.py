# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <phil@canary.md>
# date: 2014/12/03
# copy: (C) Copyright 2014-EOT Canary Health, Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import logging
import requests
from aadict import aadict
import morph
import json
import asset

#------------------------------------------------------------------------------

log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class Error(Exception): pass
class AuthorizationError(Error): pass
class ProtocolError(Error): pass

#------------------------------------------------------------------------------
class Purpose:
  DISCOVER        = 'discover'
  PREPARE         = 'prepare'
  AUGMENT         = 'augment'
  EXTEND          = 'extend'
  ALL             = (DISCOVER, PREPARE, AUGMENT, EXTEND)

#------------------------------------------------------------------------------
class Transport:
  SITE            = 'site'
  EMAIL           = 'email'
  PAPER           = 'paper'
  SMS             = 'sms'
  VOICE           = 'voice'
  ALL             = (SITE, EMAIL, PAPER, SMS, VOICE)

#------------------------------------------------------------------------------
class Environment:
  DEV             =  'dev'
  TEST            =  'test'
  CI              =  'ci'
  QA              =  'qa'
  UAT             =  'uat'
  PPE             =  'ppe'
  STG             =  'stg'
  PROD            =  'prod'
  ALL             = (DEV, TEST, CI, QA, UAT, PPE, STG, PROD)

#------------------------------------------------------------------------------
class Client(object):

  # todo: add

  #----------------------------------------------------------------------------
  def __init__(self, principal, credential, env=Environment.PROD, root=None):
    '''
    Constructs a new `canarymd.Client` object that is used to
    communicate with the Canary API. The following parameterns
    are accepted:

    :Parameters:

    principal : str

      The principal (i.e. username) to authenticate with to the Canary
      servers.

    credential : str

      The `principal` 's credential/token (i.e. password) to use to
      authenticate with the Canary servers.

    env : str, optional, default: canarymd.Environment.PROD

      The Canary environment to connect to -- defaults to the
      production servers. For testing, the staging environment
      should be used, i.e. ``canarymd.Environment.STG``.

    '''
    if env not in Environment.ALL:
      raise ValueError('invalid/unknown environment: %r' % (env,))
    self.cookies    = {}
    self.principal  = principal
    self.credential = credential
    self.env        = env
    self.root       = root or {
      Environment.PROD : 'https://api.canary.md/api',
      Environment.DEV  : 'http://api-dev.canary.md:8899/api',
    }.get(env,           'https://api-{env}.canary.md/api').format(env=env)
    self.session    = requests.Session()
    self.session.headers['content-type'] = 'application/json'
    self._version   = aadict(client=asset.version('canarymd'))
    self._checkVersion()

  #----------------------------------------------------------------------------
  def _checkVersion(self):
    res = self.session.get(self.root + '/version').json()
    if 'apis' not in res:
      sapi = res.get('api', 'UNKNOWN')
      if sapi == '1.1.0':
        self._version.update(api='v1', server=res.get('server'))
        return
      raise ProtocolError(
        'incompatible client/server versions (1.1.0 != %s)' % (sapi,))
    sapi = res.get('apis', [])
    for version in ('v2',):
      if version in sapi:
        self._version.update(api=version, server=res.get('server'))
        self.root += '/' + version
        return
    raise ProtocolError(
      'incompatible client/server versions ("v2" not in %r)' % (sapi,))

  #----------------------------------------------------------------------------
  def _apiError(self, res):
    ret = str(res.status_code) + ': '
    # todo: handle case where `res.content_type` is not application/json...
    res = res.json()
    ret += res['message']
    if 'field' in res:
      ret += ' (' + ', '.join([
          key + ': ' + value
          for key, value in morph.flatten(res['field']).items()]) + ')'
    return ret

  #----------------------------------------------------------------------------
  def _req(self, method, url, data=None, *args, **kw):
    log.debug('sending %r request to %r', method, url)
    if data is not None:
      data = json.dumps(data)
    res = getattr(self.session, method)(self.root + url, data=data, *args, **kw)
    if res.status_code != 401:
      return res
    res = self.session.post(self.root + '/auth/session', json.dumps({
      'username' : self.principal,
      'password' : self.credential,
    }))
    if res.status_code != 200:
      err = self._apiError(res)
      log.error('authentication failure: %s', err)
      raise AuthorizationError(err)
    res = getattr(self.session, method)(self.root + url, data=data, *args, **kw)
    if res.status_code != 401 and res.status_code != 403:
      return res
    err = self._apiError(res)
    log.error('post-authentication authorization failure: %s', err)
    raise AuthorizationError(err)

  #----------------------------------------------------------------------------
  def version(self):
    return self._version

  #----------------------------------------------------------------------------
  def select(self, context, peo, timeout=None):
    '''
    Request a message selection. If no applicable messages are found,
    then this returns ``None``, otherwise a
    :class:`canarymd.Selection` object is returned.

    :Parameters:

    context : str, required

      The Canary context under which to make this messaging request.

    peo : dict, required

      The Patient Engagement Opportunity (PEO) description. See the
      Canary documentation for a detailed description of all possible
      attributes. Among the common ones are:

      transport : str, required

        How the PEO is being delivered to the `recipient`. Must be one
        of the transports defined in `canarymd.Transport`. For the
        ``paper`` transport, `width` and `height` are required.

      purpose : str, required

        What the relative purpose of the PEO is to the patient
        circumstance.Must be one of the transports defined in
        `canarymd.Purpose`.

      width : int, default: null

        Indicative width of the available space in pixels.

        *Indicative* means that Canary will attempt to fill the space
        completely, but may go over or under by some amount.

        For ``paper`` transports, the physical dimensions should be
        converted to pixels using a 300 DPI resolution.

      height : int, default: null

        Indicative height of the available space in pixels. See
        `width` for details.

      recipient : { dict, str }, required

        The recipient of this PEO; either as a dictionary of
        attributes or in HL7 serialized form.

      appointment : { dict, str }, optional, default: null

        If this PEO is for an appointment, the details of the
        appointment; either as a dictionary of attributes or in HL7
        serialized form.

    '''
    if peo.get('transport') not in Transport.ALL:
      raise ValueError('invalid/unknown transport: %r' % (peo.get('transport'),))
    if peo.get('purpose') not in Purpose.ALL:
      raise ValueError('invalid/unknown purpose: %r' % (peo.get('purpose'),))
    # todo: do a full parameter check?...
    params = {
      'selection' : {
        'context'   : context,
        'peo'       : peo,
      },
    }
    if timeout is not None:
      params['timeout'] = timeout
    res = self._req('post', '/selection', params)
    if res.status_code != 200:
      err = self._apiError(res)
      log.error('selection failure: %s', err)
      raise ProtocolError(err)
    jdat = res.json()
    if 'selection' not in jdat:
      log.error(
        'unexpected error: no `selection` attribute in selection response: %r',
        res.text)
      raise ProtocolError(
        'unexpected error: no `selection` attribute in selection response')
    if jdat['selection'] is None:
      return None
    return Selection(jdat)

#------------------------------------------------------------------------------
class Selection(object):
  '''
  The result of a message selection operation.

  :Attributes:

  id : UUID

    The unique identifier for this selection.

  content : str

    The transport-specific rendered form of the messages. For example,
    for SITE and EMAIL, this will be in HTML format, and for SMS this
    will be in plain-text format.

  items : list

    An itemized list of the messages contained in `content`. (Useful
    for forensic purposes.)
  '''

  #----------------------------------------------------------------------------
  def __init__(self, data):
    self._data   = aadict.d2ar(data)
    self.id      = self._data.selection.id
    self.items   = self._data.selectionitems
    self.content = self._data.content

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
