# Install python-axolotl
## Linux

You need to have python headers installed, usually through installing a package called `python-dev`, then as superuser run:
```
git clone https://github.com/tgalal/python-axolotl
python setup.py install
```

## Windows
 - ```git clone https://github.com/tgalal/python-axolotl```
 - Install [mingw](https://sourceforge.net/projects/mingw/) compiler
 - Add mingw to your PATH
 - In PYTHONPATH\Lib\distutils create a file called distutils.cfg and add these lines:
 
    ```
    [build]
    compiler=mingw32
    ```

 - Install gcc: ```mingw-get.exe install gcc```
 - Install [zlib](http://www.zlib.net/)
    - You can use this repo to download zlib easily (https://github.com/horta/zlib.install)
    - Make sure you have CMake: https://cmake.org/download/
 - ```python setup.py install```


# Usage
- Open cmd.exe (for windows)
```
python server.py
python client_alice.py
python client_bob.py
```
