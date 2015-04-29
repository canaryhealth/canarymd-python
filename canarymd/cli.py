# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <phil@canary.md>
# date: 2014/12/03
# copy: (C) Copyright 2014-EOT Canary Health, Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import argparse
import sys
import logging
import os
import json

from . import client
from .i18n import _

#------------------------------------------------------------------------------

log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def main(args=None):

  logging.basicConfig()

  # todo: put a pointer to the website in the description...

  cli = argparse.ArgumentParser(
    # usage='%(prog)s [options] [FILENAME | "-"]',
    # description='Requests a selection from Canary',
    # epilog='%(prog)s ' + lib.version,
  )

  cli.add_argument(
    _('-v'), _('--verbose'),
    dest='verbose', action='count', default=0,
    help=_('increase verbosity (can be specified multiple times)'))

  # todo: make this required
  cli.add_argument(
    _('-u'), _('--username'), metavar=_('PRINCIPAL'),
    dest='username', default=os.environ.get('CANARYMD_USERNAME', None),
    help=_('the principal (i.e. username) to authenticate as'))

  # todo: make this required
  cli.add_argument(
    _('-p'), _('--password'), metavar=_('CREDENTIAL'),
    dest='password', default=os.environ.get('CANARYMD_PASSWORD', None),
    help=_('the principal\'s credential/token (i.e. password)'))

  cli.add_argument(
    _('-e'), _('--env'), metavar=_('ENVIRONMENT'),
    dest='env', default=os.environ.get('CANARYMD_ENV', client.Environment.PROD),
    help=_('the principal\'s credential/token (i.e. password)'))

  # todo: make this required
  cli.add_argument(
    _('-c'), _('--context'), metavar=_('CONTEXT'),
    dest='context', default=os.environ.get('CANARYMD_CONTEXT', None),
    help=_('the partner context under which to make the selection'))

  # todo: make this required?
  cli.add_argument(
    _('--purpose'), metavar=_('PURPOSE'),
    dest='purpose', default=client.Purpose.DISCOVER,
    help=_('the selection\'s purpose'))

  # todo: make this required?
  cli.add_argument(
    _('--transport'), metavar=_('TRANSPORT'),
    dest='transport', default=client.Transport.SITE,
    help=_('the selection\'s transport'))

  cli.add_argument(
    _('-t'), _('--timeout'), metavar=_('SECONDS'),
    dest='timeout', default=None, type=float,
    help=_('the maximum number of seconds (supports decimals) to wait'
           ' for a response'))

  #----------------------------------------------------------------------------
  # todo: move to sub-parser style options...

  cli.add_argument(
    'command', metavar=_('COMMAND'),
    help=_('the canarymd command; must be one of: "select" or "version"'))

  cli.add_argument(
    'datafile', metavar=_('FILENAME'),
    nargs='?', default=None,
    help=_('the data file, in JSON format, containing the PEO details'))

  # /todo
  #----------------------------------------------------------------------------

  options = cli.parse_args(args)

  if options.command not in ('select', 'version'):
    cli.error('unsupported/unknown command: %r' % (options.command,))

  if options.verbose > 2:
    logging.getLogger().setLevel(1)
  elif options.verbose == 2:
    logging.getLogger().setLevel(logging.DEBUG)
  elif options.verbose == 1:
    logging.getLogger().setLevel(logging.INFO)
  else:
    logging.getLogger().setLevel(logging.CRITICAL)

  # todo: move this into a sub-command...

  peo = dict(purpose=options.purpose, transport=options.transport)

  if options.datafile:
    try:
      with open(options.datafile, 'rb') as fp:
        data = json.loads(fp.read())
        peo.update(data)
    except Exception as err:
      print >> sys.stderr, \
        '[**] ERROR: could not open and/or parse data file: %r' \
        % (options.datafile,)
      print >> sys.stderr, '[**]      : %s' % (err)
      return 10

  try:

    cli = client.Client(
      principal   = options.username,
      credential  = options.password,
      env         = options.env,
    )

    if options.command == 'version':
      version = cli.version()
      print 'server:', version.server
      print 'client:', version.client
      print 'protocol:', version.api
      return 0

    selection = cli.select(
      context     = options.context,
      timeout     = options.timeout,
      peo         = peo,
    )

  except client.Error as err:
    print >> sys.stderr, '[**] ERROR: %s' % (err,)
    return 20

  log.info('selection id: %s', selection.id)
  log.info('  channels: %r', [item.channel_id for item in selection.items])

  sys.stdout.write(selection.content)

  return 0

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
