#Create a ubuntu base image with python 3 installed.
FROM python:3.12.7

#Set the working directory
WORKDIR /

#copy all the files
COPY . .

#Install the dependencies
RUN apt-get -y update
RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip3 install -r requirements.txt

#Expose the required port
EXPOSE 5000

#Run the command
CMD ["waitress-serve", "--host", "127.0.0.1", "--port", "5000", "app:app"]  