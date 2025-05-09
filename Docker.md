# Building your Docker image (Containerization)
A Dockerfile is just a set of instructions on how to build your container image s.t it can run consistently across different platforms and environments.

Instructions are executed during the build process, not runtime.

1. To containerize your application, you first need to create a Dockerfile in the following format
(IT MUST BE NAMED exactly "Dockerfile"!):
```yaml
# Use an official Python runtime as a parent image:
FROM python:3.12

# Set the working directory in the container (can be any path, even "/usr/src/apps"):
WORKDIR /apps

# Copy (all of) the current directory's contents into the container's working directory at: /apps:
COPY . .  # the 1st "." is (source) host path (current dir), 2nd "." is (target) path set by the "WORKDIR"

# Install any needed files or packages specified in requirements.txt:
RUN python3 -m pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 -m nltk.downloader stopwords

# Make port(s) available to the world outside this container:
EXPOSE 8000 5006  # whatever port(s) your app(s) listen to

# Define environment variable(s):
ENV NAME="Hello, World" MODE=production PORT=8000

# Run your app(s) when the container launches (SUBOPTIMAL):
# ("sh" invokes a shell (suboptimal), and "-c" is a command string)  
CMD sh -c 'python3 -m streamlit run scripts/app1.py --server.port 8000 --server.address=0.0.0.0 & python3 -m panel serve scripts/app2.py --port 5006 --address 0.0.0.0 --allow-websocket-origin=*'
```
### Important notes:
- `--server.address`: specifies which IP address(s) your app/server is allowed to listen to (accept connections from).
It can be set to a LAN IP (same public IPv4 for multiple devices) address, making it only reachable via that LAN IP (whitelist one IP to represent the whole LAN).
If set to `0.0.0.0`, it listens to all IPs (accepts connections from all external clients).
- `--allow-websocket-origin`: specifies which origins (protocol + domain) are allowed to open WebSocket connections to your app.
Relevant when accessing the app indirectly (not via raw IP), via a reverse proxy (domain name or intermediate server).
E.g. If the app is served at: `http://some.domain.com/yourapp:port_num`, WebSocket connections will be rejected without: `--allow-websocket-origin=some.domain.com:port_num`.
By default, the only allowed origin is: `localhost:5006`, hence if you change the `--server.address`, you have to `--allow-websocket-origin=--server.address:port_num`.
To allow multiple origins: `--allow-websocket-origin=192.168.x.x:5006,localhost:5006`.

2. Then you need to create a `.dockerignore` file (similar to `.gitignore`) to exclude certain files/folders from being copied into the image, reducing image size and speeding up build.

But running multiple apps (on the same host) using the approach above is **suboptimal** because `&` runs one app (process) in the background, causing it to be 
untracked by Docker (buggy). Hence, a more modular, efficient approach is to run each app in its own isolated container (each app has its own Dockerfile).

Use *Docker Compose* (requires `compose.yaml` file) to run multiple apps simultaneously in Docker containers:

File Structure:
```text
your-project/
│
├── compose.yaml
│
├── streamlit_app/
│   ├── Dockerfile
│   │── .dockerignore
│   ├── requirements.txt
│   └── app.py
│
└── panel_app/
    ├── Dockerfile
    │── .dockerignore
    ├── requirements.txt
    └── app.py
```
`streamlit_app/Dockerfile` Contents:
```yaml
FROM python:3.12

WORKDIR /app

COPY . .

RUN python3 -m pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["streamlit", "run", "app.py", "--server.port=8000", "--server.address=0.0.0.0"]
```
`panel_app/Dockerfile` Contents:
```yaml
FROM python:3.12

WORKDIR /app

COPY . .

RUN python3 -m pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 -m nltk.downloader stopwords

EXPOSE 5006

CMD ["panel", "serve", "app.py", "--address=0.0.0.0", "--port=5006", "--allow-websocket-origin=*"]
```
Docker Compose (`compose.yaml`) Contents:
```yaml
services:
  mystreamlit_service:
    build:
      context: ./streamlit_app
    image: maf/app1:latest
    ports:
      - "8000:8000"

  mypanel_service:
    build:
      context: ./panel_app
    image: maf/app2:latest
    ports:
      - "5006:5006"
```
3. Then to build your Docker image, run `docker-compose build` in the directory that contains
`compose.yaml` (for multi-container apps), or run `docker build -t <image_name>` in the 
directory that contains the Dockerfile (for single-container app).

4. Finally, to run your application(s), run:
- `$ docker compose up -d --build`: for multi-container apps
- `$ docker run -d -p 4000:8000 -p 5006:5006 <image_name>`: for single-container app
  - `-p 4000:8000`: maps the port 4000 on the host machine to port 8000 inside the container.
  - `-d`: runs everything in the background (detached mode) and return control to your terminal.
