# Note:
#   This DockerFile was created for MoneyPrinterPlus v4.7 with the aim of reducing usage costs and hoping that more people can experience its charm.
#   Human civilization is the development of productive forces guided by production tools, and we hope that this tool can contribute a little bit to human civilization.
#   If you have any questions, please feel free to contact the author or me.
#                                                   Email: fengapi@gmail.com
#
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12-slim
ENV DEBIAN_FRONTEND noninteractive
#
MAINTAINER zihan<fengapi@gmail.com>
# Include dist
COPY dist/ /root/dist/
#

# Set Mirrors For China & Install Base
Run sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    cd /root/dist/ && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends \
            tzdata \
            build-essential \
            python3-full \
            python3-dev \
            python3-pip \
            python3-yaml \
            ffmpeg \
            portaudio19-dev \
            libgtk-3-dev \
            git && \

# Set China pip Mirrors
    pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip3 install --break-system-packages --upgrade pip && \
#
# Get For MoneyPrinterPlus v4.7
    cd /root/dist/ && \
    git clone -b v4.7 https://github.com/ddean2009/MoneyPrinterPlus.git && \
    pip install --break-system-packages --no-cache-dir --ignore-installed -r /root/dist/MoneyPrinterPlus/requirements.txt  && \
    chmod +x /root/dist/rmmp.sh && \
#
#
# Setup runtime and clean up
    apt-get autoremove --purge -y  && \
    apt-get clean 
#
#
# Start Gui & Port[default]
#
EXPOSE 8501
WORKDIR /root/dist/
CMD ["/root/dist/rmmp.sh"]


# Use official slim Python base image
FROM python:3.12-slim

# Set environment to non-interactive to avoid tzdata prompts
ENV DEBIAN_FRONTEND=noninteractive

# Set maintainer info
LABEL maintainer="AppleCakes14 lohvy-wm21@student.tarc.edu.my"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-pip \
    python3-yaml \
    ffmpeg \
    portaudio19-dev \
    libgtk-3-dev \
    git \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Clone your MoneyPrinterPlus repo
RUN git clone -b main https://github.com/AppleCakes14/MoneyPrinterPlus.git /app

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose default port (Streamlit or similar)
EXPOSE 8501

# Entry point script — adjust if you have a different launch command
CMD ["bash", "./rmmp.sh"]
