# job_crawler

## 求職網站爬蟲專案

`job_crawler` 是一個用於自動化爬取求職網站 CakeResume 平台上已應徵職缺資訊的 Python 專案。專案使用 `Selenium` 和 `BeautifulSoup` 來模擬使用者行為並抓取相關資料，最後將結果以 JSON 格式輸出，便於進一步處理和分析。

![職缺爬蟲首頁](/public/image/fetch_jobs.jpg)
![首頁爬蟲演示](/public/image/fetch_jobs.gif)

 [觀看影片演示連結](https://youtu.be/R7QqjPjOSg4)

## 專案功能

- 自動登入 CakeResume 帳號
- 抓取已應徵職缺的詳細資訊，包括公司名稱、職缺名稱、應徵狀態等
- 將結果存為 HTML 檔案，並支援以 JSON 格式輸出
- 使用環境變數管理登入憑證，確保資訊安全

## 系統需求

### Python 環境與套件

- Python 3.12
- Django 5.1
- Selenium 4.23.1
- BeautifulSoup 4.12.3
- Requests 2.32.3
- python-dotenv 1.0.1

### 工具與瀏覽器

- Firefox 瀏覽器
- Geckodriver
- Poetry（用於管理虛擬環境與依賴）

## 安裝與設定

### 1. 克隆專案

首先，將專案克隆到本地環境並進入專案目錄：

```bash
$ git clone git@github.com:chenstephen0501/job_crawler.git
$ cd job_crawler
```

### 2. 虛擬環境初始化

```bash
$ pip install poetry
```

### 3. 進入虛擬環境
```bash
$ poetry shell
$ poetry install
```

### 3. 啓動專案
```bash
$ python manage.py runserver
```

### 5. 執行爬蟲
1. 打開瀏覽器，訪問 http://127.0.0.1:8000 頁面，點擊按鈕執行爬蟲，結果將以 JSON 格式返回。

2. 使用 Postman 發送 API 請求：

    - GET http://127.0.0.1:8000/jobs/fetch_cake/：抓取指定應徵職缺資訊
    - GET http://127.0.0.1:8000/jobs/fetch_cake_all/：抓取所有應徵職缺資訊
    - GET http://127.0.0.1:8000/jobs/user_apply_jobs/：手動觸發爬蟲，並獲取應徵職缺結果

### 4. 設定環境變數

- DEBUG=True
- SECRET_KEY=your_secret_key
- CAKE_EMAIL=your_email@example.com
- CAKE_PASSWORD=your_password
