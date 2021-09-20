FROM python:3.7

LABEL maintainer "Athenkosi Dyoli <athenkosidyoli@gmail.com>"
COPY ./ ./
WORKDIR ./
RUN pip install -r requirements.txt
EXPOSE 5040
CMD ["python", "covid_dash.py", "--host", "0.0.0.0"]
