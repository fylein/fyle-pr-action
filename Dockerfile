FROM python:3.10-alpine

ADD . /action
WORKDIR /action
# Install dependencies
RUN pip install -r requirements.txt

# Set the entrypoint
ENTRYPOINT ["python", "/action/src/pr_checks.py"]
