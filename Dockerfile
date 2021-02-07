FROM ubuntu
ENV TZ=Europe/Moscow
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install tzdata && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt install python3.8 python3-pip -y && python3.8 -m pip install setuptools wheel aiomoex requests pandas aiostream beautifulsoup4 pycbrf && mkdir /bot

COPY . /bot/

ENTRYPOINT  python3.8 /bot/dollar-mon.py
