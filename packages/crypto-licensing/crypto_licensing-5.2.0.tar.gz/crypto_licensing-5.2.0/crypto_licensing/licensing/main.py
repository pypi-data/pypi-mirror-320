#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Crypto-licensing -- Cryptographically signed licensing, w/ Cryptocurrency payments
#
# Copyright (c) 2022, Dominion Research & Development Corp.
#
# Crypto-licensing is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.  It is also available under alternative (eg. Commercial)
# licenses, at your option.  See the LICENSE file at the top of the source tree.
#
# It is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#

"""
    Implements the Crypto Licensing server
"""

from __future__ import print_function, absolute_import, division

import argparse
import curses, curses.ascii, curses.panel  # noqa: E401
import fnmatch
import json
import logging
import os
import posixpath
import signal
import sqlite3
import sys
import threading
import time
import traceback
import warnings

# Used for Web GUI, and for licensing database.  In the future, much of this will transition to
# Holochain-based infrastructure.
import web
import web.httpserver
import wsgilog

from ..misc		import (
    timer, Timestamp,
    log_cfg, log_levelmap, log_level,
    config_paths, config_open, ConfigNotFoundError,
    unquote
)
from ..			import licensing
from ..misc		import input_secure

__author__                      = "Perry Kundert"
__email__                       = "perry@dominionrnd.com"
__copyright__                   = "Copyright (c) 2022 Dominion Research & Development Corp."
__license__                     = "Dual License: GPLv3 (or later) and Commercial (see LICENSE)"

web.config.debug 		= False
web.config.session_parameters.update( {
    'cookie_name':	'session',
    'ignore_expiry':	True,
    'ignore_change_ip':	True,
    'timeout':		7*24*60*60,     # 1 week
} )

session_initializer		= {
    'user_id':	0,
    'name':	'',
    'pin':	0,
    'login':	0,			# 0 guest, 1 user, 2 admin
}


log				= logging.getLogger( "licensing" )

# Output files are stored in the CWD
LOGFILE				= "licensing.log"
DB_FILE				= "licensing.db"
ACCFILE				= "licensing.access"

CRDFILE				= "licensing.credentials"       # Any author credentials available persistently
KEYFILE				= "licensing." + licensing.KEYPATTERN
LICFILE				= "licensing." + licensing.LICPATTERN

# SQL configurations are typically found in crypto_licensing/licensing, but may be customized and
# placed in any of the installation's configuration file paths (eg. ~/.crypto-licensing/,
# /etc/crypto-licensing/, or the current working directory)
SQLFILE				= "licensing.sql"		# this + .* are loaded

OURPATH				= os.path.dirname( os.path.abspath( __file__ ))
TPLPATH				= os.path.join( OURPATH, "static/resources/templates/" )
LOCPATH				= os.path.abspath(os.path.curdir)

# License Server Configuration

config_extras			= [OURPATH]  # Any extra higher-priority configuration paths to look in


# The database: global 'db', which is a web.database connection.  Also 'db_lock', since sqlite3 is
# thread-safe, but will raise an exception if multiple threads attempt to write, provide a
# threading.Lock() to allow serializing of all db insert, update, etc. between threads.

# We will *always* execute all of the available ...sql* scripts.  These contain 'CREATE TABLE' and
# 'INSERT' commands, which will fail if the specified table/row already exists, so are safe to run
# repeatedly.  When we add tables and/or rows that don't already exist, they'll be created by these
# scripts.  This provides us with a rudimentary database update mechanism between releases, as long
# as we carefully migrate data from old to new tables.


db_statics			= {}
db_lock				= threading.Lock()
db				= None


def db_setup():
    """Set up application-global db, db_lock, ...  Should be done after config_extras is initialized."""

    init_db			= None
    db_file_path		= DB_FILE
    sqlfile_path		= SQLFILE
    try:
        # Load the licensing.db file.  If it can be found somewhere in the configuration path, use it --
        # otherwise, assume it's supposed to be here in the CWD.
        try:
            for f in config_open( DB_FILE ):
                with f:
                    db_file_path = f.name
                break
        except ConfigNotFoundError:
            pass
        init_db			= sqlite3.connect( db_file_path )

        # Load all licensing.sql* config files into the licensing.db Sqlite3 file.  We want to load
        # SQL files from most general/distant to most specific/nearest, so make reverse=False.
        global config_extra
        for f in config_open( SQLFILE+'*', extra=config_extras, skip='*~', reverse=False ):
            with f:
                sql		= f.read()
                sql_file	= f.name
            try:
                log.info( "Loading SQL from {}".format( sql_file ))
                init_db.executescript( sql )
            except (sqlite3.OperationalError,sqlite3.IntegrityError) as exc:
                log.info( "Failed to load %s (probably already configured, continuing): %s", sql_file, exc )
    except Exception as exc:
        log.warning( "Failed to execute {}* scripts into DB {}: {}".format(
            sqlfile_path, db_file_path, exc ))
        raise
    finally:
        if init_db:
            init_db.close()
    assert os.access( db_file_path, os.W_OK ), \
        "Cannot access licensing DB: {}".format( db_file_path )

    # OK, the DB has been initialized, and is at db_file_path.
    log.warning( "Opening DB at {path}".format( path=db_file_path ))
    global db
    db				= web.database( dbn='sqlite', db=db_file_path )
    assert hasattr( db, 'query' ), \
        "Unrecognized licensing DB connection: {!r}" % ( db )

    # Various static values that should be saved/restored.  Always begins at defaults on start-up!
    # But, also read from database.  All floating point.
    global db_statics
    db_statics			= {}
    for r in db.select( 'statics' ):
        db_statics[r.key]		= float( r.value )


def db_state_save():
    """Dump out any persistent licensing data, etc. that should be loaded next time.  This should be done
    from time to time, so we don't get too far behind, in case of a cold reboot.  Of course, save
    immediately upon license creation, etc.

    Make certain that all sqlite3 database calls are run in a single Thread.  We'll do the loading
    right below (here, in the Main Thread), but all other database I/O (including state_save()) must
    occur in the webpy Thread...

    From https://github.com/sampsyo/beets
    """
    with db_lock:
        log.info( "Saving state (thread: %s)", threading.current_thread().ident )

        for k in db_statics:
            if not db.update( 'statics', where="key = $key", vars={ "key": k }, value=db_statics[k] ):
                if not db.insert( 'statics', key=k, value=db_statics[k] ):
                    log.warning( "Failed to store statics key %s value %s" % ( k, db_statics[k] ))


def licenses( confirm=None, stored=None ):
    """Obtain all License provenances currently available from the DB and files, as a sequence of
    (signature, License) provenance pairs; signature is a 512-bit Ed25519 Signature as bytes.

    Each license provenance comprises a License and an Ed25519 Signature, and may contain dependencies.

    All unique licenses are found and yielded, indexed by their signatures.

    Any License for which you hold the Author signing keypair matching the Licenses' designed client
    / client_pubkey (or they are null/None) may be included in a new License's dependencies.

    In other words, you may create and author (sign) a brand new License with no dependencies, or
    with dependencies that have a client / client_pubkey matching your authoring keypair pubkey.

    TODO: Licenses specifying a *number* of things may be used as dependencies in authored Licenses
    until the sum of those things allocated to the authored licenses meets the License dependencies'
    number limit.

    """
    emitted			= set()

    def emit( *provs ):
        for p in provs:
            if p.signature in emitted:
                continue
            yield p.signature, p.license
            emitted.add( p.signature )
            for sig, lic in emit( *[ licensing.LicenseSigned( confirm=confirm, machine_id_path=False, **pd )
                                     for pd in p.license.dependencies or [] ] ):
                yield sig, lic

    # First, process any stored provenances.  These are assumed to contain .license and .signature
    # attributes.  Could be a sequence of LicenseSigned, or a database query yielding records with
    # .signature and .license.  These may be full Licenses structs and signatures bytes data, or
    # serialized forms.
    found			= 0
    for r in stored or []:
        try:
            prov		= licensing.LicenseSigned(
                license=r.license, signature=r.signature, confirm=confirm, machine_id_path=False )
        except Exception as exc:
            log.debug( "Failed to load stored License provenance: {exc} from: {lic}".format(
                exc=''.join( traceback.format_exception( *sys.exc_info() )) if log.isEnabledFor( logging.TRACE ) else exc,
                lic=r.license ))
            raise
        for sig, lic in emit( prov ):
            yield sig, lic
            found	       += 1
    log.info( "Licenses     saved: {}".format( found ))

    found			= 0
    path			= None
    try:
        # Load most general/distant Licenses first, including the optional extra config dirs
        global config_extras
        for path, prov in licensing.load( package=__package__, extra=config_extras, reverse=False ):
            for sig, lic in emit( prov ):
                yield sig, lic
                found	       += 1
    except Exception as exc:
        log.error( "Failed to load license from {}: {}".format( path or __package__, exc ))
        pass
    log.info( "Licenses    loaded: {}".format( found ))


def credentials( *add ):
    """Load any available credentials, and add any passed (description, (username, password)),
    ... containing new credentials supplied by the License Server administrator during operation.

    Each Thread of this License Server that must decrypt encrypted keys should use these credentials
    to access the keys.

    TODO: Should this be encrypted at-rest during operation?  It could be inspected by any
    user/root level process, and used to unlock the encrypted author signing keypairs.

    """
    yield "(No Credentials)", (None, None)

    credentials.local.update( add )
    for name, (username, password) in credentials.local.items():
        yield name, (username, password)
    log.info( "Credentials cached: {}".format( len( credentials.local )))

    found			= 0
    path			= None
    try:
        # Open any licensing.credentials* in configuration path.  We want to load most
        # general/distant files first so make reverse=True.
        global config_extras
        for f in config_open( CRDFILE+'*', extra=config_extras, skip='*~', reverse=False ):
            with f:
                # Each licensing.credentials* file should be a sequence of:
                #     [ ( "description", [ "username": "password" ] ), ... ]
                # so convert a dict into such a sequence.  However, reverse the .update so more
                # earlier (more specific) configurations are not overriden by later (more general)
                # ones.
                path		= f.name
                creds		= json.loads( f.read() )
            if isinstance( creds, dict ):
                creds		= creds.items()
            for name, (username, password) in creds:
                log.info( "  {n:<20}: {u:>20} / {p}".format( n=name, u=username, p='*' * len( password )))
                yield name, (username, password)
                found	       += 1
    except Exception as exc:
        log.error( "Failed to load {}*: {}".format( path or CRDFILE, exc ))
        pass
    log.info( "Credentials loaded: {}".format( found ))


credentials.local		= {}  # { description: (username, password), ... }


def keypairs():
    """Load all available keypairs available for authoring Licenses, using all currently available
    credentials.  This includes all Encrypted and Plaintext keys in files, and all Encrypted keys in
    database "authors" table.  Each time we add a new credential, this *may* make available more
    keys encrypted with those credentials.

    Yield sequence of all available (name, ...Keypair, credential) from "authors" table and files.
    May contain duplicates.  Caller may accumulate them, or simply scan for desired entry.

    """
    loaded			= set()
    saved			= 0
    for credname,(username,password) in credentials():
        log.info( "Keypairs for {}'s credential:".format( username ))
        for r in db.select( 'authors' ):
            cred		= dict( username=username, password=password )
            try:
                keypair		= licensing.KeypairEncrypted( ciphertext=r.ciphertext, salt=r.salt )
                keypair.into_keypair( **cred )  # Ensure the supplied credentials can decrypt it
                yield r.name, keypair, cred
                saved	       += 1
            except Exception as exc:
                # Most keypairs will fail to decrypt with most credentials...
                log.debug( "{n:<20}: Failed to decrypt w/ {u:>20} / {p}: {exc}".format(
                    n=r.name, u=cred['username'] or '(empty)', p='*' * len( cred['password'] or '(empty)' ),
                    exc=exc ))
                pass
        # Any Plaintext Keypairs (and perhaps some Encrypted ones, if duplicate credentials are
        # supplied) will be found multiple times.  Report keypairs at the same path only once.  We
        # want to load the most general/distant keys first, so reverse=False.
        path			= None
        try:
            global config_extras
            for path, keypair_src, cred, keypair in licensing.load_keypairs(
                    username=username, password=password,
                    detail=True, every=True,  # keypair may be an Exception
                    package=__package__,
                    extra=config_extras, reverse=False ):
                if isinstance( keypair, Exception ):
                    log.warning( "Failed to load keypair from {}: {}".format( path or __package__, keypair ))
                    continue
                if path not in loaded:
                    yield path, keypair, cred
                    loaded.add( path )
        except Exception as exc:
            log.error( "Failed to load keypair from {}: {}".format( path or __package__, exc ))
            pass
    log.info( "Keypairs     saved: {}".format( saved ))
    log.info( "Keypairs    loaded: {}".format( len( loaded )))


def licenses_data( path, stored=None, confirm=None, author=None, client=None, product=None ):
    """Returns all filtered licenses as data['list'] records, maybe w/ confirm of DKIM, filtered by
    author / client (maybe passed via path).  For example,

        licenses/Dom*/Awesome*   -->  All Dominion R&D Corp. authored Licenses to Awesome, Inc.

    The same result would be reached if liceses?author=Dom*&client=Awe*.

    """
    data			= {}
    data["title"]		= "Licenses"
    data["path"]		= path
    data["list"] = ll		= []
    data["keys"]		= ["author", "client", "product", "signature", "confirm", "license"]

    pathsegs			= path.strip('/').split('/') if path else []
    assert 0 <= len( pathsegs ) <= 2, \
        "Invalid licenses glob path {}; licenses/<author>/<client>/<product>".format( path )

    # Iterate all available licenses, filtering if additional license author name path component supplied
    for signature, lic in licenses( confirm=False, stored=stored ):
        record			= dict(
            author		= lic['author']['name'],
            client		= lic['client']['name'],
            product		= lic['author']['product'],
            signature		= licensing.into_b64( signature ),
            confirm		= None,
            license		= str( lic ),
        )
        author			= author or len( pathsegs ) > 0 and pathsegs[0]
        if author and not fnmatch.fnmatch( record['author'], author ):
            continue
        client			= client or len( pathsegs ) > 1 and pathsegs[1]
        if client and not fnmatch.fnmatch( record['client'], client ):
            continue
        product			= product or len( pathsegs ) > 2 and pathsegs[2]
        if product and not fnmatch.fnmatch( record['product'], product ):
            continue
        # After filtering out uninteresting Licenses, confirm if desired
        if confirm:
            try:
                lic.verify( confirm=confirm )
            except Exception as exc:
                record.update( confirm=str( exc ))
            else:
                record.update( confirm=True )
        ll.append( record )

    return data


def credentials_data( path ):
    data			= {}
    data["title"]		= "Credentials"
    data["path"]		= path
    data["list"] = ll		= []
    data["keys"]		= ["name", "username", "password"]

    pathsegs			= path.strip('/').split('/') if path else []
    assert 0 <= len( pathsegs ) <= 1, "Invalid credentials path {}".format( path )

    for name,(username,password) in credentials():
        if pathsegs and pathsegs[0] and not fnmatch.fnmatch( name, pathsegs[0] ):
            log.info( "Credential {} didn't match {}".format( name, path ))
            continue
        record			= dict(
            name	= name,
            username	= username,
            password	= password,
        )
        ll.append( record )

    return data


def keypairs_data( path ):
    data			= {}
    data["title"]		= "Keypairs"
    data["path"]		= path
    data["list"] = ll		= []
    data["keys"]		= ["name", "public_key", "credentials"]

    pathsegs			= path.strip('/').split('/') if path else []
    assert 0 <= len( pathsegs ) <= 1, "Invalid keypairs path {}".format( path )

    # Get all credentials into creds: { name: (username,password), ... }, and build a reverse-lookup dict
    # creds_reverse: { (username,password): name, ... }
    creds			= dict( credentials() )
    creds_reverse		= { v: k for k,v in creds.items() }

    log.info( "Keypairs data w/ {} credential:".format( len( creds_reverse )))
    for name,keypair,cred in keypairs():
        log.info("Found keypair: {!r}".format( (name,keypair,cred) ))
        if pathsegs and pathsegs[0] and not fnmatch.fnmatch( name, pathsegs[0] ):
            log.info( "Credential {} didn't match {}".format( name, path ))
            continue
        record			= dict(
            name	= name,
            public_key	= licensing.into_b64( keypair.into_keypair( **cred ).vk ),
            credentials	= creds_reverse.get( (cred['username'], cred['password']), '(unknown)' ),
        )
        ll.append( record )

    return data


# Set up signal handling (log rotation, log level, etc.)
# Output logging to a file, and handle UNIX-y log file rotation via 'logrotate', which sends
# signals to indicate that a service's log file has been moved/renamed and it should re-open

uptime_basis			= timer()
uptime_signalled		= False
shutdown_signalled		= False
logrotate_signalled		= False
levelmap_change			= 0  # may become +'ve/-'ve


def uptime_request( signum, frame ):
    global uptime_signalled
    uptime_signalled		= True


def shutdown_request( signum, frame ):
    global shutdown_signalled
    shutdown_signalled		= True


def logrotate_request( signum, frame ):
    global logrotate_signalled
    logrotate_signalled		= True


def loglevelup_request( signum, frame ):
    global levelmap_change
    levelmap_change	       += 1


def logleveldn_request( signum, frame ):
    global levelmap_change
    levelmap_change	       -= 1


def signal_service():
    """Service known signals.  When logging, default to log at WARNING, but ensure the
    message is seen if higher (eg. WARNING).  Support being in unknown logging
    levels when in/decreasing.

    """
    global levelmap_change
    if levelmap_change:
        rootlog			= logging.getLogger()
        actual			= rootlog.getEffectiveLevel()
        # Find the current log_levelmap key w/ a level value nearest our current actual level.  Default to 0.
        key,dif			= 0,1000
        for k,lvl in log_levelmap.items():
            if abs( lvl - actual ) < dif:
                key		= k
        # Get an available log_level up/down from the currently active one
        desired			= log_level( key + levelmap_change )
        if actual != desired:
            rootlog.setLevel( desired )
        levelmap_change		= 0

    global logrotate_signalled
    global uptime_signalled
    if logrotate_signalled:
        logrotate_signalled	= False
        uptime_signalled	= True

        rootlog			= logging.getLogger()
        actual			= rootlog.getEffectiveLevel()
        rootlog.log( max( logging.WARNING, actual ), "Rotating log files due to signal" )
        for hdlr in logging.root.handlers:
            if isinstance( hdlr, logging.FileHandler ):
                hdlr.close()

    global uptime_basis
    if uptime_signalled:
        uptime_signalled	= False
        uptime			= timer() - uptime_basis

        rootlog			= logging.getLogger()
        actual			= rootlog.getEffectiveLevel()
        rootlog.log( max( logging.WARNING, actual ), "Uptime: %3d:%02d:%06.3f",
                     int( uptime // 3600 ), int( uptime % 3600 // 60 ), uptime % 60 )


signal.signal( signal.SIGHUP,  logrotate_request )
signal.signal( signal.SIGUSR1, loglevelup_request )
signal.signal( signal.SIGUSR2, logleveldn_request )
signal.signal( signal.SIGTERM, shutdown_request )
signal.signal( signal.SIGURG,  uptime_request )

now				= timer()


def daytime( ts ):
    return Timestamp( ts )

#
# Curses-based Textual UI.
#


def message( window, text, row = 23, col = 0, clear = True ):
    rows,cols			= window.getmaxyx()
    if col < -len( text ) or row < 0 or row >= rows or col >= cols:
        return
    if col < 0:
        text			= text[-col:]
        col			= 0
    try:
        window.addstr( int( row ), int( col ), text[:cols-col] )
        if clear:
            window.clrtoeol()
    except Exception:
        pass


#
# pan{siz,loc} -- compute appropriate size and location for sensor detail panel
#
def pansiz( rows, cols ):
    return rows * 9 // 10, cols // 3


def panloc( c, rows, cols ):
    return rows//15, ( c < cols//2 ) and ( cols//2 + cols//10 ) or ( 0 + cols//10 )


def txt( win, config ):

    global now
    last			= now
    selected			= 0

    rows, cols			= 0, 0

    log.info("threads: %2d: %s" % (
        threading.active_count(),
        ', '.join( [ t.name for t in threading.enumerate() ] )))

    display			= 'licenses'		# Start off displaying Licenses
    input			= 0
    delta			= 0.0
    pansel			= None
    while not config.get( 'done' ):
        message( win, "%s (%7.3f): (%3d == '%c') Quit [qy/n]?"
                 % (  daytime( now ), delta,
                      input, curses.ascii.isprint( input ) and chr( input ) or '?'),
                 row = 0, clear = False )

        curses.panel.update_panels()
        curses.doupdate()

        # End of display loop; display updated; Beginning of next loop; await input
        input			= win.getch()

        # Refresh the things to include in the selected display.
        include			= config[display]
        if hasattr( include, '__call__' ):
            include		= list( include() )

        # Compute time advance since last update
        real			= timer()
        delta			= real - last

        # Detect window size changes, and adjust detail panel accordingly (creating if necessary)
        if (rows, cols) != win.getmaxyx():
            rows, cols		= win.getmaxyx()
            winsel		= curses.newwin( * pansiz( rows, cols ) + panloc( 0, rows, cols ))
            try:
                pansel.replace( winsel )
            except Exception:
                pansel		= curses.panel.new_panel( winsel )

        # Process input, adjusting parameters
        if 0 < input <= 255 and chr( input ) == 'q':
            config['control']['done'] = True
            return

        if 0 < input <= 255 and chr( input ) == '\f':			# FF, ^L
            # ^L -- clear screen
            winsel.clear()

        # Select next space, adjust target temp
        if input == curses.ascii.SP:					# ' '
            if pansel.hidden():
                pansel.show()
            else:
                pansel.hide()
        if selected > len( include ):
            selected		= len( include )
        if input in ( curses.ascii.STX, curses.KEY_LEFT, 260 ):		# ^b, <--
            if include:
                selected	= ( selected - 1 ) % len( include )
        if input in ( curses.ascii.ACK, curses.KEY_RIGHT, 261 ):        # ^f, -->
            if include:
                selected	= ( selected + 1 ) % len( include )
        if input in ( curses.ascii.DLE, curses.KEY_UP, 259 ):		# ^, ^p
            if include and include[selected] == 'world':		# |
                # do something to world...
                pass
            else:
                curses.beep()
        if input in ( curses.ascii.SO, curses.KEY_DOWN, 258 ):		# |
            if include and include[selected] == 'world':		# v, ^n
                pass
            else:
                curses.beep()

        if 0 < input <= 255 and chr( input ) in ( 'C', 'c', 'M', 'm' ):
            # Character keypresses
            pass

        # When a keypress is detected, always loop back and get another key, to absorb multiple
        # keypresses (eg. due to key repeat), but only do it if less then 1/3 second has passed.
        if 0 < input and delta < .3:
            continue

        # We'll be computing a new model; advance (and remember) time
        last			= real
        now                     = real

        # Next frame of animation
        win.erase()

        topmargin               = 2
        #botmargin		= 9
        #botrow			= rows - botmargin

        # Compute screen size and display headers.  We want cells a bit higher than wide, and at
        # least 20 characters wide.  Keep piling 'til we are either over 20 characters wide, or less
        # than 5/4ths as high as wide.  If we can't find a way to get cells >= 10 rows high, fail
        # and loop 'til they fix the display size.
        try:
            areas		= len( include )
            across		= 1
            rank		= 1

            def cellyx():
                y		= ( rows - topmargin ) // rank
                x		= cols // across
                return y,x

            height,width	= cellyx()
            while width > 60:
                across	       += 1
                height,width	= cellyx()
            while height > 20:
                rank	       += 1
                height,width	= cellyx()
            assert height >= 10 and width >= 30
        except Exception:
            message( win, "Insufficient screen size (%d areas, %d ranks of %d  %dx%d cells); increase height/width, or reduce font size" % (
                areas, rank, across, width, height ), col = 0, row = 0 )
            win.refresh()
            time.sleep( 2 )
            continue

        # Make h- and v-bars, everywhere except top margin
        for r in range( topmargin, rows ):
            if ( rows - r ) % height == 0:
                win.hline( r, 0, curses.ACS_HLINE, cols )
        for c in range( width, cols, width):
            win.vline( topmargin, c, curses.ACS_VLINE, rows - topmargin )

        # Update
        winsel.erase()
        wsrows, wscols		= winsel.getmaxyx()

        r			= 2
        try:
            winsel.hline( r, 1, curses.ACS_HLINE, wscols - 2 )
        except Exception:
            pass
        r                      += 1

        try:
            winsel.hline( r, 1, curses.ACS_HLINE, wscols - 2 )
        except Exception:
            pass
        r                      += 1

        winsel.border( 0 )

    # Final refresh (in case of error message)
    win.refresh()


def deduce_encoding( available, environ, accept=None ):
    """Deduce acceptable encoding from HTTP Accept: header:

        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

    If it remains None (or the supplied one is unrecognized), the
    caller should fail to produce the desired content, and return an
    HTML status code 406 Not Acceptable.

    If no Accept: encoding is supplied in the environ, the default
    (first) encoding in order is used.

    We don't test a supplied 'accept' encoding against the HTTP_ACCEPT
    settings, because certain URLs have a fixed encoding.  For
    example, /some/url/blah.json always wants to return
    "application/json", regardless of whether the browser's Accept:
    header indicates it is acceptable.  We *do* however test the
    supplied 'accept' encoding against the 'available' encodings,
    because these are the only ones known to the caller.

    Otherwise, return the first acceptable encoding in 'available'.

    """
    if accept:
        # A desired encoding; make sure it is available
        accept		= accept.lower()
        if accept not in available:
            accept	= None
        return accept

    # No predefined accept encoding; deduce preferred available one.
    # Accept: may contain */*, */json, etc.  If multiple matches,
    # select the one with the highest Accept: quality value (our
    # present None starts with a quality metric of 0.0).  Test
    # available: ["application/json", "text/html"], vs. HTTP_ACCEPT
    # "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    # Since earlier matches are the for more preferred encodings,
    # later matches must *exceed* the quality metric of the earlier.
    HTTP_ACCEPT		= environ.get( "HTTP_ACCEPT", "*/*" ).lower() if environ else "*/*"
    quality		= 0.0
    for stanza in HTTP_ACCEPT.split( ',' ):
        # application/xml;q=0.9
        q		= 1.0
        for encoding in reversed( stanza.split( ';' )):
            if encoding.startswith( "q=" ):
                q	= float( encoding[2:] )
        for avail in available:
            match	= True
            for a, t in zip( avail.split( '/' ), encoding.split( '/' )):
                if a != t and t != '*':
                    match = False
            if match:
                if q > quality:
                    quality	= q
                    accept	= avail
    return accept


def http_exception( framework, status, message ):
    """Return an exception appropriate for the given web framework,
    encoding the HTTP status code and message provided.
    """
    if framework and framework.__name__ == "web":
        if status == 404:
            return framework.NotFound( message )

        if status == 406:
            return framework.NotAcceptable()			# Will not accept a message

    return Exception( "%d %s" % ( status, message ))


def licenses_request( render, path, environ, accept, framework,
                         queries=None, posted=None,
                         session=None, logged=None,		# The user session
                         proxy=None ):

    """
        api/licenses/<name>/

    """
    variables			= queries or posted or {}
    content			= deduce_encoding( [ "text/html",
                                                     "application/json", "text/javascript",
                                                     "text/plain" ],
                                                   environ=environ, accept=accept )
    response			= ""

    # A URL w/ an empty ...?confirm is assumed to be True.
    confirm			= licensing.into_boolean( variables.get( 'confirm', False ), truthy=('',) )
    author			= licensing.into_str( variables.get( 'author' ))
    client			= licensing.into_str( variables.get( 'client' ))
    product			= licensing.into_str( variables.get( 'product' ))
    stored			= list( db.select( 'licenses' ))
    data			= licenses_data( path, stored=stored, confirm=confirm,
                                                 author=author, client=client, product=product )

    if content and content in ( "application/json", "text/javascript", "text/plain" ):
        callback		= variables.get( 'callback', "" )
        if callback:
            response           += callback + "( "
        response               += licensing.into_JSON( data, indent=4 )
        if callback:
            response           += " )"
    elif content and content in ( "text/html" ):
        response		= render.keylist( data )
    else:
        raise http_exception( framework, 406, "Unable to produce %s content" % (
            content or accept or "unknown" ))
    return content, response


def credentials_request( render, path, environ, accept, framework,
                         queries=None, posted=None,
                         session=None, logged=None,		# The user session
                         proxy=None ):

    """
        api/credentials/<name>/

    """
    variables			= queries or posted or {}
    content			= deduce_encoding( [ "text/html",
                                                     "application/json", "text/javascript",
                                                     "text/plain" ],
                                                   environ=environ, accept=accept )
    response			= ""

    data			= credentials_data( path )

    if content and content in ( "application/json", "text/javascript", "text/plain" ):
        callback		= variables.get( 'callback', "" )
        if callback:
            response           += callback + "( "
        response               += licensing.into_JSON( data, indent=4 )
        if callback:
            response           += " )"
    elif content and content in ( "text/html" ):
        response		= render.keylist( data )
    else:
        raise http_exception( framework, 406, "Unable to produce %s content" % (
            content or accept or "unknown" ))
    return content, response


def keypairs_request( render, path, environ, accept, framework,
                         queries=None, posted=None,
                         session=None, logged=None,		# The user session
                         proxy=None ):

    """
        api/keypairs/<name>/

    """
    variables			= queries or posted or {}
    content			= deduce_encoding( [ "text/html",
                                                     "application/json", "text/javascript",
                                                     "text/plain" ],
                                                   environ=environ, accept=accept )
    response			= ""
    data			= keypairs_data( path )

    if content and content in ( "application/json", "text/javascript", "text/plain" ):
        callback		= variables.get( 'callback', "" )
        if callback:
            response           += callback + "( "
        response               += licensing.into_JSON( data, indent=4 )
        if callback:
            response           += " )"
    elif content and content in ( "text/html" ):
        response		= render.keylist( data )
    else:
        raise http_exception( framework, 406, "Unable to produce %s content" % (
            content or accept or "unknown" ))
    return content, response


def issue_request( render, path, environ, accept, framework,
                    queries=None, posted=None, logged=None, proxy=None ):
    """Returns a License issuance response, as HTML or JSON.

        api/issue		-- all licenses

    When an application running on a host finds that it does not have an appropriate signed License
    available, it may request one from a cpppo.crypto.licensing server.  If such a License is
    available to issue, it will be returned.

    If not available, instructions on how to get the License issued are returned (eg. agree to
    licensing terms by paying USDC$100.00 to Ethereum address 0x3193...1ee3).  As soon as the
    License server sees that the contractual requirement has been met, the license is issued and the
    next call to the same api/issue... endpoint will return the newly Ed25591-signed License.

    If the License specifies a certain Client Public key, then the request must be signed by the
    corresponding Ed25519 Signing key.  This is almost certainly the case; issuing Licenses with a
    "null"/None client -- that allow sub-Licensing to other clients -- is not likely something you
    want to do automatically.  This proves that the requester is actually the Client; not just
    someone who knows the Client's public key.

    Only if sufficient License(s) are available in the server will they be issued.

    """
    # When using jQuery $.ajax() w/dataType: 'jsonp', it appends a
    # ?callback=... query, and sends an Accept: ... text/javascript
    # header.  Hence, accept either form.
    content			= deduce_encoding( [ "text/html",
                                                     "application/json", "text/javascript",
                                                     "text/plain" ],
                                                   environ=environ, accept=accept )
    response			= ""

    variables			= queries or posted or {}

    # Full specifications of desired License.  Must include client_pubkey.
    confirm			= licensing.into_boolean( variables.get( 'confirm', False ), truthy=('',) )
    author			= variables.get( 'author' )
    author_pubkey		= variables.get( 'author_pubkey' )
    product			= variables.get( 'product' )
    client			= variables.get( 'client' )
    client_pubkey		= variables.get( 'client_pubkey' )		# Must sign the issue request
    machine			= variables.get( 'machine' )
    signature			= variables.get( 'signature' )
    number			= variables.get( 'number' )			# optional client-supplied serialization

    # TODO: verify the signature is that of the original canonicalized, serialized IssueRequest payload
    #
    #     ...?author=Blah,%20Inc&client_pubkey=...&machine=00010203-...0e0f&signature=9Dba...Cg==
    #         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #
    # We must serialize the request in a standard way in the sender and the receiver, because the
    # data may be sent as URL arguments or POST header variables.
    issue_request		= licensing.IssueRequest(
        author=author, author_pubkey=author_pubkey, product=product,
        client=client, client_pubkey=client_pubkey, machine=machine )
    log.info( "Issue request number={number}; {req}, w/ signature: {sig!r}".format(
        number=number, req=str( issue_request ), sig=signature ))
    try:
        issue_request.verify( pubkey=client_pubkey, signature=signature )
    except Exception as exc:
        raise http_exception( framework, 401, "Ed25519 Signature of request is incorrect: {exc}".format(
            exc=exc ))

    # See if there are License(s) that match a certain portion of the requirements.  An exact match
    # can be directly returned.  A partial match can be sub-licensed.
    skip_tab = {
        'client':	lambda lic: lic.client and issue_request['client'] and lic.client['name'] != issue_request['client'],
        'client_pubkey':lambda lic: lic.client and issue_request['client_pubkey'] and lic.client['pubkey'] != issue_request['client_pubkey'],
        'author':	lambda lic: issue_request['author'] and lic.author['name'] != issue_request['author'],
        'author_pubkey':lambda lic: issue_request['author_pubkey'] and lic.author['pubkey'] != issue_request['author_pubkey'],
        'product':	lambda lic: issue_request['product'] and lic.author['product'] != issue_request['product'],
        'machine':	lambda lic: issue_request['machine'] and lic['machine'] != issue_request['machine'],
    }

    def prov_to_issue():
        """Produce a LicenseSigned suitable for the client to receive, use as a dependency of a new
        License specific to their machine, and sign and install.

        Since we scan the database 'licenses' table, do some computations and then update the table,
        we need to db_lock around this entire process, to avoid multiple simultaneous requests
        issuing the same License.  Since we do no DKIM confirmation or other network I/O here (only
        file reading), it should be quick.

        """

        def lics_filtered( *names ):
            """Scan the loaded/stored Licenses for  """
            stored			= list( db.select( 'licenses' ))
            for sig, lic in licenses( confirm=False, stored=stored ):
                log.info( "Issue request number={number}; {name}'s {product}: mismatched keys: {keys}".format(
                    number=number, name=lic.author['name'], product=lic.author['product'],
                    keys=', '.join( n for n in names if skip_tab[n]( lic ) )))
                if any( skip_tab[n]( lic ) for n in names ):
                    continue
                log.info( "Issue request number={number}; {name}'s {product} accepted: {lic}".format(
                    number=number, name=lic.author['name'], product=lic.author['product'], lic=lic ))
                yield sig, lic

        # Ideally, everything matches exactly one specific License already issued to this Client for
        # this machine.  If we've already issued the License (and perhaps the client forgot to
        # install it, or re-installed the software), and needs it again.
        try:
            (sig, lic),		= lics_filtered( 'author', 'author_pubkey', 'product', 'client', 'client_pubkey', 'machine' )
        except ValueError as exc:
            log.warning( "Failed: {exc}".format( exc=exc ))
            pass
        else:
            if lic.client and lic.machine:  # Exact match, with specific client and machine
                log.warning( "Issue request number={number}; Reissuing existing License: {lic}".format(
                    number=number, lic=lic if log.isEnabledFor( logging.INFO ) else licensing.into_b64( sig )))
                return licensing.LicenseSigned(
                    license=lic, signature=sig, confirm=False, machine_id_path=False )

        # OK, not already issued.  Find a License to specialize.  If one matches the author and
        # client (or specifies no client) and has no machine, use it to author a new License, simply
        # specialized with the client and machine specified.  The client will receive and
        # sub-License it by creating a new License with this a one of its dependencies, then sign it
        # with the client signing key they hold, and install it.
        try:
            (sig, lic),		= lics_filtered( 'author', 'author_pubkey', 'product', 'client', 'client_pubkey' )
        except ValueError as exc:
            log.warning( "Failed: {exc}".format( exc=exc ))
            pass
        else:
            if not lic.machine or lic['machine'] == issue_request['machine']:
                log.info( "Issue request number={number}; Specializing existing License: {lic}".format(
                    number=number, lic=lic if log.isEnabledFor( logging.INFO ) else licensing.into_b64( sig)))
                author_sigkey	= None
                for name,keypair,cred in keypairs():
                    vk, sk	= keypair.into_keypair( **cred )
                    pubkey	= licensing.into_b64( vk )
                    if name == lic.author['name'] and pubkey == issue_request['author_pubkey']:
                        author_sigkey = sk
                        break
                # Issue a new specialized License for Client, signed with Author's private signing key.
                if not lic.client:
                    lic.client	= licensing.Agent( name=issue_request['client'], pubkey=issue_request['client_pubkey'] )
                lic.machine	= licensing.into_UUIDv4( issue_request['machine'] )
                prov		= licensing.issue(
                    license=lic, author_sigkey=author_sigkey, confirm=False, machine_id_path=False )
                insert = db.insert( 'licenses',
                                    signature=prov['signature'],
                                    license=str( prov.license ))
                assert insert, "Specializing license insert failed"
                log.warning( "Issue request number={number}; Issued specialized License: {lic}".format(
                    number=number, lic=prov.license if log.isEnabledFor( logging.INFO ) else licensing.into_b64( prov.signature )))
                return prov

        raise http_exception( framework, 409, "No matching Licenses found matching request: {}".format(
            issue_request ))

    with db_lock:
        prov			= prov_to_issue()
    log.info( "Issue request number={number}; Issuing License for {name}' {product}".format(
        number=number, name=prov.license.author['name'], product=prov.license.author['product'] ))

    data			= {}
    data["title"]		= path or "Issue"
    data["path"]		= path
    data["list"] = ll		= []
    data["keys"]		= ["author", "client", "product", "signature", "confirm", "license"]

    record			= dict(
        author		= prov.license['author']['name'],
        client		= prov.license['client']['name'],
        product		= prov.license['author']['product'],
        signature	= licensing.into_b64( prov.signature ),
        confirm		= None,
        license		= prov.license,
    )
    if confirm:
        log.warning( "Issue request number={number}; Confirming DKIM for {name}' {product}".format(
            number=number, name=prov.license.author['name'], product=prov.license.author['product'] ))
        try:
            licensing.verify( prov, confirm=confirm, machine_id_path=False )
        except Exception as exc:
            record.update( confirm=str( exc ))
        else:
            record.update( confirm=True )
    ll.append( record )

    if content and content in ( "application/json", "text/javascript", "text/plain" ):
        callback		= variables.get( 'callback', "" )
        if callback:
            response           += callback + "( "
        response               += licensing.into_JSON( data, indent=4 )
        if callback:
            response           += " )"
    elif content and content in ( "text/html" ):
        response		= render.keylist( data )
    else:
        raise http_exception( framework, 406, "Unable to produce %s content" % (
            content or accept or "unknown" ))
    log.info("Issue request number={number}; done".format( number=number ))
    return content, response


def inline( filename ):
    """A web.py templetor global function to inline files, relative to the
    directory of this python file.  Use:

    $:inline( "some/javascript/file.js" )

    """
    with open( os.path.join( OURPATH, filename ), 'r' ) as f:
        return f.read()


def webpy( config ):
    """web.py interface.  Deduces accept encoding from Accept: header, or force
    JSON Content-Type: if .json path was explicitly requested.

    """
    config.setdefault( 'address',("0.0.0.0", 8000) )

    session			= None		# Will become a web.session.Session

    def logged( admin=False ):
        """Checked that the session's user is logged in.  Even if a user authenticates, their account
        may be disabled.

        """
        return session and session.login >= ( 2 if admin else 1 )

    def proxy( env ):
        """Detects if we are behind a proxy, and creates correct path if
        necessary, to use the original forwarded host.

        """
        proxy			= env.get( "HTTP_X_FORWARDED_HOST", "" )
        if proxy:
            proxy		= "http://" + proxy
        return proxy

    urls			= (
        "/",				"index",
        r"/index(\.html)?",		"index",
        "/(.*)/",			"trailing_stuff",
        r"/(.*)\.html",			"trailing_stuff",
        "/favicon.ico",			"favicon",
        "/robots.txt",			"robots",
        "/login",			"login",
        "/logout",			"logout",
        r"/api/issue(\.json)?",		"api_issue",		# path: "", ".json"
        "/api/issue/(.+)?",		"api_issue",		# path: "...", "....json"
        r"/api/licenses(\.json)?",	"api_licenses",
        "/api/licenses/(.+)?",		"api_licenses",
        r"/api/credentials(\.json)?",	"api_credentials",
        "/api/credentials/(.+)?",	"api_credentials",
        r"/api/keypairs(\.json)?",	"api_keypairs",
        "/api/keypairs/(.+)?",		"api_keypairs",
    )

    class trailing_stuff:
        def GET( self, path ):
            web.seeother( proxy( web.ctx.environ ) + '/' + path )

    class favicon:
        def GET( self ):
            """Always permanently redirect favicon.ico requests to our favicon.png.
            The reason we do this instead of putting a <link "icon"...> is because
            all *other* requests from browsers (ie. api/... ) returning non-HTML
            response Content-Types such as application/json *also* request
            favicon.ico, and we don't have an HTML <head> to specify any icon link.
            Furthermore, they continue to request it 'til satisfied, so we do a 301
            Permanent Redirect to satisfy the browser and prevent future requests.
            So, this is the most general way to handle the favicon.ico"""
            web.redirect( '/static/images/favicon.ico' )

    class robots:
        def GET( self ):
            web.header( "Content-Type", "text/plain" )
            return """\
User-agent: *
Disallow: /
"""

    class index:
        def GET( self, path=None ):
            render		= web.template.render(
                TPLPATH, base="layout", globals={'inline': inline, 'session': session} )
            response		= render.index( {
                "title": 	"Licensing",
                "text":		"Hello, world!",
            } )
            web.header( "Content-Type", "text/html" )
            return response

    class logout:
        def GET( self ):
            session.login	= 0
            web.seeother( proxy( web.ctx.environ ) + '/login' )

    def user_heritage( user_id ):
        """
        Return a dict containing the heirarchy of user names created by the specified user.
        """
        result			= {}

        spawn			= db.select( 'users', where='creator = $user_id', vars={ "user_id": user_id })
        for child in spawn:
            if child.user_id == user_id:
                continue

            key			= (child.name, child.user_id)
            result[key]		= user_heritage( child.user_id )

        return result

    def user_heritage_print( h, level=0 ):
        if not h:
            return
        for key in h:
            name,user_id	= key
            log.info("%s %s" % ( ' '*level, name ))
            if h[key]:
                user_heritage_print( h[key], level+1 )

    class login:
        """
        Takes an optional ?redirect=url and passes it via the POST.
        """
        def GET( self ):
            """Allow login; if session.login already true, then display PIN change dialog."""
            log.info( "Session: %r" % ( session.items() ))
            children		= None
            if logged():
                children	= user_heritage( session.user_id )
                user_heritage_print( children )

            render		= web.template.render(
                TPLPATH, base="layout", globals={'inline': inline, 'session': session} )
            response		= render.login(
                {
                    "title":	( "Login"
                                  if not logged() else
                                  "Welcome %s" % ( session.name.capitalize() )),
                    "redirect":	web.input().get( "redirect", "" ),
                    "children": children,
                })
            web.header( "Cache-Control", "no-cache" )
            web.header( "Content-Type", "text/html" )
            return response

        def POST( self ):
            """Use the provided PIN to authenticate a user, and then remember the credentials in the
            session.  If already logged in, and the 'pinnew' value and 'change' button was supplied,
            then change the user's PIN.

            """
            log.info( "Session: %r, input: %r" % ( session.items(), web.input().items() ))
            render		= web.template.render(
                TPLPATH, base="layout", globals={'inline': inline, 'session': session} )

            if "add" in web.input():
                # Post via "add" button; add a new user/PIN w/ a selected subset of current user's
                # zones.  Try update first (of existing user/PIN in the session users heritage),
                # then insert.
                error		= None
                try:
                    assert logged(), "Not logged in"
                    name	= web.input().get( "name" )
                    assert name, "Empty name"
                    login	= web.input().get( "login", 1 )
                    assert 0 <= int( login ) <= 2, "Invalid login Disable(0)/Normal(1)/Admin(2)"
                    pin		= web.input().get( "pin" )

                    update	= None
                    if logged( admin=True ):
                        # If the current user is an admin user, we can alter an existing user
                        # that we've created; change a pin or login privileges
                        evaluate		= user_heritage( session.user_id ).items()
                        target			= None
                        while evaluate:
                            item		= evaluate.pop()
                            (inam,iuid),subs	= item
                            if inam == name:
                                target		= iuid
                                break
                            else:
                                # Not updating this user; perhaps one of their sub-users?
                                evaluate       += subs.items()
                        if target:
                            log.info( "Updating user: %r" % ( name ))
                            kwds		= {}
                            kwds["login"]	= login
                            if pin:    # Update pin too, if supplied
                                kwds["pin"]	= pin
                            with db_lock:
                                update = db.update( 'users', where='user_id = $user_id',
                                                    vars={ "user_id": target }, **kwds )
                            assert update, "Update failed"
                    if not update:
                        # Existing user not found and updated; insert a new one
                        assert pin, "Empty PIN"
                        log.info( "Adding User: %r" % ( name ))
                        with db_lock:
                            insert = db.insert( 'users',
                                                creator=session.user_id,
                                                name=name.lower(),
                                                pin=pin,
                                                login=login )
                        assert insert, "Insert failed"
                except Exception as exc:
                    log.info( "Add/Update user failure: %s: %s" % ( exc, traceback.format_exc() ))
                    error	= str( exc )
                response	= render.login(
                    {
                        "title":	( "Add User Failed: %s" % ( error )
                                          if error else
                                          "Updated User %s" % ( name )
                                          if update else
                                          "Added User %s" % ( name )),
                        "redirect":	web.input().get( "redirect", "" ),
                        "children":	user_heritage( session.user_id ),
                    })
                web.header( "Cache-Control", "no-cache" )
                web.header( "Content-Type", "text/html" )
                return response

            if "change" in web.input():
                # Post via "change" button, and a new PIN provided; update the record for the logged
                # in user/PIN, who may have several with different PINs and capabilities.
                error		= None
                try:
                    assert logged(), "Not logged in"
                    pin		= web.input().get( "pin" )
                    assert pin, "Empty PIN"
                    with db_lock:
                        query	= db.update( 'users', where='name = $name AND pin = $pin',
                                             pin=web.input().get( 'pin' ),
                                             vars={
                                                 "name": session.name.lower(),
                                                 "pin": session.pin,
                                             })
                    assert query, "Update failed: %r" % ( query )
                except Exception as exc:
                    logging.info( "PIN change failure: %s: %s" % ( exc, traceback.format_exc() ))
                    error	= str( exc )
                response	= render.login(
                    {
                        "title":	( "PIN Changed for %s" % ( session.name )
                                          if not error else
                                          "PIN Change Failed: %s" % ( error )),
                        "redirect":	web.input().get( "redirect", "" ),
                        "children":	user_heritage( session.user_id ),
                    })
                web.header( "Cache-Control", "no-cache" )
                web.header( "Content-Type", "text/html" )
                return response

            if "delete" in web.input():
                # Delete users.  We can only delete users we've created.  Get our user heritage, and
                # see if matching "delete-<user>-<user_id>" checkboxes show up in the form.
                error		= None
                removed		= []
                try:
                    assert logged(), "Not logged in"
                    # [((name,user_id),{...}), ...]
                    evaluate	= user_heritage( session.user_id ).items()
                    exterminate	= []
                    while evaluate:
                        item		= evaluate.pop()
                        (name,uid),subs	= item
                        checkbox	= "delete-%s-%s" % ( name, uid )
                        if checkbox in web.input():
                            # Yup; this (and all their kids) are gone.
                            exterminate.append( item )
                        else:
                            # Not deleting this user; perhaps one of their sub-users?
                            evaluate   += subs.items()
                    while exterminate:
                        item		= exterminate.pop()
                        (name,uid),subs	= item
                        exterminate    += subs.items()
                        logging.warning("Delete user %s (%s)" % ( name, uid ))
                        with db_lock:
                            db.delete( 'users', where='user_id = $user_id',
                                       vars={
                                           "user_id": uid,
                                       })
                        removed.append( name )

                except Exception as exc:
                    logging.info( "Delete user failure: %s: %s" % ( exc, traceback.format_exc() ))
                    error	= str( exc )
                removed		= ", ".join( str(u) for u in removed ) if removed else "nobody"
                response	= render.login(
                    {
                        "title":	( "Deleted %s" % ( removed )
                                          if not error else
                                          "Deleted %s; Failed: %s" % ( removed, error )),
                        "redirect":	web.input().get( "redirect", "" ),
                        "children":	user_heritage( session.user_id ),
                    })
                web.header( "Cache-Control", "no-cache" )
                web.header( "Content-Type", "text/html" )
                return response

            # Post via "go" button (or via event on PIN input); attempt to login
            ident		= None
            error		= None
            try:
                name		= web.input().get( "name" )
                pin		= web.input().get( "pin" )
                assert name and pin, "Invalid user/PIN"
                query		= db.select( 'users', where='name=$name', vars={"name": name.strip().lower()} )
                assert query, "User not found: %r" % ( query )
                for i in query:
                    logging.info( "name: %r vs. %r, pin: %r vs %r" % ( i['name'], name, i['pin'], pin ))
                    if i['pin'] == int( pin ):
                        ident	= i
                        break
                assert ident, "Unrecognized user/PIN"
            except Exception as exc:
                logging.warning( "Login failed: name: %r, pin: %r: %s: %s" % ( name, pin, exc, traceback.format_exc() ))
                error		= str( exc )
            if ident:
                logging.info( "Login ident:   %r" % ( ident.items() ))
                session.update( ident )
                logging.info( "Login session: %r" % ( session.items() ))
                web.seeother( proxy( web.ctx.environ ) + web.input().get( "redirect", "" ))
            else:
                # No ident found; error contains explanatory string.  Try again.
                session.login	= 0
                response	= render.login(
                    {
                        "title":	"Login Failed: %s" % error,
                        "redirect":	web.input().get( "redirect", "" ),
                    })
                web.header( "Cache-Control", "no-cache" )
                web.header( "Content-Type", "text/html" )
                return response

    class api_issue:
        def GET( self, path, input_variable="queries" ):
            render		= web.template.render(
                TPLPATH, base="layout", globals={'inline': inline, 'session': session} )
            accept		= None
            if path and path.endswith( ".json" ):
                path		= path[:-5]		# clip off ".json"
                accept		= "application/json"

            # Always returns a content-type and response.  If an exception is
            # raised, it should be an appropriate one from the supplied framework to
            # carry a meaningful HTTP status code.  Otherwise, a generic 500 Server
            # Error will be produced.
            content, response	= issue_request(
                render=render, path=path, environ=web.ctx.environ,
                accept=accept, framework=web, logged=logged,
                **{ input_variable: web.input() } )
            web.header( "Cache-Control", "no-cache" )
            web.header( "Content-Type", content )
            return response

        def POST( self, path ):
            # form data posted in web.input(), just like queries
            return self.GET( path, input_variable="posted" )

    class tabular_request_base:
        # Set request = <function returning (content, response)>
        def GET( self, path, input_variable="queries" ):
            # if not logged():
            #     web.seeother( proxy( web.ctx.environ ) + '/login?redirect=' + web.ctx.environ.get( 'PATH_INFO', '' ))
            #     return
            render		= web.template.render(
                TPLPATH, base="layout", globals={'inline': inline, 'session': session} )
            accept		= None
            if path and path.endswith( ".json" ):
                path		= path[:-5]		# clip off ".json"
                accept		= "application/json"

            # Always returns a content-type and response.  If an exception is
            # raised, it should be an appropriate one from the supplied framework to
            # carry a meaningful HTTP status code.  Otherwise, a generic 500 Server
            # Error will be produced.
            request		= self.__class__.__dict__['request']
            log.info( "Tabular API call: {!r}".format( request ))
            content, response	= request(
                render=render, path=path, environ=web.ctx.environ,
                accept=accept, framework=web, logged=logged,
                **{ input_variable: web.input() } )
            web.header( "Cache-Control", "no-cache" )
            web.header( "Content-Type", content )
            return response

        def POST( self, path ):
            # form data posted in web.input(), just like queries
            return self.GET( path, input_variable="posted" )

    class api_licenses( tabular_request_base ):
        request			= licenses_request

    class api_credentials( tabular_request_base ):
        request			= credentials_request

    class api_keypairs( tabular_request_base ):
        request			= keypairs_request

    class StaticAppDir( web.httpserver.StaticApp, object ):
        """Implement our own version of StaticApp and StaticMiddleware so we can return proper caching
        headers, and specify a specific basedir for static file access. Force new-style classes in
        Python2 so super works.  Unfortunately, the Python2 SimpleHTTPRequest implementation baked
        in os.getcwd so we have to transplant a Python2/3 compatible translate_path, too.

        """
        def __init__( self, environ, start_response, directory ):
            super( StaticAppDir, self ).__init__( environ, start_response )
            self.directory	= directory

        def translate_path(self, path):
            """Translate a /-separated PATH to the local filename syntax.

            Components that mean special things to the local file system
            (e.g. drive or directory names) are ignored.  (XXX They should
            probably be diagnosed.)

            """
            # abandon query parameters
            path = path.split('?',1)[0]
            path = path.split('#',1)[0]
            # Don't forget explicit trailing slash when normalizing. Issue17324
            trailing_slash = path.rstrip().endswith('/')
            path = posixpath.normpath(unquote(path))
            words = path.split('/')
            words = filter(None, words)
            path = self.directory  # << D'oh!
            for word in words:
                if os.path.dirname(word) or word in (os.curdir, os.pardir):
                    # Ignore components that are not a simple file/directory name
                    continue
                path = os.path.join(path, word)
            if trailing_slash:
                path += '/'
            return path

    cache_max_age		= 30*24*60*60

    class StaticMiddlewareDir( web.httpserver.StaticMiddleware, object ):
        """WSGI middleware for serving static files from the specified basedir."""
        def __init__( self, app, prefix="/static/", basedir=os.getcwd() ):
            super( StaticMiddlewareDir, self ).__init__( app, prefix=prefix )
            self.basedir	= basedir
            logging.info( "Serving static files out of {}".format( basedir + prefix ))

        def __call__( self, environ, start_response ):
            path 		= environ.get( 'PATH_INFO', '' )
            path 		= self.normpath( path )
            if path.startswith(self.prefix):
                app 		= StaticAppDir( environ, start_response, self.basedir )
                app.send_header( 'Cache-Control', 'public, max-age=%d' % ( cache_max_age ))
                return app
            else:
                return self.app( environ, start_response )

    class LogMiddlewareCF( web.httpserver.LogMiddleware, object ):
        def log( self, status, environ ):
            cf_ip		= environ.get( 'HTTP_CF_CONNECTING_IP' )
            if cf_ip is None:
                cf_ip		= environ.get( 'HTTP_X_FORWARDED_FOR' )
            if cf_ip is not None and ',' in cf_ip:
                # CF appends connecting IP to X_FORWARDED_FOR
                cf_ip		= cf_ip.split( ',' )[-1].strip()
            cf_country		= environ.get( 'HTTP_CF_IPCOUNTRY' )

            #ip,port		= environ.get( 'REMOTE_ADDR' ),environ.get( 'REMOTE_PORT' )
            if cf_ip:
                environ['REMOTE_ADDR'] = cf_ip
            if cf_country:
                environ['REMOTE_PORT'] = cf_country
            return super( LogMiddlewareCF, self ).log( status, environ )

    # Get the required web.py classes from the local namespace.  The iface:port must always passed
    # on argv[1] to use app.run(), so use lower-level web.httpserver.runsimple interface.  This sets
    # up the WSGI middleware chain, prints the address and then invokes
    # httpserver.WSGIserver.start(), which does the bind, and then makes WSGI calls
    app				= web.application( urls, locals() )

    # Sessions
    global session_initializer
    session			= web.session.Session(
        app, web.session.DBStore( db, 'sessions' ), initializer=session_initializer )

    # We can't use the stock runsimple; we have to build up our own chain of WSGI middleware and run
    # its server, in order to get our custom StaticMiddleware/StaticApp to serve static files from
    # the Python module installation directory.
    access			= config.get( 'access' )

    # Log web.py HTTP requests to licensing.access
    class LogStdout( wsgilog.LogStdout ):
        """Implement the missing flush API to avoid warnings"""
        def flush(self):
            pass

    class Log( wsgilog.WsgiLog, object ):
        """Direct log messages to the correct log file, including stdout/stderr.  Because we're running
        a curses textual UI, we don't want stuff being printed to the screen accidentally -- make
        sure it all goes to the log file.

        """
        def __init__( self, application ):
            """Set up logging, and then make sure sys.stderr goes to whereever sys.stdout is now going.  This
            ensures that environ['wsgi.errors'] (which is always set to sys.stderr by web.py) goes
            to the .access log file; this is used to log each incoming HTTP request.

            """
            if access:
                super( Log, self ).__init__(
                    application,
                    logformat	= "%(message)s",
                    log		= True,
                    tohtml	= True,				# Exceptions generate HTML
                    tofile	= True,				# Logging goes to access log file
                    file	= access,
                    interval	= 'd',
                    backups	= 7,
                )
                # toprint does this automatically for sys.stdout; sys.stderr remains unchanged.
                # However, the default LogStdout is missing a required .flush method, so we'll set
                # this up manually instead
                sys.stdout = sys.stderr = LogStdout( self.logger, logging.INFO )
            else:
                super( Log, self ).__init__(
                    application,
                    logformat	= "%(message)s",
                    log		= True,
                    tohtml	= True,				# Exceptions generate HTML
                    tostream	= True,				# Logging goes to stdout
                )

    func			= app.wsgifunc( Log )
    func			= StaticMiddlewareDir( func, "/static/", os.path.dirname( __file__ ))
    func			= LogMiddlewareCF( func )       # web.httpserver.LogMiddleware( app )

    # webpy.server		= web.httpserver.WSGIServer( config['address'], app )

    # This is a CherryPy (cheroot) Server.  We have to intercept .serve(), to print the actually
    # bound web server address (eg. if using a dynamically allocated port).  This will be redirected
    # to the access logfile, unless disabled via --no-access.  Also, this class weirdly captures config, so we can update
    from cheroot import wsgi

    class Server( wsgi.Server, object ):
        def serve( self ):
            sockname		= self.socket.getsockname()
            print( "Web Interface TCP address = {sockname!r}".format( sockname=sockname ))
            sys.stdout.flush()
            config['control']['address'] = sockname
            super( Server, self ).serve()

    # Finally, make the Server available on the function's webpy.server for external access
    webpy.server		= Server( config['address'], func, server_name="localhost" )
    webpy.server.nodelay	= True

    try:
        log.warning( "Web Interface starting" )
        webpy.server.start()
    except (KeyboardInterrupt, SystemExit) as exc:
        logging.warning( "Web Interface Thread uncontrolled shutdown: %s", exc )
    except Exception as exc:
        logging.warning( "Web Interface Thread exception shutdown: %s", exc )
    finally:
        logging.info( "Web Interface Thread stopping..." )
        try:
            webpy.server.stop()
        except Exception as exc:
            logging.warning( "Web Interface Thread stop failure: %s", exc )
        webpy.server		= None
        logging.warning( "Web Interface Thread exiting" )


# To stop the server externally, hit webpy.server.stop
webpy.server			= None


def txtgui( config ):
    """Run curses UI, catching all exceptions.  Returns True on failure."""
    failure			= None
    try:        # Initialize curses
        stdscr			= curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.halfdelay( 1 )
        stdscr.keypad( 1 )

        txt( stdscr, config )               # Enter the Curses mainloop
    except Exception:
        failure			= traceback.format_exc()
    finally:
        config.setdefault( 'control', {} )['done'] = True
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        time.sleep(.25)
    if failure:
        logging.error( "Curses GUI Exception: %s", failure )
        return True
    return False


def ctlloop( beg, cnf ):
    """Execute one loop of the control system"""
    pass


def main( argv=None, **licensing_kwds ):
    """Pass the desired argv (excluding the program name in sys.arg[0]; typically pass argv=None, which
    is equivalent to argv=sys.argv[1:], the default for argparse.  Requires at least one tag to be
    defined.
    """

    ap				= argparse.ArgumentParser(
        description	= "A Crypto Licensing Server",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog		= """\
Implements Ed25519-signed cryptographic licensing web service and API.

Issues license(s) for products and capabilities available to the client, where either

  A) the server has credentials indicating ownership of the Licenses, and hence
     authority to sub-license them, or

  B) the License itself grants authority to be sub-licensed to any Agent
     asking for a License

Produces invoices for each transaction

Performance benefits greatly from installation of (optional) ed25519ll package:

    python3 -m pip install ed25519ll
"""
    )
    ap.add_argument( '-v', '--verbose', action="count",
                     default=0,
                     help="Display logging information." )
    ap.add_argument( '-q', '--quiet', action="count",
                     default=0,
                     help="Reduce logging output." )
    ap.add_argument( '-w', '--web',
                     default="0.0.0.0:8000",
                     help='enable web server on interface (default: 0.0.0.0:8000)' )
    ap.add_argument( '--no-web', dest='web',
                     action="store_false",
                     help='Disable web interface and access log file (default: False)' )
    ap.add_argument( '--access',
                     default=ACCFILE,
                     help="Log all web server access to log file (default: {ACCFILE}".format(
                         ACCFILE=ACCFILE ))
    ap.add_argument( '--no-access', dest='access',
                     const=None, action="store_const",
                     help='Disable web server access log file, including stdout/stderr redirection' )
    ap.add_argument( '--no-gui', dest='gui',
                     default=True, action="store_false",
                     help='Disable Curses GUI interface (default: False)' )
    ap.add_argument( '-c', '--config',
                     action='append',
                     help="Add another (higher priority) config file path." )
    ap.add_argument( '-l', '--log',
                     default=None,
                     help="Log file, if desired (default, if text gui: {LOGFILE})".format( LOGFILE=LOGFILE ))
    ap.add_argument( '--profile',
                     default=None,
                     help="Profile to stderr (only, if '-' specified), optionally saving data to a file (default: None)" )
    ap.add_argument( '--client',
                     default=None,
                     help="This {DISTRIBUTION}server's client licensee's company name".format(
                         DISTRIBUTION=licensing.DISTRIBUTION ))
    ap.add_argument( '--domain',
                     default=None,
                     help="This {DISTRIBUTION} server's client licensee's domain; can be used to get public key via DKIM".format(
                         DISTRIBUTION=licensing.DISTRIBUTION ))
    ap.add_argument( '--product',
                     default=licensing.PRODUCT_SERVER,
                     help="This {DISTRIBUTION} server's client licensee's product name (if any; default: {PRODUCT})".format(
                         DISTRIBUTION=licensing.DISTRIBUTION, PRODUCT=licensing.PRODUCT_SERVER ))
    ap.add_argument( '-U', '--username',
                     default=None,
                     help="{DISTRIBUTION} Agent credentials username; likely an email address ('-' to read from input)".format(
                         DISTRIBUTION=licensing.DISTRIBUTION ))
    ap.add_argument( '-P', '--password',
                     default=None,
                     help="{DISTRIBUTION} Agent credentials password ('-' to read from input)".format(
                         DISTRIBUTION=licensing.DISTRIBUTION ))
    ap.add_argument( '-R', '--register', action='store_true',
                     default=False,
                     help="If necessary, create and save a new client Keypair" )
    ap.add_argument( '-A', '--acquire', action='store_true',
                     default=False,
                     help="If no Agent Keypair or License is available, attempt to create and/or obtain one; provide --username/--password to encrypt"
                     ", then use {ENVUSERNAME}/{ENVPASSWORD} environment vars to decrypt".format(
                         ENVUSERNAME=licensing.ENVUSERNAME, ENVPASSWORD=licensing.ENVPASSWORD
                     ))
    args = ap.parse_args( argv )

    # Set up logging; also, handle the degenerate case where logging has *already* been set up (and
    # basicConfig is a NO-OP), by (also) setting the logging level.
    log_cfg['level']		= log_level( args.verbose - args.quiet )
    if args.log or args.gui:
        log_cfg['filename']	= args.log or LOGFILE
    logging.basicConfig( **log_cfg )
    if args.verbose or args.quiet:
        logging.getLogger().setLevel( log_cfg['level'] )

    profiler			= None
    profiler_limit		= 25
    if args.profile:
        import pstats
        try:
            from mtprof import Profile
        except ImportError:
            from cProfile import Profile

        profiler		= Profile()
        profiler.enable()

    # Any configuration files and licensing.load/load_keys should inspect these extra dirs
    global config_extras
    config_extras	       += args.config or []
    log.info( "Licensing configuration paths: {}".format( ', '.join( config_paths( '<file>', extra=config_extras ))))

    # Get some details about the Ed25519 version we're using, and suppress some nagging about
    # letting it generate random seeds.
    warnings.simplefilter('ignore')  # We know about handling Ed25519 random seeds...

    log.info( "Ed25519 Version: {} / {} / {}".format(
        getattr( licensing.ed25519, '__version__', None ), licensing.ed25519.__package__, licensing.ed25519.__path__ ))

    # Load our Crypto Licensing server Agent's .crypto-key* and .crypto-lic* files.
    #
    # This is the Agent's Keypair that will be assigned a License to *run* a Crypto Licensing
    # server, on a particular Machine ID.
    #
    # This is *not* an authority to sign and *issue* Crypto Licensing server licenses.  That Keypair
    # is different, and is loaded *into* the Crypto Licensing server, and is used to sign new
    # Licenses that are issued to other parties.
    #
    # If necessary, we'll ask for a License to be issued by Dominion R&D Corp, to this Agent, for
    # authorization to run on this machine.  This License will grant us the capability to issue
    # sub-Licenses for a certain number of "master" Licenses (Licenses that do not have a
    # pre-defined client baked into them, and thus could be sub-licensed to any client).  The Crypto
    # Licensing server is expected to issue Licenses that comply with the rules established by the
    # "master" License; if it is found that one is issuing invalid Licenses (ie. the "master" grants
    # 10 machines, but more than 10 sub-Licenses have been issued), then its license will be revoked
    # by blacklisting its public key.
    #
    # The secrets required to decrypt the licensing.KeypairEncrypted are expected to be in
    # environment variables (specify '-' to read from input):
    #
    #     CRYPTO_LIC_USERNAME  # or --username
    #     CRYPTO_LIC_PASSWORD  # or --password (unsafe)
    #
    # Then, find and load the Keypair and License --product (split on spaces), joined by '-'):
    #
    #     crypto-licensing-server.crypto-{keypair,license}
    #
    basename			= '-'.join( [ segment.lower() for segment in args.product.split() ] )
    log.log( logging.DETAIL, "Loading Agent Ed25519 Keypair from {}...".format( basename ))
    # Load Agent Keypair, if any, using any credentials supplied in the environment
    cl_username			= args.username or os.getenv( licensing.ENVUSERNAME )
    cl_password			= args.password or os.getenv( licensing.ENVPASSWORD )
    if args.password and args.password != '-':
        log.warning( "It is recommended to not use '-P|--password ...'; specify '-' to read from input" )

    # Cycle through the available Agent ID keys, and any License(s) for Dominion R&D's Crypto
    # Licensing.  To create an unencrypted Keypair, no --username/--password may be specified.
    # Otherwise, we must block here awaiting input.
    username			= input_secure( "Enter {} username: ".format( basename )) if cl_username == '-' else cl_username
    password			= input_secure( "Enter {} password: ".format( basename )) if cl_password == '-' else cl_password
    userpass_input		= cl_username == '-' or cl_password == '-'
    try:
        # We're looking for a License authored by Dominion R&D Corp.  This might be encapsulated as
        # one of the dependencies of the License we find (eg. if Dominion issues a License to some
        # company, which includes the ability to run a crypto-licensing server), but we'll validate
        # that the Grant was issued by Dominion R&D Corp.  For example, Dominion issues a License to
        # awesome-inc.com to sub-License crypto-licensing servers.  They, in turn, issue a License
        # to Лайка.ru to run a crypto-licensing server, and help them set it up.  When
        # http://crypto-licensing.xn--80aa0aec.ru/ (crypto-licensing.Лайка.ru) issues a License for
        # their software, part of the fees are paid to awesome-inc.com and some to dominionrnd.com.
        # The final software installation uses crypto-licensing's authorized() function, which checks
        # that each successive License's dependencies are correctly signed, and carries the original
        # 'crypto-licensing' Grant through to the recipient.
        dominion		= licensing.Agent(
            name	= licensing.COMPANY,
            domain	= licensing.DOMAIN,
            product	= licensing.PRODUCT,
            pubkey	= licensing.PUBKEY,
        )
        server			= None
        if args.product and args.domain:
            server		= licensing.Agent(
                name	= args.client,
                domain	= args.domain,
                product	= args.product,
            )

        authorization		= licensing.authorized(
            author	= dominion,
            client	= server,
            basename	= basename,
            username	= username,
            password	= password,
            registering	= args.register,        # Issue an Agent ID if none found?
            acquiring	= args.acquire,		# Acquire a License if none found?
            extra	= config_extras,        # including any locally defined config dirs
        )

        loaded			= []
        try:
            key,lic		= next( authorization )
            while True:
                if key is None or lic is None:
                    what		= "No License found for Agent ID {}".format(
                        licensing.into_b64( key.vk )) if key else "No Agent ID Keypair found"
                    if userpass_input:
                        what       += "; enter credentials"
                        if password != "-":
                            what   += " (leave blank to register w/ {}: {}".format(
                                username or "(no username)", '*' * len( password or '' ) or "(no password)" )
                    log.warning( what )
                    # No Agent ID/License loaded; username/password may be incorrect.  If none provided,
                    # then authorization may go on to register w/ the last-entered username/password.
                    # Either username or password may be updated, if desired.  Usually, credential input
                    # forces you to re-enter something you know to be correct; this loop does not.
                    # Failing to enter both credentials indicates satisfaction -- goes on to register a
                    # new Agent ID w/ credentials, if so.
                    userpass_updated = False
                    if cl_username == '-':
                        username_update	= input_secure( "Enter {} username (leave empty for no change): ".format( basename ))
                        userpass_updated |= bool( username_update )
                        if username_update:
                            username	= username_update
                    if cl_password == '-':
                        password_update	= input_secure( "Enter {} password (leave empty for no change): ".format( basename ))
                        userpass_updated |= bool( password_update )
                        if password_update:
                            password	= password_update
                    if userpass_updated:
                        log.detail( "Supplying new credentials for {}: {}".format(
                            username or "(no username)", '*' * len( password or '' ) or "(no password)" ))
                        key,lic	= authorization.send( (username,password) )
                        continue
                    # No Keypair (or perhaps a Keypair, but no License) found; credentials NOT updated.  So,
                    # the user has had the opportunity to enter a password (if either username/password was -),
                    # but has declined.  We're done.
                    log.detail( "No new credential(s) for {}: {}{}".format(
                        username or "(no username)", '*' * len( password or '' ) or "(no password)",
                        " (attempting to register new Agent ID)" if args.register else " (authorization failed)" ))
                    break
                else:
                    # A Keypair and License was found; remember it
                    loaded.append( (key,lic) )
                key,lic		= next( authorization )
        except StopIteration:
            log.detail( "Completed licensing.authorized w/ {} Keypair/Licenses found".format( len(loaded) ))

        # Collect up all the License grants; there may be more than one, if the user has purchased
        # multiple Licenses at different times.  Ensures we only include a specific License once.
        grants			= licensing.Grant()
        once			= set()
        for key,lic in loaded:
            grants_lic		= lic.grants( once=once )
            log.normal( "Located Agent Ed25519 Keypair {pubkey} w/ {product} License (from {_from}){extra}".format(
                pubkey	= licensing.into_b64( key.vk ),
                product	= lic and lic.license.author.product or "End-User",
                _from	= "from {}".format( lic._from ) if lic._from else "locally issued",
                extra	= (( " w/ grants: {}".format( grants_lic ) if log.isEnabledFor( logging.DEBUG ) else "" )
                           + ( " merging w/ grants: {}".format( grants ) if log.isEnabledFor( logging.TRACE ) else "" )),
            ))
            grants	       |= grants_lic

        # And, finally: ascertain whether we have a Grant to run Dominion R&D Corp's Crypto Licensing Server!
        assert dominion.servicekey in grants, \
            "Unable to find {}'s product {!r} service key {!r} in License Grants {}".format(
                dominion.name, dominion.product, dominion.servicekey, grants )

    except Exception as exc:
        log.error( "Failed loading Agent Keypair and/or License: {exc}".format(
            exc=''.join( traceback.format_exception( *sys.exc_info() )) if log.isEnabledFor( logging.TRACE ) else exc ))
        with open( os.path.join( os.path.dirname( __file__ ), 'static', 'txt', 'CL-KEYPAIR-MISSING.txt' ), 'r' ) as f:
            print( f.read().format(
                DISTRIBUTION	= licensing.DISTRIBUTION,
                KEYPATTERN	= licensing.KEYPATTERN,
                LICENSE_OPTION	= '--license',
            ), file=sys.stderr )
        sys.exit( 1 )

    # Set up the global db, etc.
    db_setup()

    # Summarize the initial Licenses and Keypairs available; these are re-obtained in real-time by the UIs, above
    stored			= db.select( 'licenses' )
    stored			= list( stored )
    for sig, lic in licenses( confirm=False, stored=stored ):
        log.info( "{s:<64}: {lic}".format(
            s=licensing.into_b64( sig ), lic=str( lic ) ))

    for name, keypair, (username, password) in keypairs():
        try:
            vk			= licensing.into_b64( keypair.into_keypair( username=username, password=password ).vk )
        except Exception as exc:
            vk			= str( exc )
        log.info( "{n:<20}: {vk} w/ {u:>20} / {p}".format(
            n=name, vk=vk, u=username, p='*' * len( password )))

    class daemon( threading.Thread ):
        """Every daemon must have a config['control']; sets its done = True to stop."""
        def __init__( self, config=None, **kwds ):
            super( daemon, self ).__init__( **kwds )
            self.daemon		= True
            self.config		= config or {}
            self.config.setdefault( 'control', {} ).setdefault( 'done', False )

        def stop( self ):
            logging.info( "Stopping %s Thread", self.name )
            self.config['control']['done'] = True

        def join( self, *args, **kwds ):
            self.stop()
            logging.info( "Joining %s Thread...", self.name )
            super( daemon, self ).join( *args, **kwds )
            logging.info( "Joined %s Thread", self.name )

    class txtthread( daemon ):
        def run( self ):
            try:
                while not self.config.get( 'control', {} ).get( 'done' ):
                    if txtgui( self.config ):
                        # Textual GUI has failed!  Don't restart.
                        break
            except Exception as exc:
                logging.error("Text GUI failed: %s\n%s", exc, traceback.format_exc())
            finally:
                logging.warning( "Text GUI exiting" )
                self.stop()

    class webthread( daemon ):
        def run( self ):
            try:
                webpy( self.config )
            except Exception as exc:
                logging.error( "Web GUI failed: %s\n%s", exc, traceback.format_exc() )
            finally:
                self.stop()
                logging.warning( "Web GUI exiting" )

        def stop( self ):
            """In addition to the normal stop procedure (perhaps signaling other Threads via a shared
            control dict), webpy.server has its own stop mechanism.

            """
            super( webthread, self ).stop()
            if webpy.server:
                logging.info( "Web GUI stopping..." )
                webpy.server.stop()
                logging.info( "Web GUI stopped" )

    class ctlthread( daemon ):
        def run( self ):
            try:
                while not self.config.get( 'control', {} ).get( 'done' ):
                    beg		= timer()
                    ctlloop( beg, self.config )
                    dur		= timer() - beg
                    cyc		= self.config.get( 'cycle', 1.0 )
                    if dur < cyc:
                        time.sleep( cyc - dur )
            except Exception as exc:
                logging.error( "Control system failed: %s\n%s", exc, traceback.format_exc() )
            finally:
                logging.warning( "Control system exiting" )
                self.stop()

    # Some of these threads may need to redirect sys.stdout/stderr; save and restore
    sys_stream_save		= sys.stdout, sys.stderr
    threads			= []

    # When using threading, the licensing_kwds dict is shared with the server, so don't interfere
    # with the structure while sharing the server.control dict.  Other application-specific kwds may
    # be removed safely.
    server			= licensing_kwds.get( 'server', {} )
    control			= server.get( 'control', {} )
    try:
        # Start the control system Thread.
        ctlcnf			= licensing_kwds.pop( 'ctl', {} )
        ctlcnf.setdefault( 'cycle', 1.0 )
        ctlcnf.setdefault( 'control', control )
        ctlthr			= ctlthread( config=ctlcnf, name='control' )
        ctlthr.start()
        threads.append( ctlthr )

        # Start the Curses Text GUI (if desired)
        txtcnf			= licensing_kwds.pop( 'txt', {} )
        txtcnf.setdefault( 'control', control )
        txtcnf.setdefault( 'title', 'Licensing' )
        # By default, accesses the local functions yielding the stored licenses, credentials and keypairs
        txtcnf.setdefault( 'licenses',		licenses )
        txtcnf.setdefault( 'credentials',	credentials )
        txtcnf.setdefault( 'keypairs',		keypairs )
        txtthr			= None
        if args.gui:
            txtthr		= txtthread( txtcnf, name='curses' )
            txtthr.start()
            threads.append( txtthr )

        # Start the web UI (if desired)
        webthr			= None
        if args.web:
            # Deduce interface:port to bind, and correct types
            address		= args.web.split( ':' )
            assert 1 <= len( address ) <= 2, "Web address must be in the form <interface>:<port>"
            address		= ( str( address[0] ),
                                    int( address[1] ) if len( address ) > 1 else 8000 )

            # Command-line parameters in argv are overridden by specific configurations
            # passed in licensing_kwds['web']
            webcnf		= licensing_kwds.pop( 'web', {} )
            webcnf.setdefault( 'control', control )
            webcnf.setdefault( 'address', address )
            webcnf.setdefault( 'access', args.access )

            # If all sys.stdout/stderr should got to the web server's access log file, (the
            # default), then set it here.  If not (eg. we want to be able to harvest the actual
            # dynamic IP address:port of the bound web server socket), then pass Falsey for access.
            webthr		= webthread( webcnf,  name='web' )
            webthr.start()
            threads.append( webthr )

        # Just wait for any thread (web or text GUI, control) to finish
        while not shutdown_signalled and all( t.is_alive() for t in threads ):
            signal_service()
            time.sleep( .1 )
    except Exception:
        logging.error( "Main thread Exception: %s", traceback.format_exc() )
    finally:
        # Either the Web or the Curses GUI completed, or something blew up.  Shut all the
        # threads down, restore sys.stdout/stderr and save state.
        logging.warning( "Cleaning up threads" )
        for t in threads:
            t.join( timeout=1.0 )
        sys.stdout, sys.stderr	= sys_stream_save

        logging.info( "Saving state..." )
        db_state_save()

        if args.profile:
            profiler.disable()
            if args.profile != '-':  # optionally dump stats to a filename
                profiler.dump_stats( args.profile )
            prof		= pstats.Stats( profiler, stream=sys.stderr )
            print( "\n\nTIME:", file=sys.stderr )
            prof.sort_stats(  'time' ).print_stats( profiler_limit )

            print( "\n\nCUMULATIVE:", file=sys.stderr )
            prof.sort_stats(  'cumulative' ).print_stats( profiler_limit )
