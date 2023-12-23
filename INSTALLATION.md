# INSTALLATON #  
The installation instructions are specifically for Ubunto 22.04.03.  
 Windows, Mac, Android and other flavours of Linux will probably require different steps and commands.

The app requires Python3 and MySQL Server Ver 8.0.34 or higher to be installed, and that you have root/sudo access. 

**Install python3**  
$ sudo apt install python3, pip3

**Install MySQL**  
If MySQL isnt installed, refer to the installing_MySQL_HOWTO.md  

**Preparing the Environment**    
Navigate to the folder where you want to place the app and Create a directory where it will be installed. In this case its called 'capstone'  

```
mkdir capstone
```

create a virtual environment called '.venv'
```
python3 -m venv .venv
```

activate the virtual environment
```
$source .venv/bin/activate
```


## install necessary packages
**manually**
```
(.venv)$ pip3 install django
(.venv)$ pip3 install python-decouple
(.venv)$ pip3 install whitenoise
(.venv)$ pip3 install sqlparse
(.venv)$ pip3 install typing_extensions
(.venv)$ pip3 install asgiref
(.venv)$ pip3 install pillow
(.venv)$ pip3 install mysqlclient
(.venv)$ pip3 install rawpy
```

**automatic: requirements.txt**  
These Packages can be installed via the requirements.txt file. Navigate to the download folder or where the requirements.txt file is. Its important that the virtual environment is running when you do this, You want them installed in the app environment, not globally
```
(.venv) $ pip3 install -r requirements.txt
```
Check packages are installed. It should look like this
```
(.venv) pip3 freeze  

asgiref==3.7.2
Django==4.2.5
django-debug-toolbar==4.2.0
mysqlclient==2.2.0
numpy==1.26.2
Pillow==10.0.1
python-decouple==3.8
rawpy==0.19.0
sqlparse==0.4.4
typing_extensions==4.7.1
whitenoise==6.5.0
```

```

```

# Get The Hugry Hippo App #

Clone the App from Github into the Capstone folder
```
(.venv)$: cd capstone
(.venv)$: git clone https://github.com/JefMcD/hungry_hippo_app.git

```
**Install Database**  
navigate to the folder you cloned the app.  
Login to  mysql as root and run the database installation script 
The script deletes any previous instance and then creates the Hungry_Hippo_DB and a default Hungry_Hippo admin user;  


```
(.venv)$: mysql -u root -p
Enter password: ********

mysql> source /full/path/to/the/installation/capstone/hungry_hippo/sql/install_db.sql
```
**Default Admin Login is**  
User: chief  
Password: passw0rd  
Database: Hungry_Hippo_DB  
Once the database is installed, you can change the password and use this account to manage the database instead of root.


```
```
# Troubleshooting #  
**If the database needs to be cleared down and resinstalled**  
Inside the Django Project Directory    
delete __pycache__ fodler  
delete migrations folder  
**reinstall database**  using from the MySQL terminal with the install.sql script as previously described.  
Reset the Django database ORM with the following commands.
```
$ python3 manage.py makemigrations hungry_hippo_app
$ python3 manage.py migrate
$ python3 runserver
```

# Didn't Get Done #

## Download Docker Image (Not Yet Implemented)  
This is going to be some as yet not implemented Docker business

**Docker**  
The App will be developed and deployed using Docker containers with Kubernetes to ensure a consistent environment across all platforms and make deployment to any production host or cloud services go smoother. 

Cloud Services are;  
Main corporate BB Services: AWS, Azure, Google.  
Alternatives: Digital Ocean, CLoudVPS, Kahu, Bluelock, CloudSigma  

## Deployment (Currently Not Live) ##
The app will be deployed to a live production host which greatly increases complexity since once the App is deployed, the Static Data needs to be completely reconfigured for a production environment as well as the CSRF_Token middleware. This takes the project to the next level.  
  
Currently the plan is to deploy to PythonAnywhere which provides free hosting and is most excellent.






