##########################################################################
# This is a multi-stage dockerfile. The builder stage installs compiler etc
# because PyYAML requires gcc. This bloats up the image.
# We basically build all the requirements in a virtualenv in the builder stage
# and copy over the entire virtualenv directory in the final stage.
##########################################################################

FROM python:3.10-alpine as builder

# Install dependencies

RUN apk update \
    && apk add build-base libffi-dev \
    && pip install virtualenv

RUN virtualenv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

##########################################################################
# Final stage - will just copy over the virtual env
##########################################################################


FROM python:3.10-alpine

RUN apk update \
    && pip install virtualenv

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

ADD . /action
WORKDIR /action

# Set the entrypoint
ENTRYPOINT ["python", "/action/src/pr_checks.py"]
