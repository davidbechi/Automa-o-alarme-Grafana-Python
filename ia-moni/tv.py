import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pygame
from sklearn.linear_model import SGDRegressor
import numpy as np
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#inicia o som
pygame.mixer.init()


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# emitir o som para alerta
def emitir_alerta(indicador, valor_antigo, valor_novo):
    print(f"Alerta! O indicador '{indicador}' mudou de {valor_antigo} para {valor_novo}.")
    
   
    pygame.mixer.music.load("alerta3.wav")
    pygame.mixer.music.play()
    
    time.sleep(2)  

# captura os valores
def capturar_valores():
    try:
        
        try:
            links_value = driver.find_element(By.XPATH, "//*[@id=':r14:']/div/div/div/div/div/div/span").text
            links_value = int(links_value)
        except:
            links_value = 0  

        
        try:
            sws_value = driver.find_element(By.XPATH, "//*[@id=':r16:']/div/div/div/div/div/div/span").text
            sws_value = int(sws_value)
        except:
            sws_value = 0  

        
        try:
            aps_value = driver.find_element(By.XPATH, "//*[@id=':r18:']/div/div/div/div/div/div/span").text
            aps_value = int(aps_value)
        except:
            aps_value = 0  

        
        try:
            srv_value = driver.find_element(By.XPATH, "//*[@id=':r1a:']/div/div/div/div/div/div/span").text
            srv_value = int(srv_value)
        except:
            srv_value = 0  

        
        try:
            relogios_value = driver.find_element(By.XPATH, "//*[@id=':r1c:']/div/div/div/div/div/div/span").text
            relogios_value = int(relogios_value)
        except:
            relogios_value = 0  

        
        try:
            taas_value = driver.find_element(By.XPATH, "//*[@id=':r1e:']/div/div/div/div/div/div/span").text
            taas_value = int(taas_value)
        except:
            taas_value = 0  

       
        try:
            cftvs_value = driver.find_element(By.XPATH, "//*[@id=':r1g:']/div/div/div/div/div/div/span").text
            cftvs_value = int(cftvs_value)
        except:
            cftvs_value = 0  

        
        try:
            coids_value = driver.find_element(By.XPATH, "//*[@id=':r1i:']/div/div/div/div/div/div/span").text
            coids_value = int(coids_value)
        except:
            coids_value = 0  

       
        return (links_value, sws_value, aps_value, srv_value,
                relogios_value, taas_value, cftvs_value, coids_value)

    except Exception as e:
        print(f"Erro ao capturar os valores: {e}")
        return None  # Retorna None em caso de erro 


modelos = [SGDRegressor(max_iter=1000, tol=1e-3) for _ in range(8)]
historico = {i: [] for i in range(8)}  


def treinar_modelo(novos_valores):
    global modelos
    for i, valor in enumerate(novos_valores):
        historico[i].append(valor)
        # mais de 10 valores, treina o modelo com histórico
        if len(historico[i]) > 10:
            X = np.array(range(len(historico[i]))).reshape(-1, 1)
            y = np.array(historico[i])
            modelos[i].partial_fit(X, y)


def prever_tendencias():
    previsoes = []
    for i in range(8):
        if len(historico[i]) > 10:
            X = np.array([[len(historico[i]) + 1]])  # Próximo valor a ser previsto
            previsoes.append(modelos[i].predict(X)[0])
        else:
            previsoes.append(None)  # Sem previsão se houver poucos dados
    return previsoes

# Função para gerar relatórios
# def gerar_relatorio(novos_valores, valores_anteriores, previsoes):
  #  if not os.path.exists("relatorios"):
   #     os.makedirs("relatorios")
    # with open(f"relatorios/relatorio_{time.strftime('%Y-%m-%d_%H-%M-%S')}.txt", "w") as f:
     #   for i, (novo, antigo, previsao) in enumerate(zip(novos_valores, valores_anteriores, previsoes)):
      #      f.write(f"Indicador {i + 1}: Valor Anterior: {antigo}, Valor Atual: {novo}, Previsão Futura: {previsao}\n")
      #  f.write("\n") 

#acessando painel do grafana
url = 'https://monitoria......'
driver.get(url)
time.sleep(10)  

# preenchendo campos de login e senha
username = "login"
password = "senha"
driver.find_element(By.NAME, 'user').send_keys(username)
driver.find_element(By.NAME, 'password').send_keys(password)
driver.find_element(By.XPATH, '//button[@type="submit"]').click()


time.sleep(5)

# Inicializa os valores antigos
valores_anteriores = capturar_valores()

if valores_anteriores is None:
    print("Não foi possível capturar os valores iniciais. Encerrando o monitoramento.")
    driver.quit()
else:
    print(f"Valores iniciais: {valores_anteriores}")

# Loop de monitoramento
try:
    while True:
        
        novos_valores = capturar_valores()

        if novos_valores is not None:
            
            indicadores = ['Links', 'SWs', 'APs', 'SRV Ponto', 'Relógios Ponto', 'TAAs', 'CFTVs', 'COIDs']
            for i, (novo, antigo) in enumerate(zip(novos_valores, valores_anteriores)):
                if novo != antigo:  
                    emitir_alerta(indicadores[i], antigo, novo)

            
            treinar_modelo(novos_valores)

            
            previsoes = prever_tendencias()

            # Gera o relatório
          #  gerar_relatorio(novos_valores, valores_anteriores, previsoes)

            # Atualiza os valores antigos
            valores_anteriores = novos_valores

        time.sleep(7)  # Intervalo entre verificações

except KeyboardInterrupt:
    print("Monitoramento interrompido manualmente.")

finally:
    print("Encerrando o navegador...")
    driver.quit()
