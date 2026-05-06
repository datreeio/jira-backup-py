FROM python:3.14-alpine
COPY ./ /backup
RUN adduser -D backup
RUN chown -R backup:backup /backup
WORKDIR /backup
RUN pip install --no-cache-dir ".[all]"
USER backup
ENTRYPOINT ["python", "-m", "jira_backup"]
