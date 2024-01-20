FROM ubuntu

# Install dependencies
RUN apt-get update 
RUN apt-get install -y \
    python3-pip
RUN pip3 install docker
RUN mkdir /hoster
WORKDIR /hoster
ADD hoster.py /hoster/

CMD ["python3", "-u", "hoster.py"]


