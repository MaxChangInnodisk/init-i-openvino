# ivit-i-intel
FROM openvino/ubuntu18_dev_no_samples

USER root

COPY ["./utils.sh", "./requirements.sh", "/workspace/" ]

WORKDIR /workspace

RUN chmod u+x /workspace/*.sh \
&& ./requirements.sh

# `inno_verify` will be generated when execute gen_inno_verify.sh which base on the source code from ivit_i library
COPY [ "./inno_verify", "./entrypoint",  "/usr/bin/" ]

ENTRYPOINT [ "entrypoint" ]
