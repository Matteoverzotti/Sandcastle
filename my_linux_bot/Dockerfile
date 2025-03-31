FROM ubuntu:22.04

# Install dependencies
RUN apt update && apt install -y docker.io docker-compose curl

# Set correct permissions
RUN mkdir -p /services/web /services/ssh && chmod -R 777 /services

WORKDIR /services
CMD ["/bin/bash"]

