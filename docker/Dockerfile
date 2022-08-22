# ivit-i-intel

FROM openvino/ubuntu18_dev_no_samples

WORKDIR /workspace

COPY ["./utils.sh", "./requirements.sh", "/workspace/" ]

USER root

ENV DEBIAN_FRONTEND noninteractive  

RUN chmod +x ./requirements.sh \
&& ./requirements.sh \
&& rm ./*.sh

ENTRYPOINT [ "/bin/bash", "-c" ]
