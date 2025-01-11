import json
import logging
import idna
import requests
from certbot import errors
from certbot.plugins import dns_common

try:
    import certbot.compat.os as os
except ImportError:
    import os

logger = logging.getLogger(__name__)

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Buddy

    This plugin enables usage of Buddy rest API to complete ``dns-01`` challenges."""

    description = "Automates dns-01 challenges using Buddy internal API"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = ""
        self.token = ""
        self.machine = ""
        self.workspace_id = ""
        self.tunnel_id = ""
        self.domain = ""

    @classmethod
    def add_parser_arguments(cls, add, **kwargs):
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds=30
        )

    def more_info(self):
        return self.description

    def _setup_credentials(self):
        host = os.getenv("BUDDY_HOST")
        token = os.getenv("BUDDY_TOKEN")
        machine = os.getenv("BUDDY_MACHINE")
        workspace_id = os.getenv("BUDDY_WORKSPACE_ID")
        tunnel_id = os.getenv("BUDDY_TUNNEL_ID")
        domain = os.getenv("BUDDY_DOMAIN")
        if host is None:
            raise errors.PluginError("host not defined")
        if token is None:
            raise errors.PluginError("token not defined")
        if machine is None:
            raise errors.PluginError("machine not defined")
        if workspace_id is None:
            raise errors.PluginError("workspace_id not defined")
        if tunnel_id is None:
            raise errors.PluginError("tunnel_id not defined")
        if domain is None:
            raise errors.PluginError("domain not defined")
        self.host = host
        self.token = token
        self.machine = machine
        self.workspace_id = workspace_id
        self.tunnel_id = tunnel_id
        self.domain = domain

    def _perform(self, domain, validation_name, validation):
        decoded_domain = idna.decode(domain)
        if decoded_domain != self.domain:
            raise errors.PluginError("wrong domain")
        subdomain = rreplace(validation_name, "." + domain, "", 1)
        try:
            self._api_client().add_txt_record(subdomain, validation)
        except ValueError as err:
            raise errors.PluginError("Cannot add txt record: {err}".format(err=err))

    def _cleanup(self, domain, validation_name, validation):
        decoded_domain = idna.decode(domain)
        if decoded_domain != self.domain:
            raise errors.PluginError("wrong domain")
        subdomain = rreplace(validation_name, "." + domain, "", 1)
        try:
            self._api_client().del_txt_record(subdomain, validation)
        except ValueError as err:
            raise errors.PluginError("Cannot remove txt record: {err}".format(err=err))

    def _api_client(self):
        return _ApiClient(self.host, self.token, self.machine, self.workspace_id, self.tunnel_id, self.domain)


class _ApiClient:
    def __init__(self, host, token, machine, workspace_id, tunnel_id, domain):
        """Initialize class managing a domain within Buddy API

        :param str host: API host
        :param str token: token
        :param str machine: machine
        :param str workspace_id: workspace ID
        :param str tunnel_id: tunnel ID
        :param str domain: domain
        """
        self.host = host
        self.token = token
        self.machine = machine
        self.workspace_id = workspace_id
        self.tunnel_id = tunnel_id
        self.domain = domain
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def _post_request(self, url, payload):
        """Perform a POST request to Buddy API
        :param url: relative URL
        :param payload: request body"""
        url = self.host + url
        with self.session.post(url, json=payload, verify=False) as res:
            try:
                result = res.json()
            except json.decoder.JSONDecodeError:
                raise errors.PluginError("no JSON in API response")
            if res.status_code == requests.codes.ok:
                return result
            if result["errors"]:
                raise errors.PluginError(result["errors"][0]["message"])
            raise errors.PluginError("something went wrong")

    def add_txt_record(self, subdomain, value, ttl=300):
        """Add a TXT record to a domain
        :param str subdomain: record key in zone
        :param str value: value of record
        :param int ttl: optional ttl of record"""
        # foo.bar _acme-challenge.foo.bar MIFwJwRzJuLEknEfCY2PQwhzE-yf1WIisPFjCWAlKEs
        self._post_request("/tunnel/dns/create", {
            "token": self.token,
            "machine": self.machine,
            "workspaceId": self.workspace_id,
            "tunnelId": self.tunnel_id,
            "domain": self.domain,
            "subdomain": subdomain,
            "append": True,
            "type": "TXT",
            "ttl": ttl,
            "value": value
        })

    def del_txt_record(self, subdomain, value):
        """Delete a TXT record from a domain
        :param str subdomain: record key in zone
        :param str value: value of record"""
        self._post_request("/tunnel/dns/remove", {
            "token": self.token,
            "machine": self.machine,
            "workspaceId": self.workspace_id,
            "tunnelId": self.tunnel_id,
            "domain": self.domain,
            "subdomain": subdomain,
            "value": value,
            "type": "TXT",
        })
