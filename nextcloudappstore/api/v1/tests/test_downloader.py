"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import http.server
import ipaddress
import shutil
import socket
import tempfile
import threading

from django.test import SimpleTestCase

from nextcloudappstore.api.v1.release.downloader import AppReleaseDownloader
from nextcloudappstore.api.v1.release.parser import UnsupportedAppArchiveException


class _SilentHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"x" * 16
        self.send_response(200)
        self.send_header("Content-Type", "application/gzip")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def _get_local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return None
    finally:
        sock.close()


class AppReleaseDownloaderTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.httpd = http.server.HTTPServer(("0.0.0.0", 0), _SilentHandler)
        cls.port = cls.httpd.server_address[1]
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.local_ip = _get_local_ip()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.server_thread.join()
        super().tearDownClass()

    def setUp(self):
        self.downloader = AppReleaseDownloader()
        self.target_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.target_dir, ignore_errors=True)

    def _assert_blocked(self, url):
        with self.assertRaises(UnsupportedAppArchiveException):
            self.downloader.get_archive(url, target_directory=self.target_dir, timeout=10)

    def test_loopback_ipv4_blocked(self):
        self._assert_blocked(f"http://127.0.0.1:{self.port}/app.tar.gz")

    def test_loopback_hostname_blocked(self):
        self._assert_blocked(f"http://localhost:{self.port}/app.tar.gz")

    def test_machine_local_ip_blocked(self):
        if not self.local_ip:
            self.skipTest("could not discover a local IP address")
        ip = ipaddress.ip_address(self.local_ip)
        if not ip.is_private:
            self.skipTest(f"discovered IP {self.local_ip} is not private")
        self._assert_blocked(f"http://{self.local_ip}:{self.port}/app.tar.gz")

    def test_private_ip_range_192_168_blocked(self):
        self._assert_blocked("http://192.168.1.1:1/app.tar.gz")

    def test_private_ip_range_10_blocked(self):
        self._assert_blocked("http://10.0.0.1:1/app.tar.gz")

    def test_private_ip_range_172_16_blocked(self):
        self._assert_blocked("http://172.16.0.1:1/app.tar.gz")
