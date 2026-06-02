from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time



class Search:
    def __init__(self):
        self.link_site = "https://meususdigital.saude.gov.br/publico/estabelecimento-lista"
        self.map = {
             "buttons": {
                  "permission":{
                       "xpath" : '/html/body/app-root/ion-app/ion-alert/div[2]/div[3]/button[2]/span'
                  }

             }
        }

        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
    
    def abrir_site(self):
            time.sleep(2)
            self.driver.get(self.link_site)
            time.sleep(30)
    
    def permitir_local(self):
         self.driver.find_element(By.XPATH, self.map["buttons"]["permission"]["xpath"]).click()
         
        
objeto = Search()
objeto.abrir_site()
objeto.permitir_local()
#//*[@id="ion-overlay-2"]/div[2]/div[3]/button[2]/span  | --> Xpath permissão
#/html/body/app-root/ion-app/ion-alert/div[2]/div[3]/button[2]/span  |  --> Full Xpath permissão