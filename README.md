# pinbackup is simple backup solution for you pinterest boards
Application require ability to get enviroment variable PINTEREST_TOKEN with token 
who should be making through https://developers.pinterest.com/tools/access_token/ 
with read_public permission. Only public boards!!!
Application create directory "~/pinterest" and backup your boards with pins.
Next attempt write our pins if they been update Simple install and using:

```
python setup.py install
```

```bash
export PINTEREST_TOKEN="AAABBBBaaaaa..."
pbackup
```
