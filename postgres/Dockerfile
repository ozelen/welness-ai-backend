FROM postgres:16

# Install build dependencies
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        git \
        postgresql-server-dev-16 \
    && rm -rf /var/lib/apt/lists/*

# Clone and install pgvector
RUN cd /tmp \
    && git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install

# Clean up
RUN apt-get remove -y build-essential git postgresql-server-dev-16 \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /tmp/pgvector 
