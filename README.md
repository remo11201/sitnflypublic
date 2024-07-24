# ICT2216-SSD-Group-16
### requirements 
install python    
pip install django  
pip install django-simple-captcha
pip install python-decouple
pip install mysqlclient
pip install django-admin-logs


    
python manage.py makemigrations  
python manage.py migrate  
python manage.py runserver 

To run locally swap the comments on 'default' in settings.py line 81+

admin@mail.com  
password  
http://127.0.0.1:8000/admin/ to see tables

### connect to mysql ec2 with putty
Host Name: Enter 3.145.122.51  
Set Port to 22  
Select SSH in Connection type  
Navigate to Connection > SSH > Auth > Credentials.  
Under Authentication parameters, click Browse and select your .ppk file (e.g., ICT2216-student8.ppk).  
Navigate to Connection > SSH > Tunnels.  
Source port: Enter 3306. (make sure port 3306 not being used, end MariaDB in Services Control Panel if using)  
Destination: Enter 127.0.0.1:3306.
Click Add. You should see L3306 127.0.0.1:3306 in the forwarded ports list.

Save the Session (Optional):  
Go back to the Session category.  
Enter a name under Saved Sessions and click Save.  
  
Connect to the EC2 Instance:  
Click Open to start the SSH session with the configured tunnel.  
log in as student8.

  





