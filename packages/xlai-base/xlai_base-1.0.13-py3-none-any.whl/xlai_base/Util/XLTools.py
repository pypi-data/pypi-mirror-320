# coding=utf8
import re
import hashlib
import json
import torch
import pickle
import numpy
import struct


def to_readable_buffer(data):
    if isinstance(data, (bytes, bytearray, memoryview)):
        return data
    elif isinstance(data, str):
        return data.encode('utf-8')
    elif isinstance(data, int):
        return data.to_bytes((data.bit_length() + 7) // 8, byteorder='big')
    elif isinstance(data, float):
        return struct.pack('!f', data)
    elif isinstance(data, list):
        return b''.join(to_readable_buffer(item) for item in data)
    elif isinstance(data, dict):
        return json.dumps(data).encode('utf-8')
    elif isinstance(data, numpy.ndarray):
        return data.tobytes()
    elif isinstance(data, torch.Tensor):
        return to_readable_buffer(data.detach().cpu().numpy())
    else:
        return pickle.dumps(data)


def create_md5_hash(data):
    input_sha256 = hashlib.sha256()
    input_sha256.update(to_readable_buffer(data))
    data_hash = input_sha256.hexdigest()
    return data_hash


_find_unsafe = re.compile(r'[^\w@%+=:,./-]', re.ASCII).search


def quote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"


def request_to_curl(request, compressed=False, verify=True):
    """
    Returns string with curl command by provided request object

    Parameters
    ----------
    compressed : bool
        If `True` then `--compressed` argument will be added to result
        :param verify:
        :param compressed:
        :param request:
    """
    parts = [
        ('curl', None),
        ('-X', request.method),
    ]

    for k, v in sorted(request.headers.items()):
        parts += [('-H', '{0}: {1}'.format(k, v))]

    if request.body:
        body = request.body
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        parts += [('-d', body)]

    if compressed:
        parts += [('--compressed', None)]

    if not verify:
        parts += [('--insecure', None)]

    parts += [(None, request.url)]

    flat_parts = []
    for k, v in parts:
        if k:
            flat_parts.append(quote(k))
        if v:
            flat_parts.append(quote(v))

    return ' '.join(flat_parts)
