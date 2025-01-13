# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %             Service Module - Classes and Functions           %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Main entry point of STMLab package
 
@note: STMLab command line interface
Created on 21.10.2024

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-SY,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package stmlab.service
# Module containing all command line options.
## @author 
# Marc Garbade
## @date
# 21.10.2024
## @par Notes/Changes
# - Added documentation  // mg 21.10.2024

import os, sys

from stmlab import __version__, STMLabPath

from PyCODAC.API.__exe__ import main

# Top-level modifications of base application
__settings__ = {"workers":1, "api_version":__version__} 

# Verify that default documentation can be reached in development mode
default_documentation = os.path.abspath(os.path.join(STMLabPath,"..","..","doc","stmlab"))
if os.path.exists(default_documentation):
    __settings__.update({ "static": os.path.abspath(os.path.join(default_documentation,"html","stmlab.html")),
                                         "icon":os.path.abspath(os.path.join(default_documentation,"pics","stm_lab_logo_gitlab.jpg"))})

if __name__ == '__main__':
    # Load local settings
    settings = __settings__
    # Execute application
    main(**settings); sys.exit()