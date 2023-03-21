#The python image I used to create my env
FROM python:3.7
#The root folder in the docker container
WORKDIR /docker_env
#To copy tout ce qui est en local dans le container
COPY ./requirements.txt ./
COPY ./dags ./dags
# RUN apt-get install -y chromium-browser
RUN apt-get update 
RUN apt-get install -y chromium

#To update pip
RUN pip install --upgrade pip
#To install all the libraries I need
RUN pip install --no-cache-dir -r requirements.txt
#I pip install airflow in the folder
RUN pip install "apache-airflow[celery]==2.5.1" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.5.1/constraints-3.7.txt"
#I set the environnement's variable like this command = export AIRFLOW_HOME=$(pwd) locally
ENV AIRFLOW_HOME=/docker_env
#export AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False

#The command to run inside the container to launch airflow init db, airflow scheduler, create the user&password and launch webserver
#CMD ["sh", "-c", "airflow db init & airflow scheduler & airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin & airflow webserver"]
CMD airflow db init && \
    airflow scheduler & \
    airflow users create --role Admin \
    --username admin \
    --email admin \
    --firstname admin \
    --lastname admin \
    --password admin && \
    airflow webserver


#Open in the broswer localhost:8080 
#or in 0.0.0.0:9090 with that line : docker run -itd --rm --network portfolio --name airflow -p 9090:8080 -v $(pwd):/docker_env test_airflow_new
#which python3.7
