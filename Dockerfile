FROM python:3.8.6-buster

ENV APP_PATH /usr/src/app
RUN mkdir -p ${APP_PATH}

WORKDIR ${APP_PATH}
COPY . ${APP_PATH}/
RUN pip install -r requirements.txt

EXPOSE 8050/tcp

CMD ["python", "score-tool.py"]