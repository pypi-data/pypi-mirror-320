FROM ubuntu:20.04
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3
ENV DEBIAN_FRONTEND=noninteractive
ENV HARDWARE_TARGET="cpu"
ENV TF_CPP_MIN_LOG_LEVEL='3'
ARG MODEL_TO_LOAD={{MODEL_TO_LOAD}} LANGUAGE={{LANGUAGE}} JOHNSNOWLABS_VERSION={{JOHNSNOWLABS_VERSION}} STORE_LICENSE={{STORE_LICENSE}} STORE_MODEL={{STORE_MODEL}}
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME
RUN echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/" >> ~/.bashrc
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8


RUN apt-get update && apt-get install --no-install-recommends -y \
        python3 \
        python3-dev \
        python3-pip \
        openjdk-8-jdk \
        curl && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
        && mkdir -p /app/model_cache


COPY ./ /app/
# Install Johnsnowlabs libraries
RUN pip config set global.no-cache-dir 1 && pip install -r /app/requirements.txt

# Install the model using Johnsnowlabs
RUN --mount=type=secret,id=license python3 /app/installer.py --model=$MODEL_TO_LOAD --language=$LANGUAGE --store_license=$STORE_LICENSE --store_model=$STORE_MODEL && rm -rf /root/.javacpp/* /tmp/*

# Setup Fast-API app
WORKDIR /app
COPY serve /opt/program/serve
RUN chmod 755 /opt/program/serve
ENV PATH=/opt/program:${PATH}
ENV PYTHONPATH=/app

