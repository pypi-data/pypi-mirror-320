FROM ubuntu:20.04
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3
ENV DEBIAN_FRONTEND=noninteractive
ENV TF_CPP_MIN_LOG_LEVEL='3'
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME
RUN echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/" >> ~/.bashrc
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8
{{ENVIRONMENT_VARIABLES}}


RUN apt-get update && apt-get install --no-install-recommends -y \
        python3 \
        python3-dev \
        python3-pip \
        openjdk-8-jdk \
        curl && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


COPY ./ /app/
RUN pip config set global.no-cache-dir 1 && pip install -r /app/requirements.txt

WORKDIR /app
ENV PYTHONPATH=/app

RUN --mount=type=secret,id=license {{SETUP_ENVIRONMENT}}


{{ENTRYPOINT}}
