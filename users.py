from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import requests

app = FastAPI()


class UserCreate(BaseModel):
    username: str
    password: str


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


class UsersList(BaseModel):
    users: list[UserCreate]


@app.post('/users/batch')
def create_users(users_list: UsersList):
    users = users_list.users
    success_count = 0
    failure_count = 0
    result_messages = []

    for user in users:
        response = create_user(user)
        if 'message' in response:
            if 'created successfully' in response['message']:
                success_count += 1
            else:
                failure_count += 1
            result_messages.append(response['message'])

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'result_messages': result_messages
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
