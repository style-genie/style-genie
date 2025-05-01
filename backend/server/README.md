A Python FastAPI server

# 🔧 Developer Guide

## Requirements

* Python3.11
* OpenAI account
* Container Registry
* Compute instance


## Clone the repo

Connect your host to GitHub
1. [Create a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
    * `ssh-keygen -t ed25519 -C "your_email@example.com"`
    * `eval "$(ssh-agent -s)"`
    * `ssh-add ~/.ssh/id_ed25519`
2. [Add a new SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)
    * `cat ~/.ssh/id_ed25519.pub`
    * In GitHub, Settings / Access section, click  SSH and GPG keys. Click New SSH key or Add SSH key. In the "Title" field be creative. In the "Key" field, paste your public key.

```shell
git clone git@github.com:style-genie/style-genie.git
```

## Copy the environment variables to the project root

source: ask!

```shell
cat << EOF > .env.local
KEY1=VALUE1
KEY2=VALUE2
EOF
```


### Evaluate dependencies

```shell
(ls .env.local && echo 'INFO: Found .env.local') || echo 'CRITICAL: Missing .env.local'
(ls requirements.txt && echo 'INFO: Found requirements.txt') || echo 'CRITICAL: Missing requirements.txt'
```


## Create Python environment and install dependencies

```shell
cd /path/to/project
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```


### 🏃 Running Locally

```shell
cd /path/to/project
uvicorn src.main:app --reload
```

Access the interactive API documentation at `http://localhost:8000/docs`

### Deploy with Docker

Ensure Docker daemon is running on your machine.

```shell
# Build the image
docker build -t stylegenie/$IMAGE_NAME .
# Quick test
docker run -p 80:80 stylegenie/$IMAGE_NAME
```

```shell
# Log into Container Registry 
docker login https://$DOMAIN/$CR -u $CR_USER -p $CR_PASS

# [OPTIONAL] Pull yout latest image if not already on the machine
docker pull stylegenie/$IMAGE_NAME
# on macOS you might need the suffix `--platform linux/x86_64`

# Tag and Push your image to Container Registry
docker tag $IMAGE_NAME:latest $DOMAIN/$CR/$IMAGE_NAME:latest
docker push $DOMAIN/$CR/$IMAGE_NAME:latest
```

On the server ensure docker is installed

```shell
apt  install docker.io

# create user `docker`
useradd -m -g users docker

# create user group `dockergroup`
sudo addgroup dockergroup

# add users to user group
usermod --append --groups dockergroup docker
usermod --append --groups dockergroup $ADMIN_USER

# switch to the `docker` user
su - docker
```

```shell
# Log into Container Registry 
docker login https://$DOMAIN/$CR -u $CR_USER -p $CR_PASS

# Pull yout latest image
docker pull $DOMAIN/$CR/$IMAGE_NAME
# on macOS you might need the suffix `--platform linux/x86_64`

# List all images available locally
docker images

# List all containers
docker ps -a

# :WARNING: Stop all containers
docker stop $(docker ps -q)
# :WARNING: Remove all containers
docker rm $(docker ps -a -q)

# Run image in detached mode
docker run -d --name $CONTAINER_NAME -p 80:80 $DOMAIN/$CR/$IMAGE_NAME

## Example Query

To get a clothing recommendation, you can use the following curl command:

```shell
curl "http://localhost:1500/recommendation?query=What should I wear to a party?"
```
