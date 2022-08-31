# ivit-i-intel
FROM openvino/ubuntu18_dev_no_samples

USER root
ENV WS=/opt/inno/ivit_i
WORKDIR $WS

COPY ["./utils.sh", "./requirements.sh", "./py-requirements.txt", "${WS}/" ]

RUN pwd ${WS}/ && ls ${WS}/ \
&& chmod u+x ${WS}/*.sh \
&& ${WS}/requirements.sh \
&& rm -rf ${WS}/*.sh

# `inno_verify` will be generated when execute gen_inno_verify.sh which base on the source code from ivit_i library
COPY [ "./inno_verify", "./entrypoint",  "/usr/bin/" ]

WORKDIR /workspace

ENTRYPOINT [ "entrypoint" ]
