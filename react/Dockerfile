FROM node:alpine as builder

RUN mkdir /root/react
WORKDIR /root/react

COPY . ./

RUN npm install
RUN npm run-script build

#production environment
FROM nginx:alpine
COPY --from=builder /root/react/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
