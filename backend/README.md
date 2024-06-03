For connecting to Azure SQL DB, you need to : 
- install the ODBC SQL driver : run the script **installODBCDriver.sh**
- install required python packages : **pip install -r azureSQLrequirments.txt**


Creating Service Principal : 

1. **az login**

2. **az ad sp create-for-rbac --name "App Name" --role contributor --scopes /subscriptions/{subscription_id}**

    az ad sp create-for-rbac --name "embryo_app" --role contributor --scopes /subscriptions/d203f531-849f-4cc5-96e3-bf163d2fd5a7