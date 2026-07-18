#Every Dockerfile starts with the base image, a pre-built starting point. 
#python:3.12-slim is the official Python 3.12 image, slim meaning it's a stripped down version with only the essentials.
#We use slim to keep the container as lightweight as possible, leaving more resources for services such as Jellyfin, ClamAV, etc.
FROM python:3.12-slim

#Switches the working directory inside the container to /app. 
#Every command after this runs from that folder.
WORKDIR /app

#Copies just the requirements.txt file from your local machine into the container. 
#We copy this first, before the rest of the code, since Docker caches each step. 
#If the code is changed but requirements.txt doesn't, Docker skips reinstalling packages and goes straight to copying the new code,
# making rebuilds much faster.
COPY requirements.txt .

#Installs all the Python libraries listed in requirements.txt inside the container.
#--no-cache-dir means pip doesn't store the downloaded packages after installing them, keeping the container smaller.
RUN pip install --no-cache-dir -r requirements.txt

#Copies the rest of the backend code into the container.
COPY . .

#Docker is set to listen on port 8000 for the container.
EXPOSE 8000

#The command that runs when the container starts:
    #uvicorn, which the server that runs FastAPI
    #app.main:app, which looks inside the app folder, in main.py, find the object called app
    #--host 0.0.0.0 — listen on all network interfaces, not just localhost, so the container is reachable from outside
    #--port 8000 — listen on port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
