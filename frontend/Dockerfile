FROM nginx:alpine

# The frontend is a single self-contained HTML/CSS/JS file (no build step
# needed). Nginx just serves it as a static site.
COPY public /usr/share/nginx/html
# nginx serves index.html by default -- app.html is the actual page.
RUN cp /usr/share/nginx/html/app.html /usr/share/nginx/html/index.html

EXPOSE 80
