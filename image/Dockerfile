# Ververica base to run in VVP with Flink 1.18

FROM registry.ververica.com/v2.14/flink:1.18.1-stream5-scala_2.12-java11

USER root:root

RUN pip install tensorflow-cpu==2.17 scikit-learn protobuf==3.20.3

USER flink:flink