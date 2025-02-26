FROM python:3.10-slim

WORKDIR /app

RUN apt update
#RUN apt install -y build-essential libc6-dev libc-bin locales
RUN apt install -y build-essential
RUN ldconfig
#RUN export LD_LIBRARY_PATH=/lib/aarch64-linux-gnu/:$LD_LIBRARY_PATH
COPY requirements.txt .

RUN mkdir deps
COPY deps/* ./deps
# In your Dockerfile


# In your Dockerfile

#ENV PIP_INDEX_URL=http://146.75.72.223:8080/simple/
#ENV PIP_TRUSTED_HOST=146.75.72.223


#RUN pip install --index-url=${PIP_INDEX_URL} --trusted-host=${PIP_TRUSTED_HOST} requests



#RUN pip install --trusted-host=${PIP_TRUSTED_HOST} -r requirements.txt


#RUN pip install --find-links=deps/ -r requirements.txt --no-index

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "server.py"]
