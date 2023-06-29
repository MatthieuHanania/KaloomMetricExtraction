import json
import math
import os
import requests
from datetime import datetime


def save_json_responses_to_file(project_id, merge_requests,gitlabAuth):
    """
    Save the merge requests data to a JSON file.

    Args:
        project_id (str): ID of the project.
        merge_requests (list): List of merge requests.

    Returns:
        None
    """
    file_path = "data/merge_requests_" + str(project_id) + ".json"

    #Check if the filepath exists
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Check if the file already exists
    if os.path.exists(file_path):
        # Read the existing data from the file
        with open(file_path, "r") as file:
            existing_data = json.load(file)

        # Append new data to the existing data
        existing_data.extend(merge_requests)
        merge_requests = existing_data
    else:

        merge_requests.insert(0,{"Project_creation_date":get_project_creation_date(project_id,gitlabAuth)})

    # Save the updated data to the file
    with open(file_path, "w") as file:
            json.dump(merge_requests, file, indent=4)


def print_json_schema(merge_requests):
    """
        Print the JSON schema of the merge requests data.

        Args:
            merge_requests (list): List of merge requests.

        Returns:
            None
        """
    # Get the first merge request from the list
    sample_merge_request = merge_requests[0]
    # Generate and print the JSON schema
    json_schema = generate_json_schema(sample_merge_request)
    print(json.dumps(json_schema, indent=4))


def generate_json_schema(data):
    """
        Generate JSON schema for the given data.

        Args:
            data (dict or list): Data to generate the schema for.

        Returns:
            dict: JSON schema.
        """
    if isinstance(data, dict):
        schema = {
            "type": "object",
            "properties": {}
        }
        for key, value in data.items():
            schema["properties"][key] = generate_json_schema(value)
        return schema
    elif isinstance(data, list):
        schema = {
            "type": "array",
            "items": generate_json_schema(data[0]) if len(data) > 0 else {}
        }
        return schema
    else:
        return {"type": "string"}


def get_merge_requests_page(project_id, access_token,page_number,start_date,end_date):
    """
    Retrieve merge requests data for a specific project.

    Args:
        project_id (str): ID of the project.
        access_token (str): Access token for GitLab API.
        page_number (int): Page number of merge requests to retrieve.

    Returns:
        None
    """
    # GitLab API endpoint for merge requests
    merge_requests_api_url = f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests"

    # Request headers
    headers = {
        "Private-Token": access_token
    }

    # Query parameters
    params = {
        "page": page_number,
        "per_page": 20  # Assuming 20 merge requests per page
    }

    # Send GET request to the merge requests API
    response = requests.get(merge_requests_api_url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        merge_requests = response.json()

        organized_merge_requests = []
        # organized_merge_requests.append({"project_creation_date":get_project_creation_date(project_id,access_token)})
        for merge_request in merge_requests:
            merge_request_id = merge_request.get("iid")

            # Request merge request details
            merge_request_api_url = f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{merge_request_id}"
            merge_request_response = requests.get(merge_request_api_url, headers=headers)
            merge_request_details = merge_request_response.json()


            if end_date :
                if  datetime.strptime(merge_request_details["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')< start_date:
                    #stop the function when the merge request is before the first date to vizualise
                    save_json_responses_to_file(project_id, organized_merge_requests,access_token
                    )
                    print("finish")
                    return True
                
                if not (start_date <= datetime.strptime(merge_request_details["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')<= end_date): 
                    #If a start date is specified and the merge request creation date is not on the interval, the processus is not done
    
                    continue
                        
            # Construct the organized merge request object

            organized_commit = {
                "commit_id": "",
                "details": "",
                "changesHist":[]
            }
            list_commit=[]

            organized_merge_request = {
                "merge_request_id": merge_request_id,
                "details": merge_request_details,
                "commits": [],
                "discussions": [],
                "notes": [],
                "changes": []
            }

            # Request commits for the merge request
            commit_response = requests.get(
                f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/commits",
                headers=headers)
            commits = commit_response.json()
            for commit in commits:
                commit_id= commit.get("short_id")
                commit_detail=requests.get(f"https://gitlab.com/api/v4/projects/{project_id}/repository/commits/{commit_id}/diff",
                headers=headers)
                organized_commit["commit_id"]=commit_id
                organized_commit["details"]=commit_response.json()
                organized_commit["changesHist"]=commit_detail.json()
                list_commit.append(organized_commit)

            organized_merge_request["commits"] = list_commit

            # Request discussions for the merge request
            discussion_response = requests.get(
                f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/discussions",
                headers=headers)
            discussions = discussion_response.json()
            organized_merge_request["discussions"] = discussions

            # Request notes for the merge request
            notes_response = requests.get(
                f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/notes",
                headers=headers)
            notes = notes_response.json()
            organized_merge_request["notes"] = notes

            # Request changes for the merge request
            change_response = requests.get(
                f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/changes",
                headers=headers)
            changes = change_response.json()
            organized_merge_request["changes"] = changes

            organized_merge_requests.append(organized_merge_request)

        #print_json_schema(organized_merge_requests)
        save_json_responses_to_file(project_id, organized_merge_requests,access_token)

    else:
        print(f"Error: {response.status_code} - {response.text}")

    return False


def get_project_creation_date(project_id, access_token):
    """
        Get the creation date of a project.

        Args:
            project_id (str): ID of the project.

        Returns:
            str: Creation date of the project in ISO 8601 format.
                None if the request was unsuccessful.
        """

    # GitLab API endpoint for project details
    project_api_url = f"https://gitlab.com/api/v4/projects/{project_id}"

    # Request headers
    headers = {
        "Private-Token": access_token
    }

    # Send GET request to the project details API
    response = requests.get(project_api_url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        project_details = response.json()
        creation_date = project_details.get("created_at")
        return creation_date
    else:
        print(f"Error: {response.status_code} - {response.text}")


def get_project_end_date(project_id):
    """
        Get the end date of a project based on the latest event.

        Args:
            project_id (str): ID of the project.

        Returns:
            str: End date of the project in ISO 8601 format.
                None if the request was unsuccessful or no events found.
        """
    # GitLab API endpoint for project events
    project_events_api_url = f"https://gitlab.com/api/v4/projects/{project_id}/events"

    # Request headers
    headers = {
        "Private-Token": ""
    }

    # Send GET request to the project events API
    response = requests.get(project_events_api_url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        events = response.json()
        if events:
            last_event = events[-1]
            end_date = last_event.get("created_at")
            return end_date
    else:
        print(f"Error: {response.status_code} - {response.text}")


def getGlobalNBMR(project_id, accessToken):
    # GitLab API endpoint
    merge_requests_api_url = f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests"

    # Request headers
    headers = {
        "Private-Token": accessToken
    }
    params = {'per_page': 1, 'page': 1}
    response = requests.get(merge_requests_api_url, headers=headers, params=params)

    # Check response and extract the total count
    if response.status_code == 200:
        total_count = int(response.headers.get('X-Total'))
        return total_count
    else:
        print(f'Error: {response.status_code} - {response.text}')
        return None


def getnbpage(nbMr, nbMrperPage):
    return math.ceil(nbMr / nbMrperPage)


def get_merge_requests(project_id, access_token,start_Date_Vizu = None,end_dateVizu = None):
    global_mr_nb = getGlobalNBMR(project_id, access_token)
    global_page_nb = getnbpage(global_mr_nb, 20)
    print(global_page_nb)
    for page in range(1, global_page_nb + 1):
        is_Finish = get_merge_requests_page(project_id, access_token, page,start_Date_Vizu,end_dateVizu)
        if is_Finish : break
