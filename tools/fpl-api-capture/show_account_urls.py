"""mitmproxy addon: print account endpoint request URLs."""
from urllib.parse import urlparse


class ShowUrls:
    def response(self, flow):
        path = urlparse(flow.request.pretty_url).path
        if "account" in path and "fpl.com" in flow.request.pretty_host:
            if path.startswith("/cs/customer/"):
                print(f"{flow.request.method} {flow.request.pretty_url}")


addons = [ShowUrls()]
