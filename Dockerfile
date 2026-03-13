# SPDX-FileCopyrightText: 2018 Nextcloud GmbH and Nextcloud contributors
# SPDX-License-Identifier: AGPL-3.0-or-later

# --- Stage 1: Node.js Frontend Build ---
FROM node:18 as node

WORKDIR /srv

COPY nextcloudappstore/core/static nextcloudappstore/core/static
COPY package.json package-lock.json ./
COPY webpack.config.js webpack.config.js
COPY tsconfig.json tsconfig.json

RUN npm ci
RUN npm run build


# --- Stage 2: Translations ---
FROM python:3.12 as translations

WORKDIR /srv

RUN apt-get update && apt-get install -y gettext libgettextpo-dev

# Install Poetry
RUN pip install --upgrade pip wheel && pip install poetry==1.8.2

# Copy dependency files and install
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY nextcloudappstore nextcloudappstore
COPY manage.py manage.py
COPY locale locale

# Provide a temporary secret key in order to be able to run the compile messages command
RUN echo "SECRET_KEY = 'secret'" >> nextcloudappstore/settings/base.py
RUN python manage.py compilemessages --settings=nextcloudappstore.settings.base


# --- Stage 3: Main App ---
FROM python:3.12 as main

ARG platform=production
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

WORKDIR /srv

# Install Poetry
RUN pip install --upgrade pip wheel && pip install poetry==1.8.2

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies based on platform (development vs production)
RUN poetry config virtualenvs.create false && \
    if [ "$platform" = "production" ]; then \
        poetry install --without dev --no-interaction --no-ansi; \
    else \
        poetry install --no-interaction --no-ansi; \
    fi

COPY nextcloudappstore nextcloudappstore
COPY manage.py manage.py
COPY scripts/build/start.sh start.sh

# Clean up static directory and pull compiled assets/translations from previous stages
RUN rm -rf nextcloudappstore/core/static
COPY --from=node /srv/nextcloudappstore/core/static nextcloudappstore/core/static
COPY --from=translations /srv/locale locale

RUN groupadd nextcloudappstore && \
    useradd -g nextcloudappstore -s /bin/false nextcloudappstore && \
    chown -R nextcloudappstore:nextcloudappstore /srv

ENTRYPOINT ["/srv/start.sh"]
