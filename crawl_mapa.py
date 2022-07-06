from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import chromedriver_autoinstaller
from getpass import getpass
from time import sleep 

chromedriver_autoinstaller.install()

URL_MAPA = 'https://sistemas2.utfpr.edu.br/dpls/sistema/aluno01/mpRelProfMnemDisp.inicioAluno'

def get_args():
    import argparse
    

    parser = argparse.ArgumentParser()
    parser.add_argument('-u','--username', type=str, required=True)
    args = parser.parse_args()
    return args

def get_driver():
    driver = webdriver.Chrome()
    
    return driver

def get_disciplinas(driver, args):
    driver.get(URL_MAPA)
    # /html/body/app-root/app-login/div/div/p-card/div/div/div/div/form/div[2]/div/input
    edt_username = driver.find_element(By.XPATH, '//input[contains(@autocomplete,"username")]')
    edt_password = driver.find_element(By.XPATH, '//input[contains(@autocomplete,"current-password")]')
    edt_username.send_keys(args.username)
    edt_password.send_keys(getpass())
    edt_password.submit()

    driver.implicitly_wait(2)

    semestre = driver.find_element(By.ID, 'pr_periodoanualseqnr')
    semestre.clear()
    semestre.send_keys('2')
    
    el_dept = driver.find_element(By.ID, 'pm_deptoacadnr')
    options_depts = el_dept.text.split('\n')[1:-1]
    select_dept = Select(el_dept)

    for dept in options_depts:
        select_dept.select_by_visible_text(dept)
        
        sleep(1)

        el_professor = driver.find_element(By.ID, 'pm_profmnemcodnr')
        options_professors = el_professor.text.split('\n')[1:-1]
        select_professor = Select(el_professor)
        for professor in options_professors:
            select_professor.select_by_visible_text(professor)
            el_pesquisar = driver.find_element(By.ID, 'bt_pesquisar')
            el_pesquisar.click()
            breakpoint()

    breakpoint()
    
if __name__ == '__main__':
    args = get_args()
    driver = get_driver()
    disciplinas = get_disciplinas(driver, args)
