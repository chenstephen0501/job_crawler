FROM python:3.12

# 設定工作目錄
WORKDIR /app

# 安裝 Poetry
RUN pip install poetry

# 安裝 Firefox 和 geckodriver
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    && wget https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux64.tar.gz \
    && tar -xzf geckodriver-v0.32.0-linux64.tar.gz \
    && mv geckodriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver \
    && rm geckodriver-v0.32.0-linux64.tar.gz

# 複製 Poetry 配置文件
COPY pyproject.toml poetry.lock* /app/

# 安裝依賴，並確保 Poetry 使用虛擬環境
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-dev --no-interaction --no-ansi

# 複製應用程式代碼
COPY . /app

# 暴露端口 8000
EXPOSE 8000

# 設置容器啟動時執行的命令
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
