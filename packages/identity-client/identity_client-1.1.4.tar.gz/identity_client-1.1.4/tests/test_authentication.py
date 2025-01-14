import os
import unittest

import django
from django.conf import settings
from django.http import HttpRequest

django.setup()

from django.test import TestCase as DjangoTestCase

from lxml.etree import HTML
from urllib.parse import urlparse, parse_qs
import requests


running_on_CI = os.environ.get("CI") == "true"


class GetTokensTestCase(DjangoTestCase):
    @unittest.skipUnless(running_on_CI, "only runs on CI")
    def test_end_to_end(self):
        login_session = requests.Session()
        login_html = HTML(
            login_session.get(f"{settings.IDENTITY_HOST}/auth/login/").content
        )
        data = {
            e.attrib["name"]: e.attrib["value"]
            for e in login_html.xpath("//input[@type='hidden'][@value]")
        }
        data.update({"username": "test@example.com", "password": "5XpeGLwUmUwZwwy"})
        login_session.post(
            f"{settings.IDENTITY_HOST}/auth/login/", data=data, allow_redirects=False
        )

        auth_url = f"{settings.IDENTITY_HOST}/o/authorize/?state=random_state_string&client_id={settings.IDENTITY_CLIENT_ID}&response_type=code"
        auth_html = HTML(login_session.get(auth_url).content)
        data = {
            e.attrib["name"]: e.attrib.get("value", "")
            for e in auth_html.xpath("//input[@type='hidden']")
        }
        data["allow"] = "authorize"
        code = parse_qs(
            urlparse(
                login_session.post(auth_url, data=data, allow_redirects=False).headers[
                    "Location"
                ]
            ).query
        )["code"][0]
        self.assertEqual(
            self.client.get(
                "/auth/login/", {"code": code, "state": "http://localhost/"}
            ).status_code,
            302,
        )
        self.assertEqual(self.client.session["email"], "test@example.com")

        # fetch user api key from Identity service
        api_key = login_session.get(f"{settings.IDENTITY_HOST}/auth/whoami/").json()[
            "api_key"
        ]

        self.assertEqual(self.client.get("/ping/").status_code, 403)
        self.assertEqual(
            self.client.get("/ping/", HTTP_X_USER_API_KEY=api_key).status_code, 200
        )
