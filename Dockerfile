FROM openjdk:17
# ffmpeg 설치
RUN apt-get update && apt-get install -y ffmpeg
ARG JAR_FILE=build/libs/*.jar
COPY ${JAR_FILE} app.jar
ENTRYPOINT ["java","-jar","/app.jar"]