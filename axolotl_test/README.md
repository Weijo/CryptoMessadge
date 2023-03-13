# Install python-axolotl
## Linux

You need to have python headers installed, usually through installing a package called `python-dev`, then as superuser run:
```
git clone https://github.com/tgalal/python-axolotl
python setup.py install
```

## Windows
 - ```git clone https://github.com/tgalal/python-axolotl```
 - Install [MinGW](https://sourceforge.net/projects/mingw/) compiler
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

# Install Dependencies
```
pip install -r requirements.txt
```

# Usage
_Note: Use cmd for Windows or terminal for Linux_
- Start the server
  ```
  # Server terminal
  python server.py
  ```
- Register client key with server
  ```
  # Alice terminal
  python client_x.py
  Enter your username: alice

  # Bob terminal
  python client_x.py
  Enter your username: Bob
  ```
- Select the user to talk to
  ```
  # Alice terminal
  Enter a username to talk to: bob

  # Bob terminal
  Enter a username to talk to: alice
  ```
- Alice and Bob can now start chatting!

