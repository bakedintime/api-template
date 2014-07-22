Dependencies
--------
- Python 2.7
- Setuptools
- Pip
- Virtualenv

Installation
--------

1. Install python on machine.
2. On windows, add python to Environment variables. Assuming Python 2.7,
both folder path (c:\Python27) and Scripts folder (c:\Python27\Scripts).
3. Install setuptools and pip.
4. Install virtualenv:

        pip install virtualenv

5. Setup virtualenv on the above folder: 

        cd ..
        virtualenv venv

6. Enter the virtual environment:

        cd segurosAPI

    on Windows:

        ..\venv\Scripts\activate

    on *nix:

        . ../venv/bin/activate or source ../venv/bin/activate, if supported.

7. if not present, install git

From within virtual environment

8. Clone repository (Assuming ssh-keys are already added):

        git clone git@git.tir:seguros/seguro***REMOVED***pi.git

9. Install requirements:

        pip install -r requirements.txt

10. Change ip configuration:

    Change to the according ip address from the server in the following files:
    webserver.py (line 51)
    static/index.html (line 23)

11. Run server:

        python webserver.py

Deployment On *nix
--------
1. Install supervisor
2. Install nginx
3. Copy supervisor example conf from conf folder:

        cp conf/supervisord.conf.example /etc/supervisor/supervisord.conf.example

4. Replace default conf file with the example
5. Reload supervisor and start the process

        sudo supervisorctl reload
        sudo supervisorctl status (Check if is running otherwise: sudo supervisorctl start seguro***REMOVED***pi) 

6. If the status shows an unsuccessful mes***REMOVED***ge, check the logs:

        tail -200 /var/log/supervisor/seguro***REMOVED***pi/out.log

Troubleshooting
--------
If virtualenv venv fails to execute with an error like:
    Filename x does not start with any of these prefixes.
Try removing the PYTHONPATH variable from Environment variables.

If there are problems with pyodbc like 
        
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "build/bdist.linux-i686/egg/pyodbc.py", line 7, in <module>
          File "build/bdist.linux-i686/egg/pyodbc.py", line 6, in __bootstrap__
        ImportError: libodbc.so.2: cannot open shared object file: No such file or directory

run: 
        sudo apt-get update && sudo apt-get install unixodbc-dev libmyodbc