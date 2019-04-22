# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=keyword-arg-before-vararg, arguments-differ

import os
import socket

import requests
from twisted.internet import threads
from twisted.internet.defer import ensureDeferred

from platformio import util


class AsyncSession(requests.Session):

    def __init__(self, n=None, *args, **kwargs):
        if n:
            from twisted.internet import reactor
            pool = reactor.getThreadPool()
            pool.adjustPoolsize(0, n)

        super(AsyncSession, self).__init__(*args, **kwargs)

    def request(self, *args, **kwargs):
        func = super(AsyncSession, self).request
        return threads.deferToThread(func, *args, **kwargs)

    def wrap(self, *args, **kwargs):  # pylint: disable=no-self-use
        return ensureDeferred(*args, **kwargs)


@util.memoized(expire=5000)
def requests_session():
    return AsyncSession(n=5)


@util.memoized()
def get_core_fullpath():
    return util.where_is_program(
        "platformio" + (".exe" if "windows" in util.get_systype() else ""))


@util.memoized(expire=10000)
def is_twitter_blocked():
    ip = "104.244.42.1"
    timeout = 2
    try:
        if os.getenv("HTTP_PROXY", os.getenv("HTTPS_PROXY")):
            requests.get(
                "http://%s" % ip, allow_redirects=False, timeout=timeout)
        else:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((ip, 80))
        return False
    except:  # pylint: disable=bare-except
        pass
    return True