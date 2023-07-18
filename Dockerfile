FROM python:3.10-alpine

# Install dependencies

RUN apk update \
    && apk add build-base libffi-dev \
    && pip install --upgrade pip

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD . /action
WORKDIR /action

# Set the entrypoint
ENTRYPOINT ["python", "/action/src/pr_checks.py"]
