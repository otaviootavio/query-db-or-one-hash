# Use Ubuntu as the base image
FROM ubuntu:20.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Install necessary packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    redis-server \
    postgresql \
    mysql-server \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install redis psycopg2-binary mysql-connector-python

# Copy the benchmark script and SQL files into the container
COPY benchmark.py init_postgres.sql init_mysql.sql /app/

# Setup PostgreSQL
RUN service postgresql start && \
    su - postgres -c "psql -c \"ALTER USER postgres WITH PASSWORD 'password';\"" && \
    su - postgres -c "createdb testdb" && \
    su - postgres -c "psql -d testdb -f /app/init_postgres.sql"

# Setup MySQL
RUN service mysql start && \
    mysqladmin -u root password 'password' && \
    mysql -u root -ppassword -e "CREATE DATABASE IF NOT EXISTS testdb; CREATE USER IF NOT EXISTS 'user'@'localhost' IDENTIFIED BY 'password'; GRANT ALL PRIVILEGES ON testdb.* TO 'user'@'localhost'; FLUSH PRIVILEGES;" && \
    mysql -u root -ppassword testdb < /app/init_mysql.sql

# Create a script to start services and run the Python script
RUN echo '#!/bin/bash\n\
service redis-server start\n\
service postgresql start\n\
service mysql start\n\
python3 /app/benchmark.py' > /app/run.sh && \
chmod +x /app/run.sh

# Make ports available to the world outside this container
EXPOSE 6379 5432 3306

# Run the script when the container launches
CMD ["/app/run.sh"]