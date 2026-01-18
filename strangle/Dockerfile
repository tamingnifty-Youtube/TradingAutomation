# Start from python slim-buster docker image
FROM python:3.11.8-slim
# Update base packages
RUN apt-get update -y
RUN apt-get upgrade -y
# Change TimeZone
ENV TZ=Asia/Calcutta
ENV slack_token=" "
ENV INTEGRATE_API_TOKEN=" "
ENV INTEGRATE_API_SECRET=" "
ENV TOTP=""
ENV CONNECTION_STRING=" "
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN echo $(date)
# Copy files to working directory
COPY /strangle.py /app/src/
COPY /requirements.txt /app/src/
WORKDIR /app
# Install python packages using requirements.txt
RUN pip install -r src/requirements.txt

# Run the script
CMD ["python", "src/strangle.py"]