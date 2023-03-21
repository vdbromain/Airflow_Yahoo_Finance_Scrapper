## Description

In this project, I plan to scrap financial data from yahoo finance website to train myself to implemente automated webscrapping with Selenium, Airflow, Docker and Selenium Grid togheter. My main focus was to learn and apply airflow in this project.



Duration : 9 days



The project has this structure :

- Dags folder : to define airflow's dags in one file and the my scrapper's functions in another one.

- Dockerfile : to create the environnement where everything will work toegheter.

- requirements.txt : required by the Dockerfile to build the docker's image.



## Installation

1. To launch this project, you'll need to install and run Docker Desktop on your computer. You can find all you need to install it here : [Download Docker Desktop | Docker](https://www.docker.com/products/docker-desktop/)

2. Clone this repo

3. Open a terminal in your local repo at the root of the folder

4. Create the image from the Dockerfile who set everything up for airflow working on any computer 
   
   '''docker build -t airflow_image .'''

5. Create the docker's network for the containers to connect each other
   
   ''docker network create scrap'''

6. Create the docker container with airflow and the requirements.txt in it 
   
   '''docker run -itd --rm --network scrap --name airflow-container -p 9090:8080 -v $(pwd):/docker_env airflow_image'''

7. Create the docker container with Selenium_Grid with Chromium in it. This command will automatically pull the docker's image needed to run the container :
   
   '''docker run -itd --rm --network scrap --name selenium-grid-container -p 4444:4444 --shm-size 2g seleniarm/standalone-chromium:latest'''

8. As both dockers'containers are on the same network called "scrap", you just have to go on http://0.0.0.0:9090/
   
   
   
   ![Airflow_Login.png](./img/Airflow_Login.png)

9. Username : admin

10. Password : admin

11. You click on the button on the left to activate the dag and after a few seconds, you'll see and appear a new folder named "data" with inside a new file with the scrapped data.
    
    
    
    ![Airflow_Dag_Page.png](img/Airflow_Dag_Page.png)
    
    

## Results

This project manages to scrap datas from yahoo finance website for 1 ticker (ACN in my example) and it can do it everyday by itself. The scrapped datas are :

- Date

- Open

- High

- Low

- Close*

- Ajd Close**

- Volume

The main goal for this project was to automate the whole process. Following that goal, I had to develop 2 differents dockers'containers, here is the diagram of them :



![Main_diag_airlfow.png](img/Main_diag_airflow.png)

As you can see in the airflow-container, airflow is managing everything.

To clarify the relation between both containers, the selenium-grid-container is only needed for the scrapping part. My python script (who is located in the airflow-container) has as selenium's webdriver, the name of the selenium-grid-container with that structure : http://selenium-grid-container:4444/wd/hub. At the end of the scrapping, the selenium-grid-container is not used anymore.

The data cleaning, shapping, csv creating and saving is done in the airflow-container.

## Improvements

- ###### Regarding the scrapper :
  
  - Adapt the scrapping script to scrap 100 data's companies
  
  - Divided the scrapping process between several threads to speed up the process

- ###### Regarding data's storage :
  
  - Create a database to store the whole scrapped data to facilitate data management, data updating and the access to it

- ###### Regarding docker
  
  - Create a docker-compose file to facilitate the deployment and the program's utilisation

- ###### Regarding deployment
  
  - Deploy it on the cloud to set a first step 
  
  - Create an online app where people could ask for



## Contact

<div>
<a href="https://github.com/vdbromain">
  <img title="" src="img/GitHub-logo.png" alt="GitHub-logo.png" width="62">
</a>
<a href="https://www.linkedin.com/in/vdbromain/">
  <img title="" src="img/linked-in-logo.png" alt="linked-in-logo.png" width="62">
</a>
</div>


