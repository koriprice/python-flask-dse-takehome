import json
import os
from flask import Flask, session, redirect, render_template, request, url_for
import workos
from flask_socketio import SocketIO
from flask_lucide import Lucide

# Flask Setup
app = Flask(__name__)

lucide = Lucide(app)


app.secret_key = os.getenv("APP_SECRET_KEY")
base_api_url = os.getenv("WORKOS_BASE_API_URL")
directory_id = os.getenv("DIRECTORY_ID")

# WorkOS Setup
workos_client = workos.WorkOSClient(
    api_key=os.getenv("WORKOS_API_KEY"),
    client_id=os.getenv("WORKOS_CLIENT_ID"),
    base_url=base_api_url,
)

# Enter Organization ID here

CUSTOMER_ORGANIZATION_ID = "org_01KK5JPWGTT021NFDY7ZX1HQH4"  # Use org_test_idp for testing


def to_pretty_json(value):
    return json.dumps(value, sort_keys=True, indent=4)


app.jinja_env.filters["tojson_pretty"] = to_pretty_json


@app.route("/")
def login():
    try:
        return render_template(
            "login_successful.html",
            first_name=session["first_name"],
            last_name=session.get("raw_profile", {}).get("last_name"),
            raw_profile=session["raw_profile"]
        )
    except KeyError:
        return render_template("login.html")


@app.route("/auth", methods=["POST"])
def auth():

    login_type = request.form.get("login_method")
    if login_type not in (
        "saml",
        "GoogleOAuth",
        "MicrosoftOAuth",
    ):
        return redirect("/")

    redirect_uri = "http://localhost:5000/auth/callback"

    authorization_url = (
        workos_client.sso.get_authorization_url(
            redirect_uri=redirect_uri, organization_id=CUSTOMER_ORGANIZATION_ID
        )
        if login_type == "saml"
        else workos_client.sso.get_authorization_url(
            redirect_uri=redirect_uri, provider=login_type
        )
    )

    return redirect(authorization_url)


@app.route("/auth/callback")
def auth_callback():

    code = request.args.get("code")
    # Why do I always get an error that the target does not belong to the target organization?
    if code is None:
        return redirect("/")
    profile = workos_client.sso.get_profile_and_token(code).profile
    session["first_name"] = profile.first_name
    session["raw_profile"] = profile.dict()
    session["session_id"] = profile.id
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    session["raw_profile"] = ""
    return redirect("/")

@app.route("/directory")
def directory():
    try:
        # 1. Fetch directories linked to your Organization ID
        directories = workos_client.directory_sync.list_directories(
            organization_id=CUSTOMER_ORGANIZATION_ID
        )

        if not directories.data:
            return "No directory found for this organization. Please check your Okta SCIM setup.", 404

        # 2. Get the first directory (the one you set up with Okta)
        active_directory = directories.data[0]

        # 3. Render the template with the specific variables it expects:
        # 'directory' must be a dictionary for the |tojson_pretty filter
        # 'id' is used for the Users/Groups buttons
        return render_template(
            "directory.html", 
            directory=active_directory.dict(), # Convert object to dict for JSON printing
            id=active_directory.id
        )
        
    except Exception as e:
        # This will help you see the exact error in your terminal if it fails
        print(f"Directory Route Error: {e}")
        return f"An error occurred: {e}", 500

@app.route("/users")
def directory_users():
    directory_id = request.args.get("id")
    
    if not directory_id:
        return "No directory ID provided", 400
        
    try:
        # 1. Fetch users using the required keyword 'directory_id'
        users_resource = workos_client.directory_sync.list_users(directory_id=directory_id)
        
        # 2. Convert the entire resource to a dictionary.
        # This creates the {'data': [...], 'list_metadata': {...}} structure 
        # that your HTML template specifically looks for.
        users_dict = users_resource.dict()
        
        # 3. Debug check: print this to your terminal to confirm data exists
        print(f"Found {len(users_dict['data'])} users for directory {directory_id}")

        return render_template("users.html", users=users_dict)

    except Exception as e:
        print(f"Users Route Error: {e}")
        return f"Internal Error: {e}", 500


@app.route("/user")
def directory_user():
    user_id = request.args.get("id")
    if not user_id:
        return "No user ID provided", 400
    user = workos_client.directory_sync.get_user(user_id)

    return render_template("user.html", user=user.model_dump(), id=user_id)


@app.route("/groups")
def directory_groups():
    directory_id = request.args.get("id")
    groups = workos_client.directory_sync.list_groups(directory_id=directory_id, limit=100)

    return render_template("groups.html", groups=groups)


@app.route("/group")
def directory_group():
    group_id = request.args.get("id")
    if not group_id:
        return "No user ID provided", 400

    group = workos_client.directory_sync.get_group(group_id)

    return render_template("group.html", group=group.model_dump(), id=group_id)


@app.route("/events")
def events():
    after = request.args.get("after")
    events = workos_client.events.list_events(
        events=[
            "dsync.activated",
            "dsync.deleted",
            "dsync.group.created",
            "dsync.group.deleted",
            "dsync.group.updated",
            "dsync.user.created",
            "dsync.user.deleted",
            "dsync.user.updated",
            "dsync.group.user_added",
            "dsync.group.user_removed",
        ],
        after=after,
        limit=20,
    )

    after = events.list_metadata.after
    events_data = list(map(lambda event: event.model_dump(), events.data))
    return render_template("events.html", events=events_data, after=after)


@app.route("/webhooks", methods=["GET", "POST"])
def webhooks():
    signing_secret = os.getenv("WEBHOOKS_SECRET")
    if request.data:
        if signing_secret:
            payload = request.get_data()
            sig_header = request.headers["WorkOS-Signature"]
            response = workos_client.webhooks.verify_event(
                event_body=payload, event_signature=sig_header, secret=signing_secret
            )
            message = json.dumps(response.dict())
            socketio.emit("webhook_received", message)
        else:
            print("No signing secret configured")

    # Return a 200 to prevent retries based on validation
    return render_template("webhooks.html")