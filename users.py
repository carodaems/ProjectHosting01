from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import requests

app = FastAPI()


class UserCreate(BaseModel):
    username: str
    password: str


def create_rancher_namespace(user_name):
    # Rancher API endpoint and access credentials
    rancher_endpoint = "https://172.26.192.26/v3"
    access_key = "token-n9bvc"
    secret_key = "jxglwtvs646msttkh99ktlxv29855lxrfcx2mlfhcnshkxw7n8zm7l"

    # API request parameters
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_key}:{secret_key}"
    }
    payload = {
        "name": user_name,
        "projectId": "3c255cd4-caec-4de2-a4e6-5b8e5f8a5f0c"  # Replace with your project ID
    }

    # Make API request to create the namespace
    try:
        response = requests.post(
            f"{rancher_endpoint}/namespaces",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        print(f"Namespace '{user_name}' created successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Failed to create namespace: {str(e)}")


@app.post('/users')
def create_user(user: UserCreate):
    username = user.username
    password = user.password

    # NFS share settings
    nfs_share = '/mnt/nfs_share/users'

    try:
        # Create the user and home folder on the NFS share
        create_user_command = f'useradd -m -p {password} -d {nfs_share}/{username} {username}'
        create_folder_command = f'mkdir -p {nfs_share}/{username} && chown {username}:{username} {nfs_share}/{username}'

        subprocess.run(create_user_command, shell=True, check=True)
        subprocess.run(create_folder_command, shell=True, check=True)

        return {'message': f"User '{username}' created successfully."}

    except subprocess.CalledProcessError as e:
        return {'message': f"Failed to create user: {e}"}


@app.post('/namespaces')
def create_namespace(user: UserCreate):
    username = user.username
    create_rancher_namespace(username)
    return {'message': f"Namespace '{username}' created successfully."}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
