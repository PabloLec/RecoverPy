<div align="center">
    <img src="docs/assets/logo.png" alt="RecoverPy">
</div>

<p align="center">
    <em>Recover overwritten or deleted data.</em>
</p>

<p align="center">
<a href="https://img.shields.io/github/v/release/pablolec/recoverpy" target="_blank">
    <img src="https://img.shields.io/github/v/release/pablolec/recoverpy" alt="Release">
</a>
<a href="https://github.com/PabloLec/recoverpy/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/pablolec/recoverpy" alt="License">
</a>
<a href="https://pepy.tech/project/recoverpy" target="_blank">
    <img src="https://static.pepy.tech/personalized-badge/recoverpy?period=total&units=abbreviation&left_color=grey&right_color=red&left_text=downloads" alt="Downloads">
</a>
</a>
<a href="#" target="_blank">
    <img src="docs/assets/coverage.svg" alt="Coverage">
</a>
<a href="#" target="_blank">
    <img src="https://github.com/PabloLec/recoverpy/actions/workflows/pytest.yml/badge.svg?branch=main" alt="Tests">
</a>
</p>

---

<!--ts-->
   * [Demo](#Demo)
   * [Installation](#Installation)
      * [Dependancies](#arrow_right-dependancies)
      * [Installation from pip](#arrow_right-installation-from-pip)
   * [Usage](#Usage)
   * [Tips](#Tips)
   * [Contributing](#Contributing)
<!--te-->

---

# RecoverPy

RecoverPy is a powerful tool that leverages your system capabilities to recover lost files.

Unlike others, you can not only recover deleted files but also **overwritten** data.

Every block of your partition will be scanned. You can even find a string in binary files.
## Demo

<p align="center">
    <img src="docs/assets/demo.gif">
</p>

## Installation

:penguin: RecoverPy is currently only available on Linux systems.

#### :arrow_right: Dependancies

**Mandatory:** To list and search through your partitions, recoverpy uses `grep`, `dd`, and `lsblk` commands.

**Optional:** To display real time grep progress, you can install `progress`.

To install all dependencies:
- Debian-like: `apt install grep coreutils util-linux progress`
- Arch: `pacman -S grep coreutils util-linux progress`
- Fedora: `dnf install grep coreutils util-linux progress`

#### :arrow_right: Installation from pip

`python3 -m pip install recoverpy`

## Usage

```bash
python3 -m recoverpy
```

:red_circle: **You must be root or use sudo**.

:arrow_right: Default save path is `/tmp/`, click on Settings to edit configuration.

---

:one: **Select the system partition** in which your file was. If you are out of luck, you can alternatively search in your home partition, maybe your IDE, text editor, etc. made a backup at some point.

:two: **Type a text string to search**. See tips below for better results.

:three: **Start search**, Results will appear in the left-hand box.

:four: **Select a result** to display the corresponding partition block content in the right-hand box.

:five: Once you have found your precious, **select `Save`**.

:six: You can now either save this block individually or explore neighboring blocks for the remaining parts of the file. You could then save it all in one file.

## Tips

- Always do backups! Yes, maybe too late...
- **Unmount your partition before you do anything!** Although you can search with your partition still mounted, it is highly recommended to unmount your partition to avoid any alteration to your file.

Regarding the searched string:

- Be concise, find something that could be unique to your file.
- Stay simple, your string is escaped but exotic characters may affect your results.
- Try to remember the last edit you have made to your file.

When you have found your file:

- You might see multiple results. Your system often use different partion blocks to save successive versions of a file. Make sure you've found the last version.
- Use the option to explore neighboring blocks to make sure you do not miss some part of your file.

## Contributing

Thank you for considering contributing to RecoverPy.
Any request, bug report or PR are welcome. Please read the [contributing guide](CONTRIBUTING.md).
