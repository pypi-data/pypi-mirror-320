# pistol terminal guide

## installation
all of these installation methods apply to the newest version of pistol unless stated otherwise.

### 1. windows & linux/ubuntu install using `gavel` (most recommended):
- this method installs the newest version on github, so you'll be the first to receive new versions
#### step 1: make sure `gavel` is installed
```
git clone https://github.com/pixilll/gavel
pipx install ./gavel
```
#### step 2: install pistol
```
gavel install pixilll pistol
```

### 2. windows install using `pip`:
#### step 1: make sure `pip` is updated
```
python -m pip install --upgrade pip
```
#### step 2: install pistol
```
pip install pistol
```
### 3. new in 2.0: linux/ubuntu install using `pipx`:
#### step 1: make sure `pipx` is installed and updated
```
sudo apt install pipx
```
#### step 2: install pistol
```
pipx install pistol
```
### 4. linux/ubuntu install using `pip` and `venv`:
#### step 1: create a virtual environment using `venv`
```
python3 -m venv .venv
```
#### step 2: activate the environment
```
source .venv/bin/activate
```
#### step 3: make sure `pip` is updated
```
python3 -m pip install --upgrade pip
```
#### step 4: install pistol
```
python3 -m pip install pistol
```
### 5. windows fetch using `git` and install using `pip`:
#### step 1: clone the pistol repository
```
git clone https://github.com/pixilll/pistol
```
#### step 2: make sure `pip` is updated
```
python -m pip install --upgrade pip
```
#### step 3: install the pistol directory
```
pip install ./pistol
```
### 6. new in 2.0: linux/ubuntu fetch using `git` and install using `pipx`:
#### step 1: clone the pistol repository
```
git clone https://github.com/pixilll/pistol
```
#### step 2: make sure `pipx` is installed and updated
```
sudo apt install pipx
```
#### step 3: install the pistol directory
```
pipx install ./pistol
```
### 7. linux/ubuntu fetch using `git` and install using `pip` and `venv`:
#### step 1: create a virtual environment using `venv`
```
python3 -m venv .venv
```
#### step 2: activate the environment
```
source .venv/bin/activate
```
#### step 3: clone the pistol repository
```
git clone https://github.com/pixilll/pistol
```
#### step 4: make sure `pip` is updated
```
python3 -m pip install --upgrade pip
```
#### step 5: install the pistol directory
```
python3 -m pip install ./pistol
```
### 8. build from source:
#### pistol is open-source, and any source code files can be downloaded individually if needed. pistol can be built on your system relatively easily whether you're on windows or linux.

#### /!\ disclaimer: installing pistol on linux using the third and fifth methods will make pistol only accessible while in the venv environment where it has been installed. you may need to redo step 2 every time you restart your terminal.

## which install method should i choose?

| os      | recommended | supported                    |
|---------|-------------|------------------------------|
| windows | 2nd         | 1st, 2nd, 5th, 8th           |
| ubuntu  | 3rd         | 1st, 3rd, 4th, 6th, 7th, 8th |
| linux*  | 3rd         | 1st, 3rd, 4th, 6th, 7th, 8th |
| macos   |             | no install methods for macos |

*linux means linux distributions in general, except for ubuntu which was mentioned beforehand

## os compatibility and availability

| os           | availability                    | pistol versions compatible |
|--------------|---------------------------------|----------------------------|
| windows 11   | tested, available               | &gt;=1.0                   |
| windows 8-10 | not tested, should be available | &gt;=1.0                   |
| windows <=7  | tested, not available           | no versions                |
| ubuntu       | tested, available               | &gt;=1.0                   |
| linux*       | not tested, should be available | &gt;=1.0                   |
| macos        | tested, not available           | no versions                |

*linux means linux distributions in general, except for ubuntu which was mentioned beforehand

## python compatibility and availability

| python version    | availability                              | pistol versions compatible |
|-------------------|-------------------------------------------|----------------------------|
| python >=3.13     | not tested, should be available available | &gt;=1.0                   |
| python 3.12, 3.13 | tested, available                         | &gt;=1.0                   |
| python <=3.11     | tested, not available                     | no versions                |

## dependencies

- all dependencies should come preinstalled with pistol
- if a dependency is not installed, run `bucket dep install`
- if `bucket` is not installed, run `python -m pip install --upgrade pip`, then `pip install bkt` (on windows)
- if the issue persists, reinstall pistol by running `python -m pip install --upgrade pip`, then `pip install pistol --force`

## how to start pistol
### arguments
- all pistol start methods take one argument: `<location>`
- `<location>` means where pistol will start.
- if `<location>` is not specified, it will be defaulted to `last` as long as `persistent-location` is enabled. if `persistent-location` is not enabled, `<location>` is defaulted to `.`
- location can be for ex. `.`, `..`, `/home`, `/`, `~`, `C:/`, `./my_project`, `last`
- if `<location>` is set to `last`, it will use the location where you last logged off of `pistol`.
- location can also be `storage`, which will enter storage mode instantly.
- if you want to enter a directory named `storage` in `.`, specify `./storage` instead.
### method 1: windows, ubuntu/linux executable (recommended)
- use `pistol <location>`
- tested to work on both windows and linux if everything is set up correctly on the user's device.
- recommended for most use cases
- - quick to type
- - easy to remember
### method 2: windows run as python module
- use `python -m pistol <location>` or `py -m pistol <location>` or similar
- make sure `python` or `py` are linked to python 3.12 or higher using `python --version` or `py --version`
- if the output shows that the python version is lower than python 3.12, try installing the newest version [here](https://python.org)
- once installed, or if you are sure you have python 3.12 or higher installed already, try running `python<version> -m pistol <location>`
- `<version>` means the version of python you have installed.
- - examples: `python3.12`, `python3.13`, `python3.14`
- recommended for internal uses or debugging purposes
- - if the executable (method 1) does not work, this method should almost always work.
- - if it doesn't, try reinstalling or upgrading `pistol` using `pip install --force pistol` (to reinstall) or `pip install --upgrade pistol` (to upgrade)
- - if you are starting `pistol` from within a program, this method is recommended as it is more likely to work on other computers (assuming `pistol` is installed on that computer)
### method 3: ubuntu/linux run as python module
- basically the same at the method 2 (read above)
- run with `python3` instead of `python` or `py`
### method 4: windows, ubuntu/linux run from git clone
- applies only if you have run `git clone https://github.com/pixilll/pistol` or `gh repo clone pixilll/pistol` and are in the same cwd as where you have run that command
- same as method 2 (on windows) or method 3 (on ubuntu/linux) but you run `<executable> -m pistol.pistol <location>` instead.

## commands:
- cd - change current working directory
- ucd - undo last cd
- - example:
```
posix: /home/astridot/Desktop> cd ..
posix: /home/astridot> cd Documents/MyProject
posix: /home/astridot/Documents/MyProject>cd /home/astridot
posix: /home/astridot> cd /
posix: /> ucd
posix: /home/astridot> ucd
posix: /home/astridot/Documents> ucd
posix: /home/astridot> ucd
posix: /home/astridot/Desktop> exit
➤➤ exited pistol
```
- exit - exit pistol. this can also be done faster by pressing ^D chord to ^C
- help - go to the pistol documentation page
- cls, clear - clears the screen
- version - returns the current running version of pistol
- search - open an url in your browser
- - important: this may not work if you have a modified or manually built version of pistol. you can enable this using the following commands
```
solo git clone https://github.com/pixilll/pistol
buckshot install pistol/pistol/misc/plugins/search.js
```
- cdh - stands for cd history, displays your cd history and where the next `ucd` will take you
- ccdh - stands for clear cd history, clears the cd history
- whereami - see your current location (even in storage mode)
- - important: this may not work if you have a modified or manually built version of pistol. you can enable this using the following commands
```
solo git clone https://github.com/pixilll/pistol
buckshot install pistol/pistol/misc/plugins/whereami.js
```
- st - switch to storage mode
- pistol - only works in solo mode, executes commands in pistol
- - example: while in solo mode: `pistol whereami`
- - to start a pistol instance from solo mode, use `python3 -m pistol` instead
- root - changes the cwd to `/` or whatever the root directory of your system is
- rs - stands for reverse search, works somewhat like ^R in bash
- cch - stands for clear command history, clears the command history
- rmc - stands for remove command, removes a command from the command history
- alias - creates an alias for a command
- rma - stands for remove alias, removes an alias
- ca - stands for clear aliases, clears all aliases
- rms - stands for remove suggestion, removes a `scs` cache item
- cs - stands for clear suggestions, clears the `scs` cache
- meta - analyses the size of pistol's meta file
- prop - changes small key-boolean pairs in the meta files called 'props'
- - argument 1 is the name
- - argument 2 is the value
- - the value can be true, on, off, false, disabled, enabled, or similar
- - example: `prop my_prop true`
- prop (for plugins)
- - same command as normal prop
- - precede the plugin name with `plugin:`
- - example: `prop plugin:my_plugin true` - enables a plugin named `my_plugin` if it is installed
- - more info [here](https://github.com/pixilll/pistol/blob/main/CHANGELOG.md)
- shotgun - used to manage pistol plugins easily
- - more info [here](https://github.com/pixilll/pistol/blob/main/CHANGELOG.md)
- re - refreshes the meta file, run automatically after every command by default (can be disabled using `prop auto-re false`)
- ### solo
- - solo uses the system's default shell to run further commands
- - example:
```
<posix> /home/astridot/Desktop/Project> solo dir
pistol	README.md  setup.py
<posix> /home/astridot/Desktop/Project> solo ls
pistol	README.md  setup.py
<posix> /home/astridot/Desktop/Project> solo echo Hello, world!
Hello, world!
<posix> /home/astridot/Desktop/Project> solo cd ..
⚠️  warning: cd may not work properly when executing using solo
🚨 error: solo: [Errno 2] No such file or directory: 'cd'
<posix> /home/astridot/Desktop/Project> solo exit
⚠️  warning: exit may not work properly when executing using solo
🚨 error: solo: [Errno 2] No such file or directory: 'exit'
<posix> /home/astridot/Desktop/Project> solo help
⚠️  warning: help may not work properly when executing using solo
🚨 error: solo: [Errno 2] No such file or directory: 'help'
<posix> /home/astridot/Desktop/Project> solo
<posix> /home/astridot/Desktop/Project [solo]> echo hi
hi
<posix> /home/astridot/Desktop/Project [solo]> dir
pistol	README.md  setup.py
<posix> /home/astridot/Desktop/Project [solo]> ls
pistol	README.md  setup.py
<posix> /home/astridot/Desktop/Project [solo]> cd ..
⚠️  warning: cd may not work properly when executing using solo
🚨 error: solo: [Errno 2] No such file or directory: 'cd'
<posix> /home/astridot/Desktop/Project [solo]> exit
➤➤ Exited solo
<posix> /home/astridot/Desktop/Project> exit
➤➤ Exited pistol
```
note: the above terminal snippet may be out of date and some commands may behave differently then what is shown.
- #### what are types of solo
- - there are multiple types of solo
- - each type has the same concept, but different execution
- #### current types of solo
- - `solo` - standard execution
- - `pwsolo` - executes in powershell, regardless of operating system