# Kubespray offline files: single ZIP

This project downloads **all 23 URLs** from the supplied `temp/files.list` for an `amd64` Linux offline deployment. It creates only **one** GitHub Actions Artifact, containing **one ZIP** with the original download filenames inside the `files/` directory.

## Run
1. Create a GitHub repository and upload the contents of this project **including `.github/workflows/download-files.yml`**.
2. Go to **Actions** → **Kubespray offline files - single ZIP** → **Run workflow**.
3. In the successful workflow run, download the artifact **kubespray-offline-files-amd64**. It is a single ZIP.

There is no separate SHA256 file. GitHub may display its own artifact digest in the UI.

## On the offline machine

```bash
mkdir -p /opt/kubespray-offline
unzip kubespray-offline-files-amd64.zip -d /opt/kubespray-offline
ls -lh /opt/kubespray-offline/files/
```

`download-manifest.tsv` records names, URLs and sizes without checksums.

**Important:** this is a download bundle, not an installation script. Kubespray expects its own offline file/registry configuration and file cache. Do not simply copy binaries over existing Kubernetes components. The generated list contains binaries for alternative runtimes and CNIs, so not all 23 are needed in every cluster. Other dependencies (OS packages, Python wheels, Helm charts) may still be required.

If any upstream URL fails, the workflow fails instead of publishing an incomplete ZIP. GitHub hosted runner disk capacity and artifact quota may impose limits on very large downloads.
