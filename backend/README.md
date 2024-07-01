1. Install the requirements: <br>
    **IMPORTANT !** <br>
    For compatibility reasons with the model , please use **python 3.10** as a version

    Create a python virtual environment (to avoid packages conflict with the system):
    - pip install virtualenv
    - python3.10 -m venv <venv_name>
    - source <venv_name>/bin/activate
    - pip install -r ./backend/requirements.txt

    Additionally, install **unixodbc** driver manager
    - Linux(ubuntu): **sudo apt install unixodbc**
    - macOS : **brew install unixodbc**

    Fore more information , check this [link](https://docs.teradata.com/r/Teradata-Package-for-R-User-Guide/July-2021/Connecting-to-Vantage-with-Teradata-ODBC-Driver/Installing-and-Configuring-Teradata-ODBC) (it also includes installation guides for other linux distributions and windows operating systems)

2. Provision the following resources in Microsoft Azure:
- Azure SQL DB 
- Azure Blob Storage

3. Fill the **.env_template** with the required variables (then rename the file to **.env**)
3. Connect to Azure SQL DB: 
- install the ODBC SQL driver : run the script **installODBCDriver.sh**
- install required python packages : **pip install -r azureSQLrequirments.txt**


4. Create Service Principal to make the application auto-authenticate with azure and thus access the resources: 

    1. authenticate to your azure account using : **az login**

    2. create service principal using :**az ad sp create-for-rbac --name "App Name" --role contributor --scopes /subscriptions/{subscription_id}**

5. run the application using **python3.10 app.py**
