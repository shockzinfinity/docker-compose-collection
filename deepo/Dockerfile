FROM ufoym/deepo:all-cpu
ARG DEBIAN_FRONTEND=noninteractive
RUN wget https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    apt-get install -y apt-transport-https && \
    apt-get update && \
    apt-get install -y dotnet-sdk-5.0 && \
    apt-get install -y aspnetcore-runtime-5.0 && \
    dotnet tool install -g Microsoft.dotnet-interactive

RUN apt install gpg-agent -y
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -

RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt update
RUN apt install google-chrome-stable zip xvfb -y

RUN wget -N https://chromedriver.storage.googleapis.com/95.0.4638.54/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip

ENV PATH "~/.dotnet/tools:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

RUN pip install selenium xlrd pyvirtualdisplay

RUN dotnet interactive jupyter install
