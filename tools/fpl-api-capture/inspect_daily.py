"""mitmproxy addon: inspect DailyUsage shape in energy service responses."""
import json
from urllib.parse import urlparse


class InspectDaily:
    def response(self, flow):
        if "mobile-energy-service" not in flow.request.pretty_url:
            return
        if not flow.response or flow.response.status_code != 200:
            return
        try:
            body = json.loads(flow.response.content)
        except json.JSONDecodeError:
            return
        data = body.get("data", {})
        daily = data.get("DailyUsage")
        current = data.get("CurrentUsage")
        print(f"\n### {flow.request.pretty_url.split('/')[-2]}")
        print(f"DailyUsage type: {type(daily).__name__}")
        if isinstance(daily, dict):
            print(f"  keys: {sorted(daily.keys())}")
            print(f"  endDate: {daily.get('endDate')!r}")
            print(f"  data len: {len(daily.get('data') or [])}")
        else:
            print(f"  value: {daily!r}"[:200])
        if isinstance(current, dict):
            print(f"CurrentUsage keys sample: {sorted(current.keys())[:8]}...")
        else:
            print(f"CurrentUsage: {current!r}"[:120])


addons = [InspectDaily()]
