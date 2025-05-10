I got social login to work, it's running on a google workspace that I made with my google account. When the website is pushed onto the web, whoever is responsible for deployment will make a new one.  
If you wanna test it out:
- make and run migrations
- go to the admin dashboard
- click "Social applications"
- click "Add"
- Keep provider at "Google"
- Provider ID: blank
- Name: (anything, I called it "Google Login")
- Client id: cant put these here for protection reasons
- Secret key: cant put these here for protection reasons  
(i can send in gc)
- Settings: Try leaving this blank, if there is an issue, put:
``` {"SCOPE": ["profile", "email"], "AUTH_PARAMS": {"access_type": "online"}} ```
- Sites:
 - In the "Chosen sites" tab, add http://127.0.0.1:8000, http://localhost:8000, localhost, 127.0.0.1:8000. Some of these are probably redunant but I put then in there just in case.
- Now refresh and social login should work!

### Also, you must use http://127.0.0.1:8000 instead of localhost:8000