#Lancez cette cmd : docker run -itd --rm --network portfolio --name selenium-grid-container -p 4444:4444 -p 5900:5900 -p 7900:7900 --shm-size 2g seleniarm/standalone-chromium:latest
#Ouvrir dans navigateur http://localhost:7900/ password = secret

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
#from functions.functions import scrap_yahoo
#from functions.functions import deleting_dividend_line
#from functions.functions_modified import create_csv_from_yahoo_scrap

#AIRFLOW
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator 

#To manage the dates
from datetime import datetime, timedelta

def scrap_yahoo() -> list:
    """
    This function scrapped datas from yahoo finance and convert the datas scrapped into lists. 
    It returns one with the columns names and one with the content for the future DF
    """
    print("I begin")

    options = webdriver.ChromeOptions()
    options.accept_insecure_certs = True
    options.add_argument('--disable-blink-features=AutomationControlled') ## to avoid getting detected
    options.add_argument('headless')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Remote(command_executor='http://selenium-grid-container:4444/wd/hub', options=options)

    #Defining Chrome as the driver
    #driver = webdriver.Chrome()

    #Defining the url to scrap
    url = "https://finance.yahoo.com/quote/ACN/history?period1=995500800&period2=1678406400&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"

    #To open the url in the browser
    driver.get(url)

    #To click on the button "agree" for the coockies
    cookie_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.NAME, 'agree')))
    cookie_button.click()

    #To click on the button "Maybe later" for closing the proposition
    print("I'm waiting")
    maybe_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="myLightboxContainer"]/section/button[1]')))
    print("I'm trying to click on the maybe later button")
    maybe_button.click()
    #Getting the content I want
    #Titles will be the column_names of the DF
    titles = driver.find_element(By.TAG_NAME, "thead")
    print(titles.text)
    #Content will be the content of the DF without the columns names
    content = driver.find_element(By.TAG_NAME, "tbody")
    print(content.text)
    #Convert string (the scrappes data) into list
    column_names = titles.text.split()
    values = content.text.split()

    print(f"column_names = {column_names}")
    print(f"content = {values}")

    try :
        driver.close()
        driver.quit()
    except :
        print("Driver closed by app")
    else :
        print("I've just closed the driver")
    
    return column_names, values


def deleting_dividend_line (values: list) -> list:
    """
    This function delete the data who contains the word "Dividend" with the 4 indexes before (to delete the whole line) 
    because it messes the data if I keep it.
    It returns the cleaned list
    """
        
    for i, value in enumerate(values):
        if "Dividend" in value:
            print(f"There is the word 'Dividend' in the list nb {i}")
            #As the line with dividend is always 5 items long I delete the 5 elements to delete the line
            print(f"Here is the values I'll delete : {values[i-4:i+1]}")
            del values[i-4:i+1]
            print("I've just deleted the values above")

    return values


def column_names_formatting(column_names: list) -> list:
    """
    This function makes the column_names fit the column_names'list to this shape : 
    ['Date', 'Open', 'High', 'Low', 'Close*', 'Adj_Close**', 'Volume']
    """
    column_names[5] = column_names[5] + "_" + column_names[6]
    column_names[6] = column_names[7]
    #Deleting the last element we don't need anymore
    column_names.pop()

    return column_names

def list_to_list_n_elements (list_to_convert : list, n : int) -> list:
    """
    This function convert a list into several different lists of n elements
    """
    lines : list = []
    i = 0
    while i < len(list_to_convert):
        if i == 0 :
            lines.append(list_to_convert[i:n])
            i += n
        else :
            lines.append(list_to_convert[i:i+n])
            i += n         

    return lines

def deleting_coma (list_to_modify : list, index : int=1) -> list:
    """
    This function take the list to modify and the index of the element to modify
    default value = 1 (the second element of the list) from which to delete the coma
    """
    
    #To delete the "," at the end of the day's element
    list_to_modify[index] = list_to_modify[index][0:2]

    return list_to_modify

def building_date_from_3_first_columns (list_to_modify: list, begin_index: int=0) -> list:
    """
    This function builds the date in the first columns from the 3 first ones
    It returns the list modified
    """
    #date in the first element of the list
    list_to_modify[begin_index] = list_to_modify[begin_index] + " " + list_to_modify[begin_index+1] + " " + list_to_modify[begin_index+2]

    #Deleting 2 times value with index 1 to delete the value with index 1 and 2
    #To delete the value with index 1
    list_to_modify.pop(begin_index+1)
    #To delete the value with index 1
    list_to_modify.pop(begin_index+1)

    return list_to_modify

def convert_string_into_date_time(list_to_modify : list, begin_index: int=0) -> list:
    """
    This function convert the string type first column date into date formatted for python to work with them 
    """
       
    the_date_with_hour = parser.parse(list_to_modify[begin_index])
    the_date = date(the_date_with_hour.year, the_date_with_hour.month, the_date_with_hour.day)
    list_to_modify[begin_index] = the_date
        
    return list_to_modify

def creating_list_ready_for_csv(values_list: list) -> list:
    """
    This function iterates trough the list of values scrapped and modify them storing them into a list of values to put in a csv
    Defining the final list to go into a csv (as values of csv)
    """
    list_to_csv = []

    for liste in values_list:
        #Defining a temporary list
        temp_liste = []
        #Deleting the "," of the second element of the list
        temp_liste = deleting_coma(liste, 1)
        #Concatenating the 3 first elements of the list into a single one
        temp_liste = building_date_from_3_first_columns(temp_liste, 0)
        #Converting the string date into a datetime.date object
        temp_liste = convert_string_into_date_time(temp_liste, 0)
        #Adding the temp_list to the final_list called list_to_df
        list_to_csv.append(temp_liste)

    return list_to_csv

def list_to_csv (liste : list, column_names : list, file_name : str, folder_name : str) -> None :
    """
    This function create a csv file from the column names and the list who was prepared before
    """
    today = str(date.today())
    file_name += "_" + today + ".csv"

    #Build the file path joining folder_name and file_name
    file_path = os.path.join(folder_name, file_name)
    print(file_path)
    # Check if the folder exists, if not, it creates it
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)

    with open(file_path, "w") as f:
        # using csv.writer method from CSV package
        write = csv.writer(f)
        #To write the column names in the csv
        write.writerow(column_names)
        #To write the content in the csv
        write.writerows(liste)

def create_csv_from_yahoo_scrap() :
    #Scrapping data from yahoo collecting the column_names and the values related to them
    column_names, values = scrap_yahoo()
    print("I finished scrap part")
    #Deleting the wrong datas collected such as "dividend" line in the values
    print("I'm beginning deleting coma")
    list_to_convert = deleting_dividend_line(values)
    #Restructuring the column's names for them to fit the needed shape
    column_names = column_names_formatting(column_names)
    #Taking the values'list and converting it into a list of lists of n elements here n = 9 (because there's 9 columns for the moment)
    list_to_convert = list_to_list_n_elements(list_to_convert, n=9)
    #This function take the values we put in a list of lists above and it'll delete the coma, build the date from the 3 first columns
    #Convert the string date into a datetime.date object returning the list_ready_for_csv 
    list_ready_for_csv = creating_list_ready_for_csv(list_to_convert)
    list_to_csv(list_ready_for_csv, column_names, file_name="yahoo", folder_name="./data")