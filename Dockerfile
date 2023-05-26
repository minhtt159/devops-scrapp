FROM --platform=linux/amd64 condaforge/mambaforge AS build

COPY environment.yml environment.yml

RUN conda env create -f environment.yml
# Install conda-pack:
RUN conda install -c conda-forge conda-pack

# Use conda-pack to create a standalone enviornment
# in /venv:
RUN conda-pack -n scrapp -o /tmp/env.tar && \
    mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
    rm /tmp/env.tar

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN /venv/bin/conda-unpack

FROM --platform=linux/amd64 ubuntu AS runtime

# Copy /venv from the previous stage:
COPY --from=build /venv /venv

WORKDIR /app

COPY code/ /app