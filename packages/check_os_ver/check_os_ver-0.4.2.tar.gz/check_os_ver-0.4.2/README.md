# check_os_ver

```


                                                    #*###*#
                                                    **#***#
                                                  *=**#+#*
                                          *@##**#**%%%***#
                                  @@@@@@#++++++*%#*+%%+*++%
                                 @@@@@@@%+++++++++++++++++*
                                 @@@@@@@@+++++++++++++++++#
                                 @@@@@@@@*++++++++++++++++#
                                  @@@@@@%++++++++++++*+**+*
                                   @@@@#+++++++++++*#***++*
                                      %%#***++++*******+++*
                                           *#**+++*****###**
                                           *++*##*####+=====#
                                          +*++++++======+++=++
                                          *#============+*++=+
                                          ++#+++==+=====*+==+*
                                           *#*#%%%###%%%#+=+*
                                            *++**%#*+++=++++%
                                            %+===+++++====++*
                                             *=+==+*======++@
                                             *+=+==*+=++==+*#
                                              =+***+#**++++##
                                              +++======----=+
                                           %----*####@%#%#%*#
                                            =----###--=-+####
                                             @##%@#++=====+*


```
## Use

### Use - osver: Print OS version
```bash
$ pip install check_os_ver
$ python
>>> from check_os_ver.osver import get_os_version
>>> get_os_version()
```

### Use - hi: Print "Chill guy"
```python
$ pip install check_os_ver
$ python
>>> from check_os_ver.hi import hi
>>> hi()
```

### Use - random_pic: Print "Random pic"
```python
$ pip install check_os_ver
$ python
>>> from check_os_ver.hi import random_pic as rp
>>> rp()
```

## Development environment settings
```bash
# install PDM
# git clone ...
$ source .venv/bin/activate
$ pdm install
# $ vi ...

# TEST
$ pip install
$ pdm test
$ pip install .

$ git add <FILE_NAME>
$ git commit -a
$ git push
$ pdm publish

View at:
https://pypi.org/project/check_os_ver/0.4.2/

# PR - Merge
# Tag - Release
```

## TEST
```bash
# $ pdm add -dG test pytest pytest-cov
$ pytest
$ pytest -s
$ pytest --cov
```

## Ref
- https://pdm-project.org/en/latest/
- https://packaging.python.org/en/latest/tutorials/packaging-projects/
- console_scripts
