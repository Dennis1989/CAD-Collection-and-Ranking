# Using the -slim version below for minimal size. You may want to
# remove -slim, or switch to -alpine if encountering issues
#ARG BASE_TAG=python3.9-nodejs15-slim
ARG BASE_TAG=python3.9-nodejs16-bullseye
ARG BASE_IMAGE=nikolaik/python-nodejs:$BASE_TAG

FROM $BASE_IMAGE

# Create the main Mephisto data directory
RUN mkdir /data

# create mephisto config dir
RUN mkdir ~/.mephisto
# Write the mephisto config file manually for now to avoid prompt.
RUN echo "core: "                       >> ~/.mephisto/config.yml
RUN echo "  main_data_directory: /data" >> ~/.mephisto/config.yml

# clone mephisto repo
RUN git clone https://github.com/facebookresearch/Mephisto.git /mephisto

# Upgrade pip so we can use the pyproject.toml configuration
# without raising an error
RUN pip install --upgrade pip
# install mephisto
RUN cd /mephisto && pip install -e .
# install mongoengine
RUN pip install mongoengine

WORKDIR /app
# copy our files
COPY . .
RUN ln -s /app/blueprints/* /mephisto/mephisto/abstractions/blueprints/

# initial yarn install & build
RUN cd webapp && yarn install && yarn run dev

CMD ["python", "run_task.py"]
