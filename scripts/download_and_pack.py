#!/usr/bin/env python3
"""Download each URL in files.list and package all into one ZIP. No hashes generated."""
from pathlib import Path
from urllib.parse import urlparse
import os
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
URLS = ROOT / 'files.list'
OUTPUT = ROOT / 'output'
DOWNLOADS = OUTPUT / 'files'
ARCHIVE = OUTPUT / 'kubespray-offline-files-amd64.zip'

def main():
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    urls = [line.strip() for line in URLS.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#')]
    seen = set()
    mapping = []
    for idx, url in enumerate(urls, 1):
        if not url.startswith('https://'):
            raise ValueError(f'URL must be HTTPS: {url}')
        filename = Path(urlparse(url).path).name
        if not filename or filename in seen:
            raise ValueError(f'Invalid or duplicate filename: {filename!r}')
        seen.add(filename)
        dest = DOWNLOADS / filename
        print(f'[{idx}/{len(urls)}] {filename}', flush=True)
        subprocess.run([
            'curl', '--fail', '--location', '--show-error', '--silent',
            '--retry', '5', '--retry-all-errors', '--retry-delay', '3',
            '--connect-timeout', '30', '--max-time', '1800',
            '--output', str(dest), url
        ], check=True)
        if not dest.is_file() or dest.stat().st_size == 0:
            raise RuntimeError(f'Empty download: {url}')
        mapping.append((filename, url, dest.stat().st_size))

    manifest = OUTPUT / 'download-manifest.tsv'
    manifest.write_text('filename\tsource_url\tsize_bytes\n' + ''.join(
        f'{name}\t{url}\t{size}\n' for name, url, size in mapping
    ))
    # ZIP_STORED: no further compression of archives and binaries, much faster.
    with zipfile.ZipFile(ARCHIVE, 'w', compression=zipfile.ZIP_STORED, allowZip64=True) as zf:
        for filename, _, _ in mapping:
            zf.write(DOWNLOADS / filename, arcname=f'files/{filename}')
        zf.write(manifest, arcname='download-manifest.tsv')
        zf.write(URLS, arcname='files.list')
    with zipfile.ZipFile(ARCHIVE) as zf:
        if zf.testzip() is not None:
            raise RuntimeError('Corrupt zip member')
    print(f'PACKED {len(mapping)} files into {ARCHIVE} ({ARCHIVE.stat().st_size} bytes)', flush=True)

if __name__ == '__main__':
    main()
