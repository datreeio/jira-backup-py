FROM python:3.8
COPY ./ /backup
RUN chown -R backup:backup /var/backups
WORKDIR /backup
RUN pip install -r requirements.txt
USER backup
ENTRYPOINT ["python", "backup.py"]
