FROM python:3.12-bookworm

WORKDIR /py-backapp
COPY ./backapp.py .

CMD [ "python3", "./backapp.py" ]