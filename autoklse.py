import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium.webdriver.common.action_chains import ActionChains

driver = webdriver.Edge()
driver.get('https://www.klsescreener.com/v2/')


## set the dividend yeild
input_text = driver.find_element(By.NAME,'min_dy').send_keys('6')
time.sleep(1)

## set the minimum market cap
input_text2 = driver.find_element(By.NAME,'min_marketcap').send_keys('1000')
time.sleep(1)


driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(1)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
button_path = '/html/body/div[1]/div[1]/div[3]/div/div[1]/div[1]/div/form/div[29]/div[2]/input'
submit_button = driver.find_element(By.XPATH,button_path).click()
time.sleep(3)

table_path= '/html/body/div[1]/div[1]/div[3]/div/div[2]/div[3]/table'
table = driver.find_element(By.XPATH,table_path)

# read the table
soup= BeautifulSoup(table.get_attribute('outerHTML'),'html.parser')
table_headers = []
for th in soup.find_all('th'):
    table_headers.append(th.text)
    
table_data = []
for row in soup.find_all('tr'):
    columns = row.find_all('td')
    output_row = []
    for column in columns:
        output_row.append(column.text)
    table_data.append(output_row)    
    
allthelinks = []    
for row in soup.find_all('tr'):
    for links in row.findAll('a'):
        x = links.get('href')
        allthelinks.append(x)

allthelinks = list(dict.fromkeys(allthelinks)) # to remove duplicate
company_urls = allthelinks[::2] # show only the evens result to filter out the chart link
three_urls = company_urls[0:3] # for testing
original_window = driver.current_window_handle
#driver.maximize_window()

good_stock = []

for i in range(len(company_urls)): #change 'company_urls' to 'three_urls' for testing
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1+i])
    newtab = 'https://www.klsescreener.com' + company_urls[i] #change 'company_urls' to 'three_urls' for testing
    driver.get(newtab)
    time.sleep(3)

    dividend_button_path = '/html/body/div[1]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div[4]/ul/li[3]/a'
    dividend_button = driver.find_element(By.XPATH,dividend_button_path)
    dividend_button.click()
    actions = ActionChains(driver)
    ex_date_path = '/html/body/div[1]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div[4]/div/div[4]/table/tbody/tr[1]/td[8]/a'
    ex_date = driver.find_element(By.XPATH,ex_date_path)
    actions.move_to_element(ex_date).perform()
    
    # read the table
    table_div_path= '/html/body/div[1]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div[4]/div/div[4]/table'
    table_div = driver.find_element(By.XPATH,table_div_path)
    soup_div = BeautifulSoup(table_div.get_attribute('outerHTML'),'html.parser') 
    table_div_headers = []
    for th in soup_div.find_all('th'):
        table_div_headers.append(th.text)
    #print(table_div_headers)
    
    table_div_data = []
    for row in soup_div.find_all('tr'):
        columns = row.find_all('td')
        output_div_row = []
        for column in columns:
            output_div_row.append(column.text)
        table_div_data.append(output_div_row)  
    #print(table_div_data)      
    dfdiv0 = pd.DataFrame(table_div_data, columns=table_div_headers)
    dfdiv = dfdiv0.iloc[1:]
    for head in table_div_headers:
        dfdiv[head] = dfdiv[head].str.replace('\n','')
        dfdiv[head] = dfdiv[head].str.replace(' ','')
        dfdiv[head] = dfdiv[head].str.strip().str[-4:]
    #print(dfdiv)
    columns = ['Announced', 'Financial Year', 'Subject', 'Payment Date', 'Amount', 'Indicator', '']
    dfdiv.drop(columns, axis=1, inplace=True)
    fq2023 = (dfdiv['EX Date'] == '2023').sum()
    fq2022 = (dfdiv['EX Date'] == '2022').sum()
    fq2021 = (dfdiv['EX Date'] == '2021').sum()
    if fq2022 >= 3:
        stock_name = driver.find_element(By.XPATH,'/html/body/div[1]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/span')
        stock_name_text = BeautifulSoup(stock_name.get_attribute('outerHTML'),'html.parser')
        #print(stock_name, '2023:',fq2023,' 2022:',fq2022,' 2021:',fq2021)
        good_stock.append(stock_name_text.text)
print(len(good_stock),good_stock)


'''
# remove unwanted text    
df = pd.DataFrame(table_data, columns=table_headers)
df1 = df.iloc[1:]
for head in table_headers:
    df1[head] = df1[head].str.replace('\n','')
    word = '\[s\]'
    df1[head] = df1[head].str.replace(word,'')
    
# make it beautiful    
columns = ['Change% ', '52week ', 'Volume ','PTBV ','Indicators ', ' ']
df1.drop(columns, axis=1, inplace=True)
df1['Price '] = pd.to_numeric(df1['Price '])    
df1['MCap.(M) '] = pd.to_numeric(df1['MCap.(M) '])
print(df1.sort_values(by=['MCap.(M) '], ascending=False))
'''

driver.quit()