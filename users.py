from fastapi import FastAPI
from pydantic import BaseModel
import subprocess

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

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
