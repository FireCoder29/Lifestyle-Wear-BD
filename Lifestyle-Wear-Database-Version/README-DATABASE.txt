LIFESTYLE WEAR — DATABASE STOCK VERSION
========================================

IMPORTANT
---------
This is a SEPARATE copy. Do not replace your real Lifestyle-Wear folder.
Copy the files/code into your real folder only after you test this version.

WHAT WAS ADDED
--------------
backend/main.py          FastAPI + SQLite database + stock/order API
backend/requirements.txt Python packages
backend/.env.example     Example admin-key setting
admin.html                Simple stock management page
script.js                 Connected to the stock API

1) START THE BACKEND
--------------------
Open Command Prompt/PowerShell inside the backend folder:

    cd backend
    pip install -r requirements.txt
    uvicorn main:app --reload

The API will run at:
    http://127.0.0.1:8000

The database file is created automatically:
    backend/lifestyle_wear.db

2) SET AN ADMIN KEY
-------------------
Before using admin.html, set an environment variable.
Windows CMD:
    set LW_ADMIN_KEY=your-private-key
    uvicorn main:app --reload

PowerShell:
    $env:LW_ADMIN_KEY="your-private-key"
    uvicorn main:app --reload

3) TEST THE WEBSITE
-------------------
The current script.js is configured for:
    http://127.0.0.1:8000

Use VS Code Live Server (or another local web server) for the frontend.
Open index.html through that local server, not by double-clicking the file.

4) RESTOCK PRODUCTS
-------------------
Open admin.html through a local web server.
Enter:
- Backend URL: http://127.0.0.1:8000
- Admin key: the value you set in LW_ADMIN_KEY

Click Load products, change a stock number, and click Save.

5) WHAT HAPPENS WHEN A CUSTOMER ORDERS
--------------------------------------
The browser sends the cart to FastAPI.
FastAPI checks the latest database stock inside a transaction.
If enough stock exists, it records the order and decreases stock atomically.
If stock is not enough, the order is rejected and the customer sees the error.
Only after the database update succeeds does the site open WhatsApp.

6) IMPORTANT FOR GITHUB PAGES
-----------------------------
GitHub Pages can still host index.html, products.html, CSS, JS and images.
It CANNOT run FastAPI or SQLite.
You will deploy backend/ to a separate HTTPS Python host later.
Then change this line in script.js:

    const API_BASE_URL = "http://127.0.0.1:8000";

to your live HTTPS backend URL, for example:

    const API_BASE_URL = "https://your-backend.example.com";

Do not use an http:// backend from an https:// GitHub Pages site.

7) FILES TO COPY TO YOUR REAL FOLDER LATER
-------------------------------------------
You will NOT copy everything blindly.
I recommend copying:
- the new backend/ folder
- admin.html
- the updated script.js

Your existing index.html, products.html, style.css and images can stay as they are.

NOTE
----
The backend CORS setting currently allows all origins for easy testing.
When you deploy, restrict allow_origins to your real GitHub Pages URL.
