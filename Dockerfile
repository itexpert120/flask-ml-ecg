#Create a ubuntu base image with python 3 installed.
FROM python:3.12.7

#Set the working directory
WORKDIR /

#Install the dependencies
RUN apt-get -y update
RUN apt-get update && apt-get install python3 python3-pip -y
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 git  -y

# git lfs
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash
RUN apt-get install git-lfs -y

#copy all the files
COPY . .
COPY .git/ .git
RUN git lfs install
RUN git fetch --prune
RUN git checkout main
RUN git lfs pull

RUN pip3 install -r requirements.txt

#Expose the required port
EXPOSE 5000

# check if the model is present
RUN ls -la

#Run the command
CMD waitress-serve --host=127.0.0.1 --port=$PORT app:app