FROM node:18 AS build
ARG VERSION
WORKDIR /opt
# RUN apk add git
# RUN git clone https://github.com/excalidraw/excalidraw node_app
RUN wget https://github.com/excalidraw/excalidraw/archive/refs/tags/v$VERSION.zip
RUN unzip v$VERSION.zip
RUN ls
WORKDIR /opt/excalidraw-$VERSION
RUN ls
RUN yarn --ignore-optional --network-timeout 600000

ARG NODE_ENV=production

RUN yarn build:app:docker

FROM nginx:1.21-alpine
ARG VERSION
COPY --from=build /opt/excalidraw-$VERSION/build /usr/share/nginx/html

HEALTHCHECK CMD wget -q -O /dev/null http://localhost || exit 1
