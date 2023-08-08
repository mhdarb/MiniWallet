# MiniWallet
**Setup Using Docker**
1. Install Docker in your system.
2. Clone git repo and open it in code editor(VsCode) etc.
3. Run command: docker-compose up --build.This will build the container from image and install all requirement dependencies.After that the container will run the server on the mentioned port.
4. Container is now running at http://localhost:8000
5. Import the postman collection and start testing apis first by creating a customer and so on.
6. After creating customer and initializing wallet account use the token received for subsequent requests.

**Setup Without Using Docker**
1. Install python3 in your system and add it to system env variables.
2. Clone git repo and open code in any editor like V.S Code.
3. Run command : pip install -r requirements.txt in the project directory.
4. Run migrations command :
     1. python manage.py makemigrations account
     2. python manage.py migrate
5. Run server : python manage.py runserver 8000


**Assumptions:**
1. Used Django User model as base model for creating customer
2. Used django rest framework TokenAuthentication for handling authorization and authentication of requests.
3. Assumed that transaction will be failed for already existing transaction with  same reference_id.
4. For deposit and withdrawal functionality taken safety measures for concurrency control using lock while updating balance so that other
   similar requests of deposit/withdrawal does not affect the current executing transaction.
5. As mentioned that a max delay in a transaction of deposit/withdraw can happen of 5 seconds.For that used sleep method to wait for random seconds between 1 and 5 and process request.

