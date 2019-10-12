FROM alwaysai/edgeiq:0.7.19
FROM python:3.7-alpine
RUN pip3 install -r requirements.txt
RUN curl -Ss https://bootstrap.pypa.io/get-pip.py | python3