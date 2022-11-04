FROM python:3.8.14-slim
RUN apt-get update 
# setting PYTHONUNBUFFERED to a value different from 0 ensures that the python output i.e. the stdout and stderr streams are sent straight to terminal (e.g. your container log) 
ENV PYTHONUNBUFFERED=1
# setting Lang env var For standard language support
ENV LANG C.UTF-8
# Symbolic links to pip and python for ease of use
RUN ln -sf /usr/bin/pip3 /usr/bin/pip
RUN ln -sf /usr/bin/python3 /usr/bin/python
# Installing and upgrading package manager
RUN apt-get install python3-pip -y && pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --no-cache-dir pipenv
# setting the working directory to the project folder
WORKDIR /news-sites-analytics
RUN python3 --version
COPY Pipfile Pipfile.lock ./
# Installing project dependencies
RUN pipenv install --dev
RUN pipenv run playwright install chromium
RUN pipenv run playwright install-deps chromium
COPY . ./
EXPOSE 8000

