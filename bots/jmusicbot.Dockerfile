FROM ubuntu
WORKDIR /opt
RUN apt update
RUN apt install -y wget openjdk-18-jre-headless
#RUN wget https://github.com/jagrosh/MusicBot/releases/download/0.3.9/JMusicBot-0.3.9.jar
ENTRYPOINT [ "java", "-Dnogui=true", "-jar", "/opt/JMusicBot-0.3.9.jar" ]
