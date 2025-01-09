#Create a ubuntu base image with python 3 installed.
FROM python:3.12.7

#Set the working directory
WORKDIR /

#Install the dependencies
RUN apt-get -y update
RUN apt-get update && apt-get install python3 python3-pip -y
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 git  -y

#copy all the files
COPY . .
# COPY .git/ .git

# curl to download the model
RUN curl -o ecg_classification_model.tflite https://utfs.io/f/A96e4rcb6rkCNlFFMlS3jSv1CBXJKha6qZ2lQnfpMbGRHcsx

RUN pip3 install -r requirements.txt

#Run the command
CMD waitress-serve --host=127.0.0.1 --port=$PORT app:app