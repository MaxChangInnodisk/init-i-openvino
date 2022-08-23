# ivit-i-intel
FROM openvino/ubuntu18_dev_no_samples

USER root

# RUN ln -sf /bin/bash /bin/sh && ln -sf /bin/bash /bin/sh.distrib
# SHELL ["/bin/bash", "-ec"]

COPY ["./utils.sh", "./requirements.sh", "/workspace/" ]

WORKDIR /workspace

RUN chmod u+x /workspace/*.sh \
&& ./requirements.sh

ENTRYPOINT [ "/bin/bash", "-c" ]

CMD [ "bash" ]
