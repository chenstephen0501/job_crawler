import requests, logging, time, json, uuid, os
from bs4 import BeautifulSoup
from django.http import JsonResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from django.http import HttpResponseRedirect

logging = logging.getLogger("django")

def fetch_cake_jobs(req):
    url = 'https://www.cakeresume.com/jobs'
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  
        with open('response_content.html', 'w', encoding='utf-8') as file:
            file.write(response.text)
        
    except requests.RequestException as err:
        logging.error(f"Request failed: {err}")
        return JsonResponse({"error": str(err)}, status=500) 

    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []

    for job_item in soup.find_all('div', class_='JobSearchItem_wrapper__bb_vR'):
        try:
            company_name = job_item.find('a', class_='JobSearchItem_companyName__bY7JI').text.strip()
            position_title = job_item.find('a', class_='JobSearchItem_jobTitle__bu6yO').text.strip()
            position_description = job_item.find('div', class_='JobSearchItem_description__si5zg').text.strip()
            inline_messages = job_item.find_all('div', class_='InlineMessage_inlineMessage____Ulc InlineMessage_inlineMessageLarge__uaRgi InlineMessage_inlineMessageDark__JjyEO')

            if len(inline_messages) >= 3:
                third_inline_message = inline_messages[2]
                salary_tag = third_inline_message.find('div', class_='InlineMessage_label__LJGjW')
                salary = salary_tag.text.strip() if salary_tag else 'N/A'
            else:
                salary = 'N/A'

            position_location = job_item.find('a', class_='JobSearchItem_featureSegmentLink__yMxQc').text.strip()
            position_link = f"https://www.cakeresume.com{job_item.find('a', class_='JobSearchItem_jobTitle__bu6yO')['href']}"

            job_dict = {
                "id": str(uuid.uuid4()),
                "company_name": company_name,
                "position_title": position_title,
                "position_description": position_description,
                "salary": salary,
                "position_location": position_location,
                "position_link": position_link,
            }

            jobs.append(job_dict)

        except (json.JSONDecodeError, KeyError) as err:
            logging.warning(f"Skipping problematic data: {err}")
            continue

    return JsonResponse(jobs, safe=False)

def fetch_cake_jobs_all(req):
    baseurl = 'https://www.cakeresume.com/jobs?location_list%5B0%5D=%E5%8F%B0%E5%8C%97%E5%B8%82%2C%20%E5%8F%B0%E7%81%A3&location_list%5B1%5D=%E6%96%B0%E5%8C%97%E5%B8%82%2C%20%E5%8F%B0%E7%81%A3&profession%5B0%5D=it_software-engineer&profession%5B1%5D=it_back-end-engineer&profession%5B2%5D=it_front-end-engineer&profession%5B3%5D=it_full-stack-development&page='
    page = 1
    headers = {'User-Agent': 'Mozilla/5.0'}
    jobs = []

    while True:
        url = f"{baseurl}{page}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() 

        except requests.RequestException as err:
            logging.error(f"Request failed: {err}")
            return JsonResponse({"error": str(err)}, status=500)  

        soup = BeautifulSoup(response.text, 'html.parser')

        jobs_items = soup.find_all('div', class_='JobSearchItem_wrapper__bb_vR')
        
        if not jobs_items:
            break

        for job_item in jobs_items:
            try:
                company_name = job_item.find('a', class_='JobSearchItem_companyName__bY7JI').text.strip()
                position_title = job_item.find('a', class_='JobSearchItem_jobTitle__bu6yO').text.strip()
                position_description = job_item.find('div', class_='JobSearchItem_description__si5zg').text.strip()
                inline_messages = job_item.find_all('div', class_='InlineMessage_inlineMessage____Ulc InlineMessage_inlineMessageLarge__uaRgi InlineMessage_inlineMessageDark__JjyEO')

                if len(inline_messages) >= 3:
                    third_inline_message = inline_messages[2]
                    salary_tag = third_inline_message.find('div', class_='InlineMessage_label__LJGjW')
                    salary = salary_tag.text.strip() if salary_tag else 'N/A'
                else:
                    salary = 'N/A'

                position_element = job_item.find('a', class_='JobSearchItem_featureSegmentLink__yMxQc')

                if position_element:
                    position_location = position_element.text.strip()
                else:
                    position_location = 'N/A'

                position_link = f"https://www.cakeresume.com{job_item.find('a', class_='JobSearchItem_jobTitle__bu6yO')['href']}"

                job_dict = {
                    "id": str(uuid.uuid4()),
                    "company_name": company_name,
                    "position_title": position_title,
                    "position_description": position_description,
                    "salary": salary,
                    "position_location": position_location,
                    "position_link": position_link,
                }

                jobs.append(job_dict)
            except (json.JSONDecodeError, KeyError) as err:
                logging.warning(f"Skipping problematic data: {err}")
                continue

        next_page_button = soup.find_all(class_='Pagination_itemNavigation__Cv3M8')[-1]

        if next_page_button:
            if next_page_button.name == "a":
                page += 1
                time.sleep(3) 
            else:
                break
        else:
            break

    return JsonResponse(jobs, safe=False)

def user_apply_jobs(request):
    url = 'https://www.cakeresume.com/'
    firefox_binary_path = '/usr/bin/firefox' 
    options = webdriver.FirefoxOptions()
    options.binary_location = firefox_binary_path
    geckodriver_path = '/usr/local/bin/geckodriver'
    service = webdriver.FirefoxService(executable_path=geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options)

    driver.get(url)
    try:
        login_button = driver.find_element(By.LINK_TEXT, "登入")
        login_button.click()
        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
        email_input.send_keys(os.getenv("CAKE_EMAIL"))
        password_input.send_keys(os.getenv("CAKE_PASSWORD"))

        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        submit_button.click()

        time.sleep(5)

        job_menu = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'SidebarMenu_menuHeaderTitle__t1Ow3') and text()='求職']"))
        )
        job_menu.click()

        applied_jobs = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'SidebarMenu_menuItemContentValue__MYWG2') and .//span[text()='已應徵職缺']]"))
        )
        applied_jobs.click()

        time.sleep(5)

        with open('response_content.html', 'w', encoding='utf-8') as file:
            file.write(driver.page_source)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        apply_jobs = soup.find_all('div', class_='UserJobApplicationList_item__za9o4')

        jobs = []

        for job in apply_jobs:
            company_name = job.find("a", class_="JobApplicationItem_companyName__NXrvJ").text.strip()
            job_title = job.find("a", class_="JobApplicationItem_jobTitle__i1m5a").text.strip()
            company_url = job.find("a", class_="JobApplicationItem_companyName__NXrvJ")['href']
            job_url = f"{url}{job.find("a", class_="JobApplicationItem_jobTitle__i1m5a")['href']}"
            logo_url = job.find("img", class_="CompanyLogo_logo__1hyTe")['src']
            cover_letter = job.find("div", class_="JobApplicationItem_coverLetterSingleLine__Ec31B").text.strip()

            application_status = {
                "read_within": job.find("div", class_="InlineMessage_inlineMessage____Ulc").text.strip(),
                "employer_status": job.find_all("div", class_="InlineMessage_inlineMessage____Ulc")[1].text.strip(),
                "resume_link": f"{url}{job.find("a", class_="JobApplicationItem_file__q5eyr")['href']}",
                "days_ago": job.find("span", class_="JobApplicationItem_note__uSzuh").text.strip()
            }

            job_info = {
                "id": str(uuid.uuid4()),
                "company": company_name,
                "job_title": job_title,
                "logo_url": logo_url,
                "company_url": company_url,
                "job_url": job_url,
                "cover_letter": cover_letter,
                "application_status": application_status
            }

            jobs.append(job_info)

        return JsonResponse(jobs, safe=False)

    except TimeoutException as e:
        return JsonResponse({"error": "操作超時，無法找到元素。"}, status=500)

    except NoSuchElementException as e:
        return JsonResponse({"error": "無法找到指定的元素。"}, status=500)

    finally:
        driver.quit()


def user_login(request):
    url = 'https://www.cakeresume.com/'
    firefox_binary_path = '/usr/bin/firefox' 
    options = webdriver.FirefoxOptions()
    options.binary_location = firefox_binary_path
    geckodriver_path = '/usr/local/bin/geckodriver'
    service = webdriver.FirefoxService(executable_path=geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options)

    driver.get(url)

    try:
        login_button = driver.find_element(By.LINK_TEXT, "登入")
        login_button.click()

        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
        email_input.send_keys(os.getenv("CAKE_EMAIL"))  
        password_input.send_keys(os.getenv("CAKE_PASSWORD"))  

        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        submit_button.click()

        time.sleep(5)

        job_menu = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'SidebarMenu_menuHeaderTitle__t1Ow3') and text()='求職']"))
        )
        job_menu.click()

        applied_jobs = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'SidebarMenu_menuItemContentValue__MYWG2') and .//span[text()='已應徵職缺']]"))
        )
        applied_jobs.click()

        logged_in_url = driver.current_url

        driver.quit()

        return HttpResponseRedirect(logged_in_url)

    except TimeoutException as e:
        return JsonResponse({"error": "操作超時，無法找到元素。"}, status=500)

    except NoSuchElementException as e:
        return JsonResponse({"error": "無法找到指定的元素。"}, status=500)
