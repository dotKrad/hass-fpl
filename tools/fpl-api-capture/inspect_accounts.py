"""mitmproxy addon: inspect account list endpoints."""
import json
from urllib.parse import urlparse


class InspectAccounts:
    def response(self, flow):
        path = urlparse(flow.request.pretty_url).path
        if path not in (
            "/cs/customer/v1/resources/header",
            "/cs/customer/v1/resources/account",
            "/cs/customer/v1/accountservices/resources/loginNew",
        ) and "multiaccount" not in path:
            return
        if not flow.response or flow.response.status_code != 200:
            return
        try:
            body = json.loads(flow.response.content)
        except json.JSONDecodeError:
            return
        print(f"\n### {flow.request.method} {path}")
        if path.endswith("/header"):
            acct_block = body["data"]["accounts"]["data"]
            print(
                f"count={acct_block.get('count')} total={acct_block.get('total')} "
                f"hasMore={acct_block.get('hasMore')} returned={len(acct_block.get('data', []))}"
            )
            total_acc = body["data"].get("multiProfileDetails", {}).get("data", {}).get(
                "totalAccCount"
            )
            print(f"totalAccCount={total_acc}")
        elif path.endswith("/account"):
            print(
                f"count={body.get('count')} total={body.get('total')} "
                f"hasMore={body.get('hasMore')} returned={len(body.get('data', []))}"
            )
            for a in body.get("data", []):
                print(
                    f"  {a.get('accountNumber')} status={a.get('statusCategory')} "
                    f"statusName={a.get('statusName')}"
                )
        elif path.endswith("/loginNew"):
            accts = body.get("data", {}).get("AccountList", {}).get("data", [])
            print(f"loginNew accounts: {len(accts)}")


addons = [InspectAccounts()]
