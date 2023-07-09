# HowManyContenderAPI
Code for the server I use to get all data I need from Nadeo API

## Steps to install

### On debian based OS

1. Install python 3.11 

```bash 
sudo apt install python3.11
```

2. Install virtualenv

```bash
sudo apt install virtualenv
```

3. Create virtual environment

```bash
virtualenv -p /usr/bin/python3.11 env
```

4. Activate virtual environment

```bash 
source env/bin/activate
 ```

5. Install all requirements of the server

```bash
 pip install -r requirements.txt
```

6. Create src/utils/authenticate.txt file

> This file only contains one line : email@adress.com:password
> <br>Email and password are the identifiers of the Ubisoft connect account you want to use

7. Start server
```bash
python App.py
```

## License
2023 Martin CORNU-MANSUY martin2001.cornumansuy@gmail.com

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

