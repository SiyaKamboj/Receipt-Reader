This app uses an OCR API to scan uploaded receipts, itemize the products purchased on the screen, and let users pick what they consumed and automatically split the cost between everyone. It’s built with Python and Flask on the backend, using SQLAlchemy for handling the database, and React for the frontend. I’m also currently integrating the Zelle API, so users can send payment requests right from the app, but if that doesn’t happen, I am going to allow users to send the requested amounts directly to other users.