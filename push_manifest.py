"""Push the live IMDb Rows manifest into the Stremio account's addon collection,
so every device picks up new catalogs or resources without a reinstall.

Reads the auth key from the Stremio Mac app's localStorage and backs up the
current collection to ~/.stremio_collection_backup.json first. Stdlib only.

Usage: python3 push_manifest.py
"""
import glob, json, os, sqlite3, ssl, urllib.request

LIVE = "https://liamcanning.github.io/stremio-imdb-rows/manifest.json"
DB = "~/Library/WebKit/com.westbridge.stremio5-mac/WebsiteData/Default/*/*/LocalStorage/localstorage.sqlite3"
CTX = ssl.create_default_context(cafile="/etc/ssl/cert.pem")


def call(method, **body):
    req = urllib.request.Request(f"https://api.strem.io/api/{method}", data=json.dumps(body).encode(),
                                 headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
        return json.load(r)["result"]


def main():
    v = sqlite3.connect(f"file:{glob.glob(os.path.expanduser(DB))[0]}?mode=ro", uri=True) \
        .execute("select value from ItemTable where key='profile'").fetchone()[0]
    key = json.loads(v.decode("utf-16-le") if isinstance(v, bytes) else v)["auth"]["key"]
    addons = call("addonCollectionGet", authKey=key, update=True)["addons"]
    json.dump(addons, open(os.path.expanduser("~/.stremio_collection_backup.json"), "w"))
    with urllib.request.urlopen(LIVE, timeout=60, context=CTX) as r:
        live = json.load(r)
    for a in addons:
        if a["manifest"]["id"] == live["id"]:
            old = a["manifest"]["version"]
            a["manifest"] = live
            call("addonCollectionSet", authKey=key, addons=addons)
            print(f"IMDb Rows {old} -> {live['version']}, catalogs: {len(live['catalogs'])}")
            return
    print("IMDb Rows not installed on this account")


if __name__ == "__main__":
    main()
