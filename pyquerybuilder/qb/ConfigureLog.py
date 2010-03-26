#!/usr/bin/env python
# $Id: ConfigureLog.py,v 1.1 2007/03/22 15:15:04 valya Exp $
"""
Load the logging configuration file.
"""
__author__ = "Andrew J. Dolgert <ajd27@cornell.edu>"
__revision__ = "$Revision: 1.1 $"

import logging
import logging.config

def configurelog():
    """Log configuration"""
    logging.config.fileConfig("logging.conf")
    
    #create logger
    logger = logging.getLogger("ConstructQuery")
