#SELENIUM
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

#For the function convert_string_into_date_time()
from dateutil import parser
from datetime import date
#For the function list_to_csv
import os
import csv

#Personnal Functions
from main import create_csv_from_yahoo_scrap 

#AIRFLOW
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator 

#To manage the dates
from datetime import datetime, timedelta

#Defining the default_args for the DAG
defaults_args = {
    "owner": "Romain",
    "description": "Scraping financial data from yahoo",
    "depends_on_past" : False,
    "start_date" : datetime(2023, 3, 12),
    "email": ['admin@admin.be'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

#Defining the dag => #0 0 * * * is the same as @daily makes the same "everyday at midnight"
#Catchup=False to not make the tasks from the start_date until now when I'll launch it
with DAG("scrapping", default_args=defaults_args, schedule_interval='0 0 * * *', catchup=False) as dag : 

    #Defining the PythonOperator to call the function everyday at midnight
    #yahoo_scrapper = PythonOperator(task_id="yahoo_scrapper", python_callable=print_thg, op_kwargs={'what_I_have_to_print':"I'm in the first print"}, dag=scrapping_dag)
    
    #Start_end
    start_dag = EmptyOperator(task_id="start_dag")
    #end_dag
    end_dag = EmptyOperator(task_id="end_dag")
    #Print the first task is finished
    scrapping = PythonOperator(task_id="scrapping", python_callable=create_csv_from_yahoo_scrap)

#Defining the dependencies
start_dag >> scrapping >> end_dag