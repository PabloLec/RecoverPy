<div align="center">
  <img src="docs/assets/logo.png" alt="RecoverPy" width="auto">
  <h2>RecoverPy</h2>
  <em>Scan raw partitions and recover data by inspecting disk blocks directly.</em>

  <br><br>
  ![GitHub release](https://img.shields.io/github/v/release/pablolec/recoverpy?style=flat-square)
  ![License](https://img.shields.io/github/license/pablolec/recoverpy?style=flat-square)
  ![Downloads](https://static.pepy.tech/personalized-badge/recoverpy?period=total&units=abbreviation&left_color=grey&right_color=red&left_text=downloads)
  ![Tests](https://github.com/PabloLec/recoverpy/actions/workflows/pytest.yml/badge.svg?branch=main)
</div>

---

## 🎬 Demo

<p align="center">
  <img src="docs/assets/demo.gif" alt="RecoverPy Demo">
</p>

## 🔎 Overview

When a file is deleted, its metadata disappears first. The underlying disk blocks often remain intact until they are reused.

RecoverPy scans raw partition data directly and searches for byte patterns across the entire device. If the blocks have not been overwritten, fragments of deleted files can still be located by their content.

It lets you inspect matching blocks, navigate adjacent ones, and extract what remains in a straightforward way.

If the blocks are gone, recovery is impossible. If they are still there, RecoverPy helps you retrieve them.

---

## 🧭 What you can do

* Search a partition or disk image for a specific string.
* Inspect the disk blocks where matches are found.
* Move across adjacent blocks to recover fragmented data.
* Select and save useful content.

RecoverPy does not attempt to interpret filesystem structures or restore filenames. It focuses on exposing what remains on disk and making it accessible.

---

## 📦 Installation

### Requirements

- Linux
- Python 3.9+

Accessing raw block devices typically requires `sudo`.

### Using `uv`

```bash
sudo uvx recoverpy
````

Or install locally:

```bash
uv tool install recoverpy
sudo recoverpy
```

### Using pip

```bash
python -m pip install recoverpy
sudo recoverpy
```

---

## ▶️ Usage

Start RecoverPy:

```bash
sudo recoverpy
```

1. Select a partition.
2. Enter a distinctive search string.
3. Start the scan.
4. Open a result.
5. Inspect and navigate blocks.
6. Save useful content.

Using a unique identifier, configuration key, or sentence fragment generally produces better results than common words.

---

## ⚙️ How it works

RecoverPy operates directly on the raw byte stream of a block device.

The selected partition is opened in read-only mode and scanned sequentially using fixed-size chunks. The scanner processes the stream incrementally, keeping a small overlap between chunks to ensure that matches spanning chunk boundaries are not missed.

Pattern matching is performed at the byte level. For every match, RecoverPy records the exact absolute offset within the device. This offset becomes the reference point for block inspection and navigation.

Block reads are performed using explicit offsets rather than relying on filesystem abstractions. This allows precise access to adjacent blocks without loading large portions of the device into memory.

The entire scan is streaming-based and memory-bounded: RecoverPy never loads the full partition into memory.

---

## ⚠️ Limitations

RecoverPy works on raw data. It does not reconstruct files automatically or infer file boundaries.

Results may be partial or fragmented. If the underlying blocks have already been overwritten, recovery is not possible.

Accessing block devices typically requires sudo. To reduce the risk of further overwriting, avoid writing to the target partition during recovery and unmount it when possible.

---

## 🤝 Contributing

If you run into a bug or think something could be improved, feel free to open an issue. And if you’d like to work on it yourself, pull requests are always appreciated.

---

## 🛠 Development

Project structure:

* `recoverpy/ui/` — Textual interface
* `recoverpy/lib/search/` — streaming search engine
* `recoverpy/lib/storage/` — block and device access
* `recoverpy/lib/text/` — decoding utilities
* `tests/` — unit and integration tests

### Setup

```bash
uv sync --dev
```

### Run locally

```bash
sudo uv run recoverpy
```

### Run tests

```bash
uv run pytest -q
```
