from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Callable

from fastapi import HTTPException
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from app.admin_ops.browser_flows import available_flows, run_named_flow

SCREENSHOT_DIR = Path("/opt/agente-divina/logs/browser_screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def _browser_run(url: str, actions: list[dict[str, Any]] | None = None, timeout: int = 15000) -> dict[str, Any]:
    actions = actions or []
    results: list[dict[str, Any]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1366, "height": 900})
        response = page.goto(url, wait_until="networkidle", timeout=timeout)

        for index, action in enumerate(actions, start=1):
            kind = str(action.get("action") or "").strip()
            selector = action.get("selector")
            value = action.get("value")
            item: dict[str, Any] = {"index": index, "action": kind, "ok": True}

            try:
                if kind == "wait_for_selector":
                    page.wait_for_selector(str(selector), timeout=int(action.get("timeout") or timeout))
                    item["selector"] = selector

                elif kind == "fill":
                    page.fill(str(selector), str(value or ""), timeout=int(action.get("timeout") or timeout))
                    item["selector"] = selector

                elif kind == "click":
                    page.click(str(selector), timeout=int(action.get("timeout") or timeout))
                    item["selector"] = selector

                elif kind == "press":
                    page.press(str(selector), str(value or "Enter"), timeout=int(action.get("timeout") or timeout))
                    item["selector"] = selector

                elif kind == "assert_text":
                    text = page.text_content(str(selector), timeout=int(action.get("timeout") or timeout)) or ""
                    expected = str(value or "")
                    item["selector"] = selector
                    item["text"] = text[:500]
                    item["expected"] = expected
                    item["ok"] = expected in text

                elif kind == "assert_url_contains":
                    expected = str(value or "")
                    item["current_url"] = page.url
                    item["expected"] = expected
                    item["ok"] = expected in page.url

                elif kind == "screenshot":
                    name = str(value or f"screenshot-{_timestamp()}.png")
                    if not name.endswith(".png"):
                        name += ".png"
                    path = SCREENSHOT_DIR / name
                    page.screenshot(path=str(path), full_page=bool(action.get("full_page", True)))
                    item["path"] = str(path)

                elif kind == "extract_text":
                    text = page.text_content(str(selector or "body"), timeout=int(action.get("timeout") or timeout)) or ""
                    item["selector"] = selector or "body"
                    item["text"] = text[:4000]

                elif kind == "wait":
                    page.wait_for_timeout(int(value or action.get("ms") or 1000))

                else:
                    raise HTTPException(status_code=400, detail=f"ação de navegador não suportada: {kind}")

            except PlaywrightTimeoutError as exc:
                item["ok"] = False
                item["error"] = f"timeout: {exc}"
            except Exception as exc:
                item["ok"] = False
                item["error"] = str(exc)

            results.append(item)
            if not item.get("ok") and bool(action.get("stop_on_error", True)):
                break

        final = {
            "ok": bool(response and response.ok) and all(r.get("ok") for r in results),
            "url": url,
            "current_url": page.url,
            "status": response.status if response else None,
            "title": page.title(),
            "actions": results,
        }
        browser.close()
        return final


def browser_health(url: str) -> dict[str, Any]:
    return _browser_run(url)


def _attach_diagnostics(page):
    diagnostics: dict[str, list[dict[str, Any]]] = {
        "console": [],
        "page_errors": [],
        "request_failed": [],
        "responses": [],
    }

    def interesting(url: str) -> bool:
        return any(part in url for part in ["/api/", "/erp/security", "/admin/full-access", "127.0.0.1:3000", "127.0.0.1:8000"])

    def on_console(msg):
        try:
            if msg.type in {"error", "warning"}:
                diagnostics["console"].append({"type": msg.type, "text": msg.text[:1000]})
        except Exception as exc:
            diagnostics["console"].append({"type": "diagnostic_error", "text": str(exc)})

    def on_page_error(exc):
        diagnostics["page_errors"].append({"error": str(exc)[:2000]})

    def on_request_failed(req):
        try:
            diagnostics["request_failed"].append({
                "method": req.method,
                "url": req.url,
                "resource_type": req.resource_type,
                "failure": req.failure,
            })
        except Exception as exc:
            diagnostics["request_failed"].append({"error": str(exc)})

    def on_response(resp):
        try:
            url = resp.url
            if interesting(url):
                item = {"status": resp.status, "url": url, "request_method": resp.request.method}
                if resp.status >= 400:
                    try:
                        item["body_preview"] = (resp.text() or "")[:1500]
                    except Exception:
                        pass
                diagnostics["responses"].append(item)
        except Exception as exc:
            diagnostics["responses"].append({"error": str(exc)})

    page.on("console", on_console)
    page.on("pageerror", on_page_error)
    page.on("requestfailed", on_request_failed)
    page.on("response", on_response)
    return diagnostics


def _browser_flow(flow: str, args: dict[str, Any], timeout: int) -> dict[str, Any]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1366, "height": 900})
        diagnostics = _attach_diagnostics(page)
        try:
            result = run_named_flow(page, flow, args, timeout)
            result["diagnostics"] = diagnostics
            return result
        finally:
            browser.close()


def handle_browser_op(req: Any, run_cmd: Callable[..., dict[str, Any]] | None = None) -> dict[str, Any] | None:
    op = req.operation
    if op not in {"browser_open", "browser_run", "browser_health", "browser_screenshot", "browser_extract_text", "browser_login_check", "browser_flow", "browser_list_flows"}:
        return None

    args = req.args or {}
    url = args.get("url") or req.path or "https://grupo-divina-dashboard.vercel.app/auth/login"
    timeout = int(args.get("timeout") or 15000)

    if op == "browser_list_flows":
        return {"ok": True, "flows": available_flows()}

    if op == "browser_flow":
        flow = str(args.get("flow") or req.content or "login")
        return _browser_flow(flow, args, timeout)

    if op == "browser_health":
        return _browser_run(str(url), timeout=timeout)

    if op == "browser_open":
        return _browser_run(str(url), actions=args.get("actions") or [], timeout=timeout)

    if op == "browser_run":
        return _browser_run(str(url), actions=args.get("actions") or [], timeout=timeout)

    if op == "browser_screenshot":
        name = args.get("name") or f"browser-{_timestamp()}.png"
        return _browser_run(str(url), actions=[{"action": "screenshot", "value": name}], timeout=timeout)

    if op == "browser_extract_text":
        selector = args.get("selector") or "body"
        return _browser_run(str(url), actions=[{"action": "extract_text", "selector": selector}], timeout=timeout)

    if op == "browser_login_check":
        return _browser_flow("login", args, timeout)

    return None
