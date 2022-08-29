# ivit-i-intel
FROM openvino/ubuntu18_dev_no_samples

USER root

COPY ["./utils.sh", "./requirements.sh", "/workspace/" ]

WORKDIR /workspace

RUN chmod u+x /workspace/*.sh \
&& ./requirements.sh

# RUN ln -sf /bin/bash /bin/sh && ln -sf /bin/bash /bin/sh.distrib && tree `pwd`
# SHELL ["/bin/bash", "-ec"]

COPY ["./entrypoint.sh", "/" ]
# ENTRYPOINT [ "/bin/bash", "-c", "source /entrypoint.sh" ]
ENTRYPOINT [ "/entrypoint.sh" ]

# CMD [ "bash" ]

# ENTRYPOINT [ "ls" ]
