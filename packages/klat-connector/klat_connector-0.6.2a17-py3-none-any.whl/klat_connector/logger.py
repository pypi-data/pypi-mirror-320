# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2025 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending
import logging
import os

fmt = '%(asctime)s - %(levelname)-8s - %(name)s:%(module)s:%(funcName)s:%(lineno)d - %(message)s'
levels_dict = {'DEBUG': logging.DEBUG,
               'INFO': logging.INFO,
               'WARNING': logging.WARNING,
               'ERROR': logging.ERROR,
               'CRITICAL': logging.CRITICAL}
logging.basicConfig(level=levels_dict.get(os.environ.get('LOG_LEVEL', 'DEBUG').upper(), logging.DEBUG),
                    format=fmt, datefmt='%Y-%m-%d:%H:%M:%S')
logging.getLogger("socketio.client").setLevel(logging.WARNING)
logging.getLogger("engineio.client").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
LOG = logging.getLogger("klat_connector")
