###### To containerize your application, you first need to create a Dockerfile in the following format:
	IT MUST BE NAMED "Dockerfile" excatly!!!

'''
# Use an official Python runtime as a parent image:
FROM python:3.12

# Set the working directory in the container (can be any path, even "/app"):
WORKDIR /usr/src/app

# Copy (all of) the current directory's contents into the container's working directory at: /usr/src/app:
COPY . .  # the 1st "." is (source) host path (current dir), 2nd "." is (target) path set by the "WORKDIR"

# Install any needed packages specified in requirements.txt:
RUN pip install --no-cache-dir -r requirements.txt

# Make port(s) available to the world outside this container:
EXPOSE 8000 5006  # whatever port(s) your app(s) listen to

# Define environment variable(s):
ENV NAME World

# Run your app(s) when the container launches:
CMD sh -c 'python -m streamlit run scripts/app1.py --server.port 8000 & python -m panel serve scripts/app2.py --port 5006 --address 0.0.0.0 --allow-websocket-origin=*'

# where "sh" invokes a shell, and "-c" is a command string  
'''

###### Then you need to create a `.dockerignore` file (similar to `.gitignore`)

###### Then navigate to directory containing the files and run:
`$ docker build -t give_any_image_name .`

##### Finally, to run your application, run:
`$ docker run -p 4000:8000 -p 5007:5007 given_image_name`
The `-p 4000:8000` maps the port 4000 on the host machine to port 8000 inside the container
(it can also be mapped to the same port `-p 8000:8000`)
