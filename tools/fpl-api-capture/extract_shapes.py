"""mitmproxy addon: extract JSON key shapes from FPL API responses."""
import json
from urllib.parse import urlparse


API_PREFIXES = (
    "/cs/customer/",
    "/api/resources/",
)


def key_paths(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else k
            yield p
            yield from key_paths(v, p)
    elif isinstance(obj, list) and obj:
        yield from key_paths(obj[0], f"{prefix}[]")


class ExtractShapes:
  def response(self, flow):
    parsed = urlparse(flow.request.pretty_url)
    if "fpl.com" not in flow.request.pretty_host:
      return
    if not any(parsed.path.startswith(p) for p in API_PREFIXES):
      return
    if not flow.response or not flow.response.content:
      return
    ct = flow.response.headers.get("content-type", "")
    if "json" not in ct and not flow.response.content[:1] in (b"{", b"["):
      return
    try:
      body = json.loads(flow.response.content)
    except json.JSONDecodeError:
      return
    keys = sorted(set(key_paths(body)))[:60]
    status = flow.response.status_code
    print(f"\n{'='*70}")
    print(f"{flow.request.method} {parsed.path}  [{status}]")
    for k in keys:
      print(f"  {k}")


addons = [ExtractShapes()]
