from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
import uuid
import json
import logging

logging = logging.getLogger("django")

# Create your views here.
def fetch_cake_jobs(request):
    url = 'https://www.cakeresume.com/jobs'
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 確保請求成功，否則拋出異常
        with open('response_content.html', 'w', encoding='utf-8') as file:
            file.write(response.text)
        
    except requests.RequestException as err:
        logging.error(f"Request failed: {err}")
        return JsonResponse({"error": str(err)}, status=500)  # 返回錯誤訊息

    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []

    # 遍歷每個職缺項目
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