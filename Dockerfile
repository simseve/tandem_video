# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y build-essential wget ffmpeg libmagick++-dev --no-install-recommends && \
#    apt-get install -y libmagick++-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

## ImageMagicK Installation ##
RUN mkdir -p /tmp/distr && \
    cd /tmp/distr && \
    wget https://download.imagemagick.org/ImageMagick/download/releases/ImageMagick-7.0.11-2.tar.xz && \
    tar xvf ImageMagick-7.0.11-2.tar.xz && \
    cd ImageMagick-7.0.11-2 && \
    ./configure --enable-shared=yes --disable-static --without-perl && \
    make && \
    make install && \
    ldconfig /usr/local/lib && \
    cd /tmp && \
    rm -rf distr

COPY . .

VOLUME /app/output

# Modify the policy.xml file
# RUN sed -i 's|<policy domain="path" rights="none" pattern="@*"/>|<!-- <policy domain="path" rights="none" pattern="@*"/> -->|g' /etc/ImageMagick-6/policy.xml

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
ENTRYPOINT ["python", "app.py"]
CMD ["-f", "clip_short.mp4", "-n", "Test Pilot", "-d", "23/04/2023", "-l", "Test Location", "-v", "0.3"]
