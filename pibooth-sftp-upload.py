#!/usr/bin/env python

import os
import paramiko
import pibooth
from pibooth.utils import LOGGER

__version__ = "1.0.0"

SECTION='SFTP'

@pibooth.hookimpl
def pibooth_configure(cfg):
    cfg.add_option(SECTION,'server','',
        "SFTP server to upload processed files to")
    cfg.add_option(SECTION,'port',22,
        "Port that SFTP server is listening on")
    cfg.add_option(SECTION,'username','',
        "Username for SFTP server")
    cfg.add_option(SECTION,'password','',
        "Password for SFTP server")
    cfg.add_option(SECTION,'upload_path','',
        "Path on SFTP server to upload files to")

@pibooth.hookimpl
def pibooth_startup(cfg, app):
    if not cfg.get(SECTION, 'server') or not cfg.get(SECTION, 'username') or not cfg.get(SECTION,'upload_path'):
        LOGGER.debug(f'No credentials for SFTP server defined in {SECTION}, deactivating upload')
    else:
        LOGGER.info('Initializing SFTP server connection')
        app.transport = paramiko.Transport((cfg.get(SECTION,'server'), cfg.getint(SECTION,'port')))
        app.transport.connect(username = cfg.get(SECTION,'username'), password = cfg.get(SECTION,'password'))
        app.sftp = paramiko.SFTPClient.from_transport(app.transport)

@pibooth.hookimpl
def state_processing_exit(cfg, app):
    if hasattr(app, 'sftp'): 
        upload_dir = cfg.get(SECTION,'upload_path')
        name = os.path.basename(app.previous_picture_file)   
        server_path = os.path.join(upload_dir,name)
        LOGGER.info(f"Uploading {name} to {cfg.get(SECTION,'server')}:{upload_dir}")
        app.sftp.put(app.previous_picture_file, server_path)

@pibooth.hookimpl
def pibooth_cleanup(app):
    if hasattr(app, 'sftp'):
        app.sftp.close()
    if hasattr(app, 'transport'):
        app.transport.close()