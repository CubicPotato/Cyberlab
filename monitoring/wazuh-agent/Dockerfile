FROM wazuh/wazuh-agent:4.14.3

RUN yum install -y python3-pip && \
    pip3 install --no-cache-dir \
        docker==7.1.0 \
        urllib3==1.26.20 \
        requests==2.32.2 && \
    yum clean all