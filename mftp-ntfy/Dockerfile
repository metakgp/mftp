FROM binwiederhier/ntfy

COPY server.yml /etc/ntfy/server.yml

EXPOSE 8000

ENTRYPOINT ["ntfy", "serve"]