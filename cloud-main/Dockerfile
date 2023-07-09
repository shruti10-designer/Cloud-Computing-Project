FROM python:3.10
COPY . .
RUN apt-get update
RUN apt-get install -y python3-pip python3-dev python3
RUN pip install --upgrade pip 
RUN pip install -r requirements.txt 
EXPOSE 8080
ENTRYPOINT [ "python3" ] 
CMD [ "main.py" ]