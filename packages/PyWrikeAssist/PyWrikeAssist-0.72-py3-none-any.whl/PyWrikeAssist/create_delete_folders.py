import pandas as pd
import numpy as np
import requests
from PyWrike.gateways import OAuth2Gateway1
from PyWrike import (
    validate_token,
    authenticate_with_oauth2,
    get_folder_id_by_name,
    get_subfolder_id_by_name,
    create_wrike_project,
    create_wrike_folder,
    delete_wrike_folder,
    delete_wrike_project,
    get_responsible_id_by_name_and_email,
    delete_wrike_folder_by_id,
    get_folder_id_by_paths_2,
    get_space_id_by_name
)

def create_and_delete():
    # Prompt user for Excel file path
    excel_file = input("Enter the path to the Excel file: ")

    try:
        # Load data from the Excel sheets
        config_df = pd.read_excel(excel_file, sheet_name="Config", header=1)
        project_df = pd.read_excel(excel_file, sheet_name="Projects")
        print("Excel file loaded successfully.")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Retrieve configuration data
    access_token = config_df.at[0, "Token"]
    folder_path = config_df.at[0, "Project Folder Path"]
    space_name = config_df.at[0, "Project Folder Path"]  # Assuming you have a space name in Config

    # Validate or refresh access token
    if not validate_token(access_token):
        client_id = config_df.at[0, "Client ID"]
        client_secret = config_df.at[0, "Client Secret"]
        redirect_url = config_df.at[0, "Redirect URL"]
        access_token = authenticate_with_oauth2(client_id, client_secret, redirect_url)
        if not access_token:
            print("Authentication failed. Exiting.")
            return

    # Get space ID
    space_id = get_space_id_by_name(space_name, access_token)
    if not space_id:
        print("Space ID not found. Please check the space name in the configuration.")
        return

    # Handle Deletion
    print("\n--- Starting Deletion Process ---")
    for index, row in project_df.iterrows():
        delete_folder_path = row.get("Delete Folder Path")
        if pd.notna(delete_folder_path):
            print(f"\nProcessing deletion for path: '{delete_folder_path}'")
            target_folder_id = get_folder_id_by_paths_2(delete_folder_path, space_id, access_token)
            if target_folder_id:
                delete_wrike_folder_by_id(access_token, target_folder_id)
            else:
                print(f"Could not resolve folder path: '{delete_folder_path}'. Skipping deletion.")

    # Handle Creation
    print("\n--- Starting Creation Process ---")
    for index, row in project_df.iterrows():
        project_name = row.get("Create Project Title")
        folder_name = row.get("Create Folders")
        first_name = row.get("First Name")
        last_name = row.get("Last Name")
        email = row.get("Email")
        start_date = row.get("Start Date")
        end_date = row.get("End Date")

        # Skip rows without project creation details
        if pd.isna(project_name):
            continue

        # Convert timestamps to strings
        start_date = start_date.strftime('%Y-%m-%d') if pd.notnull(start_date) else None
        end_date = end_date.strftime('%Y-%m-%d') if pd.notnull(end_date) else None

        # Get parent folder ID based on the configured project folder path
        parent_folder_id = get_folder_id_by_paths_2(folder_path, space_id, access_token)
        if not parent_folder_id:
            print(f"Parent folder path '{folder_path}' could not be resolved. Skipping project creation.")
            continue

        # Check if the project or standalone folder already exists
        project_id = get_subfolder_id_by_name(parent_folder_id, project_name.strip(), access_token)
        if not project_id:
            print(f"Project '{project_name}' not found. Creating it.")
            if pd.isna(first_name) and pd.isna(last_name) and pd.isna(email) and not start_date and not end_date:
                project_id = create_wrike_folder(access_token, parent_folder_id, project_name.strip())
            else:
                responsible_id = get_responsible_id_by_name_and_email(first_name, last_name, email, access_token)
                if responsible_id:
                    project_id = create_wrike_project(
                        access_token, parent_folder_id, project_name.strip(), responsible_id, start_date, end_date
                    )
        else:
            print(f"Project '{project_name}' found with ID: {project_id}")

        # If the project or folder exists or was created successfully, create subfolders
        if project_id and pd.notna(folder_name):
            existing_subfolder_id = get_subfolder_id_by_name(project_id, folder_name.strip(), access_token)
            if not existing_subfolder_id:
                print(f"Creating subfolder '{folder_name}' in project/folder '{project_name}'")
                create_wrike_folder(access_token, project_id, folder_name.strip())
            else:
                print(f"Subfolder '{folder_name}' already exists in '{project_name}' with ID: {existing_subfolder_id}")

if __name__ == "__create_and_delete__":
    create_and_delete()
