FROM python:3.10.11
WORKDIR /imageRipples
COPY ./app /imageRipples/app
COPY ./requirements.txt main.py /imageRipples/
RUN pip install -r requirements.txt
RUN transformers-cli download bert-base-uncased google/vit-base-patch16-224
EXPOSE 6002
CMD ["python", "./app/main.py"]
