"""
Shared pre-compiled regex patterns for parsing and text processing.
"""

import re

RE_NEAR_SYNTAX = re.compile(r'NEAR/(\d+)', re.IGNORECASE)
RE_TOKEN_SPLIT = re.compile(r'[^\w]+', re.UNICODE)
RE_SIZE_OP = re.compile(r'size:(>|<|>=|<=)?(\d+)([kmg]b?)?', re.IGNORECASE)
RE_FTS_CLEAN = re.compile(r'[^\w\s]', re.UNICODE)
RE_WIKILINKS = re.compile(r'\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]')
URL_PATTERN = re.compile(r'https?://')
EMAIL_PATTERN = re.compile(r'[\w\.-]+@[\w\.-]+')
DATE_PATTERN = re.compile(r'\d{4}-\d{2}-\d{2}')
IP_PATTERN = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
MAC_PATTERN = re.compile(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})')
