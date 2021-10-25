FROM ufoym/deepo:all-cpu
ARG DEBIAN_FRONTEND=noninteractive
RUN wget https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    apt-get install -y apt-transport-https && \
    apt-get update && \
    apt-get install -y dotnet-sdk-5.0 && \
    apt-get install -y aspnetcore-runtime-5.0 && \
    dotnet tool install -g Microsoft.dotnet-interactive

ENV PATH "~/.dotnet/tools:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

RUN dotnet interactive jupyter install
