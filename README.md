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
<a href="#" target="_blank">
    <img src="https://github.com/PabloLec/recoverpy/actions/workflows/recoverpy-tests.yml/badge.svg?branch=main" alt="Tests">
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
<!--te-->

---

# RecoverPy

You can already find plenty of solutions to recover deleted files, but it can be a hassle to recover overwritten files. RecoverPy searches through every block of your partition to find your request.

## Demo

<p align="center">
    <img src="docs/assets/demo.gif">
</p>

## Installation

:penguin: RecoverPY is currently only available on Linux systems.

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

:red_circle: **You must have root access to use recoverpy**.

If you are not logged as root use `sudo recoverpy` or log in with `su -` before execution.<br/>
*And if you are pentesting, well, keep grinding.*

---

First, **select the system partition** in which your file was. If you are out of luck, you can alternatively search in your home partition, maybe your IDE, text editor, etc. made a backup at some point.

Then, **type some text to search**. See tips below for better results.

Note that searching a string in a whole partition may take _a while_. (see [euphemism](https://en.wikipedia.org/wiki/Euphemism "euphemism"))

Results will appear in the left-hand box. Select a result to display the corresponding partition block content in the right-hand box.

Once you have found your precious, select `Save`.

You can now either save this block individually or explore neighboring blocks for the remaining parts of the file. You could then save it all in one file.

**Save path is set in `conf.yaml`. Default is `/tmp/`.**

## Tips

- Always do backups! Yes, maybe too late...
- **Unmount your partition before you do anything!** Although you can search with your partition still mounted, it is highly recommended to unmount your partition to avoid any alteration to your file.

Regarding the searched string:

- Be concise, find something that could be unique to your file.
- Stay simple, your string is escaped but exotic characters may affect your results.
- Try to remember the last edit you have made to your file.

When you found your file:

- Use the option to explore neighboring blocks to make sure you do not miss some part of your file.
