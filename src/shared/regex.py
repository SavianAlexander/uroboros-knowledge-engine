"""
Shared pre-compiled regex patterns for parsing and text processing.
"""

import re

RE_NEAR_SYNTAX = re.compile(r'NEAR/(\d+)', re.IGNORECASE)
RE_TOKEN_SPLIT = re.compile(r'[^\w]+', re.UNICODE)
RE_SIZE_OP = re.compile(r'size:(>|<|>=|<=)?(\d+)([kmg]b?)?', re.IGNORECASE)
RE_FTS_CLEAN = re.compile(r'[^\w\s]', re.UNICODE)
RE_WIKILINKS = re.compile(r'\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]')
