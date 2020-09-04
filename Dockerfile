FROM python:3.7.4-alpine

COPY ./*.py /python/
COPY ./requirements.txt /python/

RUN pip install -r /python/requirements-ci.txt

WORKDIR /python

CMD ["python", "Get-Repo.py"]