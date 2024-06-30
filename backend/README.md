1. Install the requirements: 

    **python3.10 -m pip install requirements.txt** 

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

        az ad sp create-for-rbac --name "embryo_app" --role contributor --scopes /subscriptions/d203f531-849f-4cc5-96e3-bf163d2fd5a7
5. run the application using **python3.10 app.py**