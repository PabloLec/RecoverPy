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
    <img src="https://github.com/PabloLec/recoverpy/actions/workflows/pytest.yml/badge.svg?branch=main" alt="Tests">
</a>
</p>

---

<!--ts-->

* [Demo](#Demo)
* [Installation](#Installation)
    * [Dependencies](#dependencies)
    * [Run with pipx](#run-with-pipx)
    * [Installation from pip](#installation-from-pip)
    * [Installation from AUR](#installation-from-aur)
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

## Setup

:penguin: RecoverPy is currently only available on Linux systems.  
:red_circle: **You must be root or use sudo**.

### Dependencies

**Mandatory:** To list and search through your partitions, recoverpy uses `grep`, `dd`, and `lsblk` commands. Although,
if you're running a major Linux distrucition these tools should already be installed.

**Optional:** To display real time grep progress, you can install `progress`.

To install all dependencies:

- Debian-like: `apt install grep coreutils util-linux progress`
- Arch: `pacman -S grep coreutils util-linux progress`
- Fedora: `dnf install grep coreutils util-linux progress`

## Usage

### Run with uvx

`sudo uvx recoverpy`

### Run with pipx

`sudo pipx run recoverpy`

### Installation from pip

`python3 -m pip install recoverpy`

then run `sudo python3 -m recoverpy`

---

- **Select the system partition** in which your file was. If you are out of luck, you can alternatively search in your
  home partition, maybe your IDE, text editor, etc. made a backup at some point.

- **Type a text string to search**. See tips below for better results.

- **Start search**, Results will appear in the left-hand box.

- **Select a result**.

- Once you have found your precious, **select `Open`**.

- You can now either save this block individually or explore neighboring blocks for the remaining parts of the file. You
  could then save it all in one file.

## Tips

- Always do backups! Yes, maybe too late...
- **Unmount your partition before you do anything!** Although you can search with your partition still mounted, it is
  highly recommended to unmount your partition to avoid any alteration to your file.

Regarding the searched string:

- Be concise, find something that could be unique to your file.
- Stay simple, your string is escaped but exotic characters may affect your results.
- Try to remember the last edit you have made to your file.

When you have found your file:

- You might see multiple results. Your system often use different partion blocks to save successive versions of a file.
  Make sure you've found the last version.
- Try exploring neighboring blocks to be sure to save your whole file.

## Contributing

Thank you for considering contributing to RecoverPy.
Any request, bug report or PR are welcome. Please read the [contributing guide](CONTRIBUTING.md).
