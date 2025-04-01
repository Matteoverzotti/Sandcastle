FROM ubuntu:18.04
RUN apt update && apt install -y apache2 && apt install -y curl
COPY vulnerable_index.html /var/www/html/index.html

# Redirect Apache logs to stdout and stderr
RUN ln -sf /dev/stdout /var/log/apache2/access.log && \
    ln -sf /dev/stderr /var/log/apache2/error.log

CMD ["apachectl", "-D", "FOREGROUND"]
