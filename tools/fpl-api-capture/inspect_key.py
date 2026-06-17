"""mitmproxy addon: inspect specific FPL API responses."""
import json
from urllib.parse import urlparse


class Inspect:
    def response(self, flow):
        path = urlparse(flow.request.pretty_url).path
        targets = {
            "/cs/customer/v1/resources/header",
            "/cs/customer/v1/accountservices/resources/loginNew",
        }
        if path not in targets and "/select" not in path and "hourly" not in path:
            return
        if not flow.response or flow.response.status_code != 200:
            return
        try:
            body = json.loads(flow.response.content)
        except json.JSONDecodeError:
            return
        print(f"\n### {flow.request.method} {path}")
        if path.endswith("/header"):
            accts = body["data"]["accounts"]["data"]["data"]
            print(f"accounts in header: {len(accts)}")
            for a in accts:
                print(f"  {a['accountNumber']} status={a.get('statusCategory')} balance={a.get('balance')}")
        elif path.endswith("/loginNew"):
            accts = body["data"]["AccountList"]["data"]
            print(f"accounts in loginNew: {len(accts)}")
            for a in accts:
                print(
                    f"  balancesDrilldown={'yes' if 'balancesDrilldown' in a else 'NO'} "
                    f"balance={a.get('balance')} dueDateVal={a.get('dueDateVal')!r}"
                )
        elif "/select" in path:
            d = body.get("data", {})
            print(
                f"account={d.get('accountNumber')} premise={d.get('premiseNumber')} "
                f"meterNo={d.get('meterNo')} currentBillDate={d.get('currentBillDate')}"
            )


addons = [Inspect()]
