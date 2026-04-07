from selenium import webdriver
from selenium.webdriver import Service
import time



class Search:
    def __init__(self):
        self.link_site = ""
        self.map = {}

        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
    
    def abrir_site(self):
        try:
            self.driver.get(self.link_site)
            time.sleep(10)
        