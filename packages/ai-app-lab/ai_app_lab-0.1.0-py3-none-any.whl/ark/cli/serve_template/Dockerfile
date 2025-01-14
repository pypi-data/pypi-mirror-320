FROM python:3.9.5

ARG SDK_WHEEL="ark-0.1.1-py3-none-any.whl"
ARG SDK_URL=https://maas-assistant.tos-cn-beijing.volces.com/sdk/${SDK_WHEEL}

COPY code /opt/application/code
COPY run.sh /opt/application/run.sh

RUN wget ${SDK_URL} -O ${SDK_WHEEL}
RUN pip install ${SDK_WHEEL}

WORKDIR /opt/application
USER root

RUN chmod a+x /opt/application/run.sh
CMD /opt/application/run.sh