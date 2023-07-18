FROM python:3.10-alpine

ADD . /action
WORKDIR /action
# Install dependencies

RUN apk update && apk add build-base libffi-dev
RUN pip install "Cython<3.0" pyyaml --no-build-isolation
RUN pip install -r requirements.txt

# Set the entrypoint
ENTRYPOINT ["python", "/action/src/pr_checks.py"]
