import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from twocaptcha import TwoCaptcha
import requests
import json
from PIL import Image
import base64
import time
import os
import shutil
import random


def get_social_links(channel_url):
    CAPTCHA_API_KEY = "d6bedc99780cd530f42b671b7957????" # Api keyini buraya yapıştır. 
    mail_list = ["testsk19042025@gmail.com","testsk20042025@gmail.com"] # maillerinizi giriniz.
    # Not : Tek mail ile bot detection olur bu sebeple 2 mail önerilir.
    mail = random.choice(mail_list)
    password = "????"# mail şifresini giriniz. İki şifre de aynı değilse liste açınız.
    
    
    
    CAPTCHA_SOLVE_URL = "http://2captcha.com/in.php"
    CAPTCHA_RESULT_URL = "http://2captcha.com/res.php"
    
    
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-extensions")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("--mute-audio")
    options.add_argument("--log-level=3")
   
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(channel_url + "/about")
        time.sleep(3)
        
        social_links = {
            'email': 'not have email',
            'instagram': 'not have instagram', 
            'twitter': 'not have twitter',
            'facebook': 'not have facebook'
        }
        # Email çekme kısmı:
        # links = driver.find_elements(By.XPATH, "//div[@id='link-list-container']//yt-channel-external-link-view-model")
        
        time.sleep(5) 
        
        try:
            
            wait = WebDriverWait(driver, 15)

            wait.until(
            EC.presence_of_element_located((By.ID, "link-list-container"))
            )
            sign_in_bttn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[@id='additional-info-container']/table/tbody/tr[1]/td[2]/yt-attributed-string/span/span/a")
            ))
            sign_in_bttn.click()

            e_posta = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='identifierId']")
            ))
            e_posta.send_keys(mail)
            e_posta.send_keys(Keys.ENTER)
            time.sleep(6)
            # 1. captcha
            
            def is_captcha_passed(driver):
                try:
                    driver.find_element(By.ID, "password")  # CAPTCHA geçtiyse şifre input'u gelmiş olur
                    return True
                except NoSuchElementException:
                    pass
                
                try:
                    error_el = driver.find_element(By.XPATH, "//div[contains(text(), 'Wrong')]")
                    return False
                except NoSuchElementException:
                    return False

            attempt = 0
            MAX_ATTEMPTS = 3

            while attempt < MAX_ATTEMPTS:
                attempt += 1
                print(f"[{attempt}. deneme] CAPTCHA çözülüyor...")

                try:
                    img_element = driver.find_element(By.ID, "captchaimg")
                    img_src = img_element.get_attribute("src")
                    full_url = urljoin(driver.current_url, img_src)

                    session = requests.Session()
                    for cookie in driver.get_cookies():
                        session.cookies.set(cookie['name'], cookie['value'])

                    response = session.get(full_url)
                    b64 = base64.b64encode(response.content).decode()

                    payload = {
                        'key': CAPTCHA_API_KEY,
                        'method': 'base64',
                        'body': b64,
                        'json': 1
                    }
                    response = requests.post("http://2captcha.com/in.php", data=payload).json()
                    if response.get("status") != 1:
                        print("2Captcha gönderme hatası:", response.get("request"))
                        continue
                    
                    captcha_id = response["request"]
                    result_url = f"http://2captcha.com/res.php?key={CAPTCHA_API_KEY}&action=get&id={captcha_id}&json=1"

                    for _ in range(20):
                        time.sleep(5)
                        result = requests.get(result_url).json()
                        if result['status'] == 1:
                            captcha_text = result['request']
                            break
                    else:
                        print("CAPTCHA çözümü alınamadı.")
                        continue
                    
                    try:
                        captcha_input = driver.find_element(By.ID, "ca")
                        captcha_input.clear()
                        captcha_input.send_keys(captcha_text)
                    except NoSuchElementException:
                        print("CAPTCHA input bulunamadı.")
                        continue
                    
                    try:
                        next_btn = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//*[@id='identifierNext']/div/button/span"))
                        )
                        next_btn.click()
                    except TimeoutException:
                        print("Next butonu tıklanamadı.")
                        continue
                    
                    time.sleep(5)
                    if is_captcha_passed(driver):
                        print("CAPTCHA başarıyla geçildi.")
                        break
                    else:
                        print("CAPTCHA geçilemedi, tekrar deneniyor...")

                except Exception as e:
                    print("Beklenmeyen hata:", e)
                    continue
                
            else:
                print("Maksimum deneme sayısına ulaşıldı, CAPTCHA aşılamadı.")
                
            time.sleep(6)

            password_btn = driver.find_element(By.XPATH,"//*[@id='password']/div[1]/div/div[1]/input")
            password_btn.click()
            password_btn.send_keys(password)
            password_btn.send_keys(Keys.ENTER)
            time.sleep(6)
            about_btnn = driver.find_element(By.XPATH,"//*[@id='page-header']/yt-page-header-renderer/yt-page-header-view-model/div/div[1]/div/yt-description-preview-view-model/truncated-text/button/span/span")
            about_btnn.click()
            time.sleep(5)
            last_e_post = driver.find_element(By.XPATH,"//*[@id='view-email-button-container']/yt-button-view-model/button-view-model/button/yt-touch-feedback-shape/div/div[2]")
            last_e_post.click()
            time.sleep(4)
            
            solver = TwoCaptcha(CAPTCHA_API_KEY)
            
            
            
            try:
                # sitekey = driver.find_element(By.CLASS_NAME, "g-recaptcha").get_attribute("data-sitekey")
                sitekey = "6Lf39AMTAAAAALPbLZdcrWDa8Ygmgk_fmGmrl???"  # sitekey bilginizi girin.
                result = solver.recaptcha(sitekey=sitekey, url=driver.current_url)
                code = result["code"]
                print("✅ Token alındı!")
                # g-recaptcha-response inputunun yüklendiğinden emin ol
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "g-recaptcha-response"))
                )
                # token'ı input'a yaz
                driver.execute_script("""
                let recaptchaCallback = document.getElementById("g-recaptcha-response");
                recaptchaCallback.style.display = "block";
                recaptchaCallback.value = arguments[0];
                recaptchaCallback.dispatchEvent(new Event('change'));
                """, code)
                print("✅ Token yazıldı!")
                
                time.sleep(3)
                # submit butonuna tıkla
                # submit_btn = driver.find_element(By.ID, "submit-btn")
                
                print("✅ Form gönderildi!")
                # submit_btn.click()
                submit_btn = driver.find_element(By.ID, "submit-btn")                   
                
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_btn)
                time.sleep(2)
                submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-btn")))

                submit_btn.click()
                time.sleep(10)
                email_data =  driver.find_element(By.ID,"email").text
                print(email_data)
                social_links['email'] = email_data
                
                
            except Exception as e:
                print("❌ Hata:", e)


            
        
        except Exception as e:
            print("email çekerken hata oldu hata : " + str(e))
        

        # sosyal medya linkleri
        links = driver.find_elements(By.XPATH, "//div[@id='link-list-container']//yt-channel-external-link-view-model")
        
        for link in links:
            try:
                spans = link.find_elements(By.TAG_NAME, "span")
                if len(spans) >= 2:
                    label = spans[0].text.strip().lower()
                    url = spans[1].text.strip()
                    
                    if 'instagram' in label:
                        social_links['instagram'] = url
                    elif 'twitter' in label or 'x.com' in label:
                        social_links['twitter'] = url
                    elif 'facebook' in label:
                        social_links['facebook'] = url
                    
            except:
                continue
                
        return social_links
        
    except Exception as e:
        print("Scraping hatası: " +str(e))
        return None
    finally:
        if driver:
            driver.quit()

def add_social_media_info(input_csv):
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"{input_csv} bulunamadı")
    
    output_csv = 'tech_youtubers_final.csv'  # Sabit çıktı dosya adı
    
    try:
        df = pd.read_csv(input_csv)
        
        # Sosyal medya sütunlarını ekle
        for platform in ['email', 'instagram', 'twitter', 'facebook']:
            if platform not in df.columns:
                df[platform] = f'not have {platform}'
        
        # Linkleri çek
        for index, row in df.iterrows():
            links = get_social_links(row['Channel Link'])
            if links:
                for platform, url in links.items():
                    df.at[index, platform] = url
        
        # Eski dosyaları temizle
        if os.path.exists(input_csv):
            os.remove(input_csv)
        if os.path.exists(input_csv + '.old'):
            os.remove(input_csv + '.old')
        
        df.to_csv(output_csv, index=False)
        print(f"\nFinal dosyası oluşturuldu: {output_csv}")
        return output_csv
        
    except Exception as e:
        print(f"CSV işleme hatası: {e}")
        raise