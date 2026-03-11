# python-flask-dse-takehome

This is an example Flask application demonstrating how to use the [WorkOS Python SDK](https://github.com/workos/workos-python) to implement SSO and Directory Sync using Okta. 

## Prerequisites

- Python 3.6+
- A WorkOS Dashboard Account
- An Okta Developer Account
- Follow the [SSO authentication flow instructions](https://workos.com/docs/sso/guide/introduction) to set up an SSO connection.
    - When you get to the step where you provide the `REDIRECT_URI` value, use http://localhost:5000/auth/callback.
- Follow the [Create a New Directory Connection](https://workos.com/docs/directory-sync/guide/create-new-directory-connection) step in the WorkOS Directory Sync guide.

*The SSO authentication and Directory Sync must both be set up in the same WorkOS Organization with the same Okta developer account*

# Running the Example App Locally

1. Clone the git repo using: 
   
   ```bash
   # HTTPS
   $ git clone https://github.com/koriprice/python-flask-dse-takehome.git
   ```

   or

   ```bash
   # SSH
   $ git clone git@github.com:koriprice/python-flask-dse-takehome.git
   ```

2. Create a Python virtual environment:

   ```bash
   $ python3 -m venv env
   ```

3. Source the Python virtual environment:

    ```bash
   $ source env/bin/activate
   (env) $
   ```
   
   or

   ```bash
   $ source env/Scripts/activate
   (env) $
   ```
   if running on Windows


4. Install the cloned app's dependencies.
  
   ```bash
   (env) $ pip install -r requirements.txt
   ```

5. Retrieve the following values from your WorkOS Dashboard account:
    - Your [WorkOS API key](https://dashboard.workos.com/api-keys)
    - Your [SSO-specific, WorkOS Client ID](https://dashboard.workos.com/configuration)

6. In the root directory of this example app, `python-flask-dse-takehome/`. Create a `.env` file to securely store the environment variables.
    ```
    WORKOS_API_KEY='your_workos_api_key'
    WORKOS_CLIENT_ID='your_workos_client_id'
    APP_SECRET_KEY='your_secret_key'
    ```
    *The APP_SECRET_KEY can be any string value*

8. Source the environment variables so they are accessible to the operating system.

   ```bash
   (env) $ source .env
   ```

9. In the `app.py` file, change the `CUSTOMER_ORGANIZATION_ID` value to the ID of the WorkOS Organization you will be using. This is the Organization where you set up SSO and Directory Sync using Okta as part of the prerequisites. The Organization ID can be found in your WorkOS Dashboard. 

10. Start the server
    
    ```bash
    (env) $ flask run
    ```

11. Navigate to `localhost:5000`, or `localhost:5001` depending on which port you launched the server, in your web browser. 

# Successfull Integration Capabilities

If you have successfully integrated SSO and Directory Sync, and have successfully run the app locally, you will be able to do the following:

After navigating to your local app, the first page will prompt you to log in. To confirm the SSO integration was successful, log in with the "Enterprise SAML" button at the bottom of the page. This will prompt you to log in using Okta.

After successfully logging in, you will see a Profile Details page. 

*Page updated from the original WorkOS template to explicitly show user first and last name in addition to raw profile data*

From this Profile page, you can click the "View Directory" button in the top right to navigate to your Okta Directory. This will take you to the "Directory Details" page, which displays the raw directory data. 

From the "Directory Details" page, you can click the "Users" button in the bottom left. 

This will take you to a list of all the users in the associated directory.

*The users page was updated from the original WorkOS template to correctly display the user emails*

You also have an option to view each user to get see their complete raw profile data. 

# Video Example

The following video is an example of what this app should look like when run locally after successfully implementing SSO and Directory Sync.

[Watch here](https://www.youtube.com/watch?v=57pBt-J6_0w)

# Credits & Resources
This application is built upon the foundation of the [official WorkOS Python Example Applications.](https://github.com/workos/python-flask-example-applications?tab=readme-ov-file) It specifically extends the [SSO](https://github.com/workos/python-flask-example-applications/tree/main/python-flask-sso-example) and [Directory Sync](https://github.com/workos/python-flask-example-applications/tree/main/python-flask-directory-sync-example) examples into a single application.
