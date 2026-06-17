"""mitmproxy addon: summarize captured FPL endpoints."""
from collections import defaultdict
from urllib.parse import urlparse


class Summarize:
    def __init__(self):
        self.counts = defaultdict(int)
        self.samples = []

    def response(self, flow):
        host = flow.request.pretty_host
        if "fpl.com" not in host and "cognito" not in host:
            return
        parsed = urlparse(flow.request.pretty_url)
        key = f"{flow.request.method} {parsed.path}"
        self.counts[key] += 1
        if len(self.samples) < 300:
            status = flow.response.status_code if flow.response else None
            self.samples.append((key, status))

    def done(self):
        print(f"Total FPL-related requests: {sum(self.counts.values())}")
        print(f"Unique endpoints: {len(self.counts)}\n")
        for key, n in sorted(self.counts.items(), key=lambda x: -x[1]):
            print(f"{n:3d}x  {key}")


addons = [Summarize()]
