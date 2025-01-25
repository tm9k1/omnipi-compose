FROM ubuntu:22.04
WORKDIR /opt
RUN apt update
RUN apt install -y wget openjdk-21-jre-headless
ENTRYPOINT [ "java", "-Dnogui=true", "-jar", "/opt/JMusicBot.jar" ]
