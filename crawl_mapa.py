from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
from getpass import getpass
from time import sleep 
from datetime import datetime
chromedriver_autoinstaller.install()
import pandas as pd 
from tqdm import tqdm 

URL_MAPA = 'https://sistemas2.utfpr.edu.br/dpls/sistema/aluno01/mpRelProfMnemDisp.inicioAluno'

def get_args():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-u','--username', type=str, required=True)
    parser.add_argument('password', default=getpass(), nargs='?')
    parser.add_argument('-a', '--ano', type=str, default=str(datetime.today().year))
    parser.add_argument('-s', '--semestre', type=str, default='2' if datetime.today().month > 6 else '1')
    parser.add_argument('-d', '--dept', type=str, default='')
    parser.add_argument('-p', '--prof', type=str, default='')
    parser.add_argument('-o', '--output', type=str, default='')
    args = parser.parse_args()

    args.dept = args.dept.upper()
    args.prof = args.prof.upper()
    if not args.output:
        args.output = f'{args.ano}-{args.semestre}.csv'
    return args

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    return driver

def get_depts(driver):
    if args.dept:
        return args.dept.split(',')
    el_dept = driver.find_element(By.ID, 'pm_deptoacadnr')
    return el_dept.text.split('\n')[1:-1]
def set_dept(driver, dept):
    el_dept = driver.find_element(By.ID, 'pm_deptoacadnr')
    Select(el_dept).select_by_visible_text(dept)

def get_profs(driver):
    el_professor = driver.find_element(By.ID, 'pm_profmnemcodnr')
    professores = el_professor.text.split('\n')[1:-1]
    if args.prof:
        professores = [p for p in professores if p.split(' -')[0].upper() in args.prof.split(',')]
    return professores
def set_prof(driver, prof):
    el_professor = driver.find_element(By.ID, 'pm_profmnemcodnr')
    Select(el_professor).select_by_visible_text(prof)

def wait_result_load(driver):
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, 'div_tab1'))
    )

def get_horario(driver, disciplina_cod):
    term = '<br />'+disciplina_cod
    scripts = driver.find_elements(By.XPATH, f'//script[contains(text(), "{term}")]')
    ids = []
    for script in scripts:
        id_hor = script.get_attribute('innerHTML').split("'")[1]
        ids.append(id_hor)
    
    horarios = []
    for id in ids:
        el = driver.find_element(By.ID, id)
        if el.text.strip():
            horarios.append(id.replace('dv_','').upper())
    horarios = list(set(horarios))
    horarios.sort()
    horarios = ','.join(horarios)
    return horarios

def get_disciplinas(driver):
    driver.get(URL_MAPA)
    edt_username = driver.find_element(By.XPATH, '//input[contains(@autocomplete,"username")]')
    edt_password = driver.find_element(By.XPATH, '//input[contains(@autocomplete,"current-password")]')
    edt_username.send_keys(args.username)
    edt_password.send_keys(args.password)
    edt_password.submit()

    driver.implicitly_wait(2)

    print(f'Consultando mapa do semestre {args.ano}/{args.semestre}')

    el_ano = driver.find_element(By.ID, 'pi_periodoanualanonr')
    el_ano.clear()
    el_ano.send_keys(args.ano)

    el_semestre = driver.find_element(By.ID, 'pr_periodoanualseqnr')
    el_semestre.clear()
    el_semestre.send_keys(args.semestre)
    
    disciplinas = []

    options_depts = get_depts(driver)

    for dept in tqdm(options_depts, desc='Departamentos'):
        set_dept(driver, dept)

        sleep(1)

        options_professors = get_profs(driver)
        for professor in tqdm(options_professors, desc='Professores'):
            set_prof(driver, professor)
            
            btn_pesquisar = driver.find_element(By.ID, 'bt_pesquisar')
            btn_pesquisar.click()
            
            sleep(.8)

            codname = professor.split(' ')[0]
            

            professor_dict = {
                'professor': professor,
                'departamento': dept,
                'ano/periodo': args.ano + '/' + args.semestre,
            }

            try:
                el_tab_disciplinas = driver.find_element(By.CLASS_NAME, "tabela")
            except:
                continue

            headers = [th.text for th in el_tab_disciplinas.find_elements(By.TAG_NAME, "th")]
            rows = el_tab_disciplinas.find_elements(By.XPATH, "tbody/tr")
            for i, el_row in enumerate(rows):
                codigos = el_row.find_elements(By.TAG_NAME, "td")[1].text
                nome = el_row.find_elements(By.TAG_NAME, "td")[2].text
                codigo = codigos.split(' ', 1)[0]
                turmas = codigos.split(' ', 1)[-1].split(' - ')
                for turma in turmas:
                    disciplina = {
                        'disciplina': codigo,
                        'turma': turma,
                        'nome': nome,
                        **professor_dict,
                    }
                    disciplina['horario']= get_horario(driver, codigo+'-'+turma)
                    disciplinas.append(disciplina)
    return disciplinas

def save_disciplinas(disciplinas):
    df = pd.DataFrame(disciplinas)
    df.to_csv(args.output, index=False)

args = get_args()
if __name__ == '__main__':
    driver = get_driver()
    disciplinas = get_disciplinas(driver)
    save_disciplinas(disciplinas)