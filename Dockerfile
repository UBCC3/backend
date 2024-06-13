FROM ubuntu:22.04
RUN echo 'APT::Install-Suggests "0";' >> /etc/apt/apt.conf.d/00-docker
RUN echo 'APT::Install-Recommends "0";' >> /etc/apt/apt.conf.d/00-docker
RUN DEBIAN_FRONTEND=noninteractive \
  apt-get update \
  && apt-get install -y python3  git python3-pip  libpq-dev gcc python3-dev\
  && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/UBCC3/UI.git
RUN cd UI && git checkout feat/fast-api
RUN pip install -r UI/server/requirements.txt
WORKDIR UI/server
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
