FROM mcr.microsoft.com/devcontainers/base:ubuntu

COPY install-tools.sh ./install-tools.sh
RUN chmod +x install-tools.sh && ./install-tools.sh --tools=all

# Clean up
RUN rm install-tools.sh install-tools.log install-summary.json