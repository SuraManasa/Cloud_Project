FROM python:3.7

RUN mkdir /stock
COPY requirements.txt /stock/requirements.txt
WORKDIR /stock
RUN pip3 install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
COPY . /stock/
EXPOSE 80
CMD ["python3", "wsgi.py"]
