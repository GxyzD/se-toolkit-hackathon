FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html
COPY style.css /usr/share/nginx/html/static/style.css
COPY script.js /usr/share/nginx/html/static/script.js

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]