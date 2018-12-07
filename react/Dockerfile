FROM node:9.6.1:alpine as builder

RUN mkdir /root/react
WORKDIR /root/react

COPY . ./

RUN npm install
RUN npm run-script build



