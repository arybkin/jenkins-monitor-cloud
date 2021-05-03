FROM python:3.8

ENV PROJECT_DIR /usr/src/jenkins-monitor

COPY *.py ${PROJECT_DIR}/
COPY *.txt ${PROJECT_DIR}/
COPY *.json ${PROJECT_DIR}/
#COPY *.json ${PROJECT_DIR}/

WORKDIR ${PROJECT_DIR}

RUN pip install -r requirements.txt

EXPOSE 80

RUN ls -la

CMD ["python", "app.py"]
