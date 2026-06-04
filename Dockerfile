FROM eclipse-temurin:17-jdk

WORKDIR /app

COPY target/gameapp-1.0.0.jar app.jar

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]
