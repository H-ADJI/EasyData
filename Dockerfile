# # FROM ubuntu:20.04
FROM  mcr.microsoft.com/playwright:v1.22.0-focal
RUN apt-get update && apt-get install -y software-properties-common gcc && \
    add-apt-repository -y ppa:deadsnakes/ppa && apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev -y
# RUN apt install python3.10 -y
RUN wget https://www.python.org/ftp/python/3.8.14/Python-3.8.14.tar.xz
RUN tar -xf Python-3.8.14.tar.xz
RUN cd Python-3.8.14/ && ./configure --enable-optimizations && make -j $(nproc) && make altinstall
ENV PYTHONUNBUFFERED=1
ENV LANG C.UTF-8
# This is our runtime
RUN ln -sf /usr/bin/pip3 /usr/bin/pip
RUN ln -sf /usr/bin/python3 /usr/bin/python
# This is dev runtime
# RUN apt add --no-cache --virtual .build-deps build-base python3-dev
# RUN apt add --no-cache libffi-dev gcc musl-dev make
# Using latest versions, but pinning them
RUN apt install python3-pip -y && pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --no-cache-dir pipenv
WORKDIR /news-sites-analytics
# RUN pipenv --python 3.10
RUN python3 --version
COPY Pipfile Pipfile.lock ./

RUN pipenv install
RUN pipenv run playwright install
RUN apt-get update && pipenv run playwright install-deps
# RUN pipenv shell
COPY . ./
EXPOSE 8011
# CMD [ "uvicorn","main:app","--reload" ]



