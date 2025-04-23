<div align="center">
  <img src="docs/assets/logo.png" alt="RecoverPy" width="auto">
  <h2>RecoverPy</h2>
  <em>Find and recover deleted or even overwritten files from your Linux partitions, quickly and easily.</em>
  
  <br><br>

  ![GitHub release](https://img.shields.io/github/v/release/pablolec/recoverpy?style=flat-square)
  ![License](https://img.shields.io/github/license/pablolec/recoverpy?style=flat-square)
  ![Downloads](https://static.pepy.tech/personalized-badge/recoverpy?period=total&units=abbreviation&left_color=grey&right_color=red&left_text=downloads)
  ![Tests](https://github.com/PabloLec/recoverpy/actions/workflows/pytest.yml/badge.svg?branch=main)
  
</div>

---

RecoverPy doesn't just recover deleted files, but also helps you **recover overwritten data** by scanning each disk block. Whether it's a lost snippet of code, accidentally deleted configs, or overwritten text files, RecoverPy gives you a powerful, interactive way to get it back.

## ✨ Features

- ✅ Recover **overwritten and deleted files**
- 🔍 Search file contents by string, even in binary files
- 📟 Modern, easy-to-use terminal UI
- 🐧 Linux compatible (all file systems supported)
- ⚡️ Fast, leveraging core Linux utilities (`grep`, `dd`, `lsblk`)

---

## 🎬 Demo

<p align="center">
  <img src="docs/assets/demo.gif" alt="RecoverPy Demo">
</p>

---

## 📦 Installation

> **Warning:** You **must** run RecoverPy as root (`sudo`).

RecoverPy is Linux-only. Make sure you have these common tools installed (`grep`, `dd`, `lsblk`). Optionally, install `progress` to monitor scan progress:

```bash
# Debian / Ubuntu
sudo apt install grep coreutils util-linux progress

# Arch
sudo pacman -S grep coreutils util-linux progress

# Fedora
sudo dnf install grep coreutils util-linux progress
```

### Quick Run (no installation)

Using `pipx`:

```bash
sudo pipx run recoverpy
```

Or using `uvx`:

```bash
sudo uvx recoverpy
```

### Install from PyPI

```bash
python3 -m pip install recoverpy
sudo recoverpy
```

---

## 💻 Usage

1. **Launch RecoverPy:**

```bash
sudo recoverpy
```

2. **Select Partition:**  
   Choose the partition where your lost data resides. If unsure, try scanning your `/home` partition, it might contain editor or IDE backups.

3. **Search Content:**  
   Enter a unique string from the lost file content. RecoverPy will scan disk blocks to locate matches.

4. **Find & Recover:**  
   Results appear interactively. Select a result, preview the block, and save it. Explore neighboring blocks if the file spans multiple disk blocks.

---

## 💡 Recovery Tips

- 🛑 **Unmount partition first:** Reduce risk of data overwriting.
- 🎯 **Be specific:** Use unique, simple search strings.
- ⏳ **Act quickly:** The sooner you scan, the higher your recovery chances.
- 📑 **Check adjacent blocks:** Your file might span several blocks—check them all.

---

## 🤝 Contributing

Found a bug or have an idea? PRs, issues, and suggestions are warmly welcome. Check out our [contributing guide](CONTRIBUTING.md) for how to get involved!

---

If RecoverPy saved your day, consider ⭐️ starring the repo, thanks for your support!

