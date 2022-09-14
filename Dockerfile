FROM python:3.9

ADD cacert.crt /usr/local/share/ca-certificates/foo.crt
RUN chmod 644 /usr/local/share/ca-certificates/foo.crt 
RUN update-ca-certificates

ADD . .

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED = 1

CMD python ./event.py
