# Recoverpy [![GitHub release (latest by date)](https://img.shields.io/github/v/release/pablolec/recoverpy)](https://github.com/PabloLec/recoverpy/releases/) [![GitHub](https://img.shields.io/github/license/pablolec/recoverpy)](https://github.com/PabloLec/recoverpy/blob/main/LICENCE) [![Downloads](https://static.pepy.tech/personalized-badge/recoverpy?period=total&units=abbreviation&left_color=grey&right_color=yellow&left_text=Downloads)](https://pepy.tech/project/recoverpy)

Recoverpy is a CUI utility written in Python with the help of [py_cui](https://github.com/jwlodek/py_cui "py_cui").

You can already find plenty of solutions to recover deleted files but it can be a hassle to recover overwritten files. Recoverpy search through every inodes to find your request.

## Installation

:penguin: The main prerequisite is having a Linux system.

The file system type of your partition should not be a problem, just make sure you have access to `grep`, `dd`, and `lsblk` commands.

- Debian-like :

`apt install grep coreutils util-linux`

- Arch :

`pacman -S grep coreutils util-linux`

- Fedora :

`dnf install grep coreutils util-linux`

### - From pip (_recommended_):

Pip should be already installed if you have Python >=3.4. Otherwise, see [pip docs](https://pip.pypa.io/en/stable/installing/ "pip docs") for installation.

`pip install recoverpy`

### - From source:

To install:

```bash
git clone https://github.com/pablolec/recoverpy
cd recoverpy
python3 -m pip install .
```

To update:

`python3 -m pip install --upgrade recoverpy`

## Demo

<p align="center">
    <img src="docs/assets/demo.gif">
</p>

## Usage

```bash
python3 -m recoverpy
```

**You must have root access to use recoverpy**.

If you are not logged as root use `sudo recoverpy` or log in with `su -` before execution.

First, select the system partition in which your file was. If you are out of luck, you can alternatively search in your home partition, maybe your IDE, text editor, etc. made a backup at some point.

Then, type a text to search. You can now start the search.

Note that searching a string in a whole partition may take _a while_. (see [euphemism](https://en.wikipedia.org/wiki/Euphemism "euphemism"))

Results will appear in the left-hand box. Select a result to display the corresponding partition block content in the right-hand box.

Once you have found your precious, select `Save`.
You can now either save this block individually or explore neighboring blocks for the remaining parts of the file. You could then save it all in one file.

**Save path is set in `conf.yaml`. Default is `/tmp/`.**

## Tips

- Always do backups! Yes, maybe too late...
- **Unmount your partition before you do anything!** Although you can search with your partition still mounted, it is highly recommended to unmount your partition to avoid any alteration to your file.

Regarding the string you search:

- Be concise, find something that could be unique to your file.
- Stay simple, your string is escaped but exotic characters may affect your results.
- Try to remember the last edit you have made to your file.

When you have a match:

- Use the option to explore neighboring blocks to make sure you do not miss some part of your file.
