#!/usr/bin/env python
"""Download the operations wiki with template information."""
import io
import re
import tarfile
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

URL_WIKI_EXPORT = "https://home.strw.leidenuniv.nl/~burtscher/metis_operations/"
PATH_HERE = Path(__file__).parent


def main():
    """Download the operations wiki with template information."""
    with urllib.request.urlopen(URL_WIKI_EXPORT) as f:
        html = f.read().decode("utf-8")

    fns_tarballs = sorted(
        re.findall(
            r'<a href="(metis_operations_\d\d\d\d-\d\d-\d\dT\d\d_\d\d_\d\d.tar.gz)',
            html,
        )
    )

    fn_last_tarball = fns_tarballs[-1]
    sdate_last_tarball = fn_last_tarball[17:36]
    date_last_tarball = datetime.strptime(
        sdate_last_tarball,
        "%Y-%m-%dT%H_%M_%S",
    )
    assert date_last_tarball > datetime.now() - timedelta(
        hours=2
    ), f"Tarball {fn_last_tarball} is more than two hours old, something is wrong."

    url_last_tarball = URL_WIKI_EXPORT + fn_last_tarball
    with urllib.request.urlopen(url_last_tarball) as ftb:
        ftb_bytes = ftb.read()
        io_bytes = io.BytesIO(ftb_bytes)
        tb = tarfile.open(fileobj=io_bytes, mode="r")
        tb.extractall(path=PATH_HERE)


if __name__ == "__main__":
    main()
