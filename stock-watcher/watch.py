#!/usr/bin/env python3
"""Houdt twee CatchYourCards-producten in de gaten en stuurt een push via ntfy.sh
zodra ze te koop zijn (of zodra de pagina ineens anders reageert, bv. een wachtrij).

Alleen standaardbibliotheek. Instellingen via env:
  NTFY_TOPIC   ntfy-topic om op te abonneren in de ntfy-app
  INTERVAL     seconden tussen checks (standaard 15)
  DURATION     hoe lang draaien in seconden (standaard 0 = oneindig)
"""
import json, os, random, re, sys, time, urllib.request, urllib.error
from urllib.parse import urlparse

BASE = "https://catchyourcards.nl"
PRODUCTS = {
    "pokemon-30th-celebration-ultra-premium-collection-night": "Ultra Premium Collection: Night",
    "pokemon-30th-celebration-figure-collection-mewtwo": "Figure Collection: Mewtwo",
}
TOPIC = os.environ.get("NTFY_TOPIC", "cyc-pkmn-f1c7cdfc49")
INTERVAL = float(os.environ.get("INTERVAL", "15"))
DURATION = float(os.environ.get("DURATION", "0"))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept-Language": "nl-NL,nl;q=0.9",
        "Cache-Control": "no-cache", "Pragma": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.geturl(), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, url, e.read().decode("utf-8", "replace")


def notify(title, msg, url, priority="urgent"):
    req = urllib.request.Request(
        f"https://ntfy.sh/{TOPIC}", data=msg.encode(), method="POST",
        headers={"Title": title.encode("ascii", "ignore").decode(),
                 "Priority": priority, "Tags": "rotating_light",
                 "Click": url, "Actions": f"view, Open pagina, {url}"})
    try:
        urllib.request.urlopen(req, timeout=15).read()
        log("push verstuurd:", title)
    except Exception as e:
        log("push mislukt:", e)


def check_api(slug):
    """WooCommerce Store API. None als die niet bruikbaar is."""
    try:
        code, _, body = fetch(f"{BASE}/wp-json/wc/store/v1/products?slug={slug}&_={int(time.time())}")
        if code != 200:
            return None
        data = json.loads(body)
        if not data:
            return None
        p = data[0]
        return bool(p.get("is_in_stock")) and p.get("is_purchasable", True) is not False
    except Exception:
        return None


def check_html(slug):
    """Geeft ('in'|'out'|'unknown', detail)."""
    url = f"{BASE}/product/{slug}/?nc={int(time.time())}{random.randint(0, 999)}"
    try:
        code, final, html = fetch(url)
    except Exception as e:
        return "unknown", f"fout: {e}"
    host = urlparse(final).hostname or ""
    if not host.endswith("catchyourcards.nl"):
        return "unknown", f"doorgestuurd naar {host} (wachtrij?)"
    if code != 200:
        return "unknown", f"HTTP {code}"
    low = html.lower()
    if "queue-it" in low or ("wachtrij" in low and "single_add_to_cart_button" not in low):
        return "unknown", "wachtrij-pagina gedetecteerd"
    # Alleen het hoofdproduct bekijken: alles vóór de 'combineer je aankoop'-carrousel
    main = low.split("combineer je aankoop")[0]
    out = re.search(r'class="[^"]*\bout-of-stock\b|>\s*uitverkocht\s*<', main)
    add = "single_add_to_cart_button" in main or re.search(r'class="[^"]*\bstock in-stock\b', main)
    if add and not out:
        return "in", "knop 'in winkelwagen' staat erop"
    if out:
        return "out", "uitverkocht"
    return "unknown", "geen herkenbare voorraadstatus"


def status(slug):
    api = check_api(slug)
    html, detail = check_html(slug)
    if api is True or html == "in":
        return "in", f"api={api} html={detail}"
    if api is False or html == "out":
        return "out", f"api={api} html={detail}"
    return "unknown", f"api={api} html={detail}"


def main():
    log(f"start, topic={TOPIC}, interval={INTERVAL}s")
    notify("Pokemon-watcher draait", "Je krijgt een push zodra een box te koop is.",
           BASE, priority="default")
    last = {s: "out" for s in PRODUCTS}
    last_alert = {s: 0.0 for s in PRODUCTS}
    t0 = time.time()
    while not DURATION or time.time() - t0 < DURATION:
        for slug, name in PRODUCTS.items():
            st, detail = status(slug)
            log(f"{name}: {st} ({detail})")
            page = f"{BASE}/product/{slug}/"
            if st == "in" and time.time() - last_alert[slug] > 60:
                # blijft elke minuut pushen zolang hij op voorraad is
                notify(f"OP VOORRAAD: {name}", f"Nu kopen! {page}", page)
                last_alert[slug] = time.time()
            elif st == "unknown" and last[slug] != "unknown":
                notify(f"Pagina veranderd: {name}", f"{detail}. Kijk nu: {page}", page, "high")
            last[slug] = st
        time.sleep(INTERVAL + random.uniform(0, 3))
    log("klaar (DURATION verstreken)")


if __name__ == "__main__":
    sys.exit(main())
