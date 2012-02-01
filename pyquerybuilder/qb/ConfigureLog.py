#!/usr/bin/env python
# $Id: ConfigureLog.py,v 1.1 2007/03/22 15:15:04 valya Exp $
"""
Load the logging configuration file.
"""
__author__ = "Andrew J. Dolgert <ajd27@cornell.edu>"
__revision__ = "$Revision: 1.1 $"

import logging
import logging.config
from pyquerybuilder.tools.config import readconfig
import imp
import os

def configurelog():
    """Log configuration"""
    logfile = None
    try:
        config = readconfig()
        logfile = config['logfile']['logconfig']
    except:
        basedir = imp.find_module('pyquerybuilder')[1]
        logfile = os.path.join(basedir, 'config/logging.conf')

    logging.config.fileConfig(logfile)

    #create logger
    logger = logging.getLogger("ConstructQuery")
    logger.setLevel(logging.DEBUG)
