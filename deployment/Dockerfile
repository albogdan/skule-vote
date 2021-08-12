FROM python:3.9-buster

# Set working directory
WORKDIR /usr/src/skule_vote

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set time zone
RUN cp /usr/share/zoneinfo/Canada/Eastern /etc/localtime \
  && echo "America/Toronto" > /etc/timezone

# Install dependencies
RUN apt-get update && apt-get install -y postgresql-client

RUN pip install --upgrade pip
COPY skule_vote/requirements.txt /usr/src/skule_vote/requirements.txt
RUN pip install -r /usr/src/skule_vote/requirements.txt

# Copy app
COPY skule_vote/ /usr/src/skule_vote/

# Copy entrypoint
COPY deployment/entrypoint.sh /usr/src/entrypoint.sh
RUN chmod +x /usr/src/entrypoint.sh
ENTRYPOINT ["/usr/src/entrypoint.sh"]
