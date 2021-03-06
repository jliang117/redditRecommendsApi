FROM python:3.6

# Install python and pip
COPY requirements.txt /requirements.txt

RUN pip install --upgrade pip 
RUN pip install -r /requirements.txt 
RUN python -m spacy download en_core_web_sm
# Add our code
ADD ./webapp /opt/webapp/
WORKDIR /opt/webapp

# Expose is NOT supported by Heroku
# EXPOSE 5000 		

# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku			
CMD gunicorn --bind 0.0.0.0:$PORT wsgi 

