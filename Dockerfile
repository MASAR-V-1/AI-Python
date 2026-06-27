# python version
FROM python:3.11-slim

# prevents Python from writing .pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# prevents Python from buffering stdout and stderr (to see logs in real time)
ENV PYTHONUNBUFFERED 1

# declare the working directory inside the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt /app/

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the current directory contents into the container at /app
COPY . /app/

#the port that the container will listen to
EXPOSE 8000    

#to run the server in development mode
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 