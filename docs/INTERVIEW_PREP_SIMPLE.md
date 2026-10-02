# QueueSense — Interview Guide (Simple Version)

This is your easy-to-read guide. Short sentences. Simple words. Use this to
prepare for your interview.

---

## 1. One-Line Pitch

"QueueSense predicts hospital wait times using machine learning. Patients
get a live token. Staff manage the queue in real time."

## 2. What Is This Project?

It is a hospital queue system. Patients register and get a wait-time
estimate. Staff can see the queue and manage it. The wait time is predicted
by a trained ML model.

## 3. Why Did I Choose This Project?

- Everyone understands hospital waiting. It is easy to explain.
- It uses many skills at once: frontend, backend, ML, login system, and
  deployment.
- It solves a real problem, not a fake one.

## 4. Real-Life Example

A patient walks into a clinic. They register with their name and phone
number. The system checks the queue size and how many doctors are free. It
predicts a wait time, like 40 minutes. The patient can check this on their
phone. Staff can call the next patient, mark them done, or turn a doctor on
or off duty. The wait time updates for everyone else right away.

---

## 5. My Role in This Project

I built the whole project by myself. I did every part:

- **Frontend**: I built the website. Patients use it to register and check
  their wait time. Staff use it to manage the queue.
- **Backend**: I built the API using FastAPI. It handles patients, doctors,
  login, and predictions.
- **Machine Learning**: I built and trained the model. I compared 3 models
  and picked the best one.
- **Login System**: I built real login with passwords and tokens (JWT).
- **Real-Time Updates**: I used WebSocket so the queue updates live.
- **Deployment**: I used Docker so the app can run anywhere.

**Simple way to say it:** "I was the only developer. I built the frontend,
backend, ML model, login system, and deployment, all by myself."

---

## 6. Tech Stack (Simple Table)

| Part | Tool | Why |
|---|---|---|
| Frontend | HTML, CSS, JavaScript | Simple, no extra setup needed |
| Backend | FastAPI (Python) | Fast, easy to use, auto-creates API docs |
| ML Model | scikit-learn | Easy to train and test models |
| Login | JWT + password hashing | Safe way to log in users |
| Real-time | WebSocket | Sends live updates to the browser |
| Deployment | Docker | Runs the same way on any computer |

---

## 7. Interview Questions and Simple Answers

### Basic Questions

**Q: What does your project do?**
A: It predicts how long a patient will wait at a hospital. It uses a
machine learning model.

**Q: Why did you build this?**
A: Hospital waiting is a real problem. I wanted to solve it and also
practice full-stack and ML skills together.

**Q: What is your role?**
A: I am the only developer. I built everything — frontend, backend, ML
model, login, and deployment.

**Q: How long did it take?**
A: I built it step by step, day by day, adding one feature at a time.

**Q: Is this a real hospital system?**
A: No. It is a working prototype. It shows how a real system could work.
It is not connected to a real hospital yet.

---

### Machine Learning Questions

**Q: What model did you use?**
A: Gradient Boosting Regressor. It is a tree-based model.

**Q: Why this model?**
A: I tested 3 models: Linear Regression, Random Forest, and Gradient
Boosting. Gradient Boosting had the lowest error.

**Q: What features does the model use?**
A: Queue size, number of doctors, appointment type, time of day, day of
week, and if it is an emergency.

**Q: How accurate is your model?**
A: It is off by about 9 minutes on average. That is a good result for this
kind of data.

**Q: Is your data real?**
A: No. I made synthetic (fake but realistic) data. Real hospital data is
private and hard to get.

**Q: What is R² score?**
A: It tells how well the model explains the data. My model has an R² of
0.92. That means it explains 92% of the pattern in the data.

**Q: Why not use deep learning?**
A: My data is small and simple. Deep learning needs much more data. Simple
models work better here.

**Q: What is overfitting?**
A: It means the model learns the training data too well, but fails on new
data. I used a train/test split to check for this.

**Q: How did you test your model?**
A: I split the data into 80% for training and 20% for testing. I checked
the error on the test part.

---

### Backend Questions

**Q: Why did you use FastAPI?**
A: It is fast. It checks data automatically. It creates API docs by
itself.

**Q: How does your login system work?**
A: I hash passwords so they are never stored in plain text. When a user
logs in, I give them a token (JWT). This token proves they are logged in.

**Q: What is JWT?**
A: It stands for JSON Web Token. It is a safe way to check if a user is
logged in, without storing sessions on the server.

**Q: How do you protect staff-only actions?**
A: I check for a valid token before letting someone update the queue or
doctors.

**Q: What database do you use?**
A: Right now, I use in-memory storage. This means data resets when the
server restarts. In a real system, I would use PostgreSQL.

**Q: How would you scale this for many hospitals?**
A: I would use a real database. I would add a hospital ID to every record.
I would also use a message system like Redis for real-time updates.

---

### Frontend Questions

**Q: Why no React or Vue?**
A: My project is small. Plain HTML, CSS, and JavaScript were enough. No
extra setup was needed.

**Q: How did you make it responsive?**
A: I used CSS Grid and Flexbox. I also added breakpoints for small
screens.

**Q: How does real-time update work on the frontend?**
A: The frontend connects to the backend using WebSocket. The server sends
updates every 2 seconds.

---

### Deployment Questions

**Q: How do you deploy this project?**
A: I use Docker. One container runs the backend. Another runs the
frontend. Docker Compose runs both together.

**Q: Where can this be hosted?**
A: The backend can go on Render. The frontend can go on Netlify.

**Q: Why two different hosting services?**
A: Netlify only hosts static files. It cannot run a Python server. Render
can run the backend server. So I split them.

---

### Problem-Solving Questions (Very Important)

**Q: Tell me about a bug you fixed.**
A: My model sometimes predicted negative wait times. That is not possible
in real life. I fixed it by limiting the output between 2 and 180 minutes.

**Q: Tell me about another bug.**
A: My trained model file would not load on a different computer. This
happened because of a library version mismatch. I fixed it by rebuilding
the model inside Docker, every time, using the exact library versions
installed there.

**Q: What was the hardest part of this project?**
A: Making the fake training data realistic. At first, my wait times were
too high, even more than 20 hours. I fixed the data logic to make it more
realistic.

**Q: How do you debug problems?**
A: I check error messages carefully. I test small parts of the code
separately. I use print statements or test scripts to check if functions
work correctly.

---

### Behavioral Questions

**Q: What did you learn from this project?**
A: I learned that building an ML system is not just about the model. It is
also about good data, good testing, and a working system around the
model.

**Q: What would you improve next?**
A: I would add a real database, write automated tests, and support
multiple hospitals.

**Q: What are the limits of your project?**
A: It uses fake data. It uses in-memory storage. It only supports one
queue right now. I know these limits and I am ready to fix them.

**Q: Why should we hire you based on this project?**
A: I can build a full system alone. I can find and fix real bugs. I
understand both the ML side and the software side of a project.

---

## 8. Quick Facts to Remember

- Model used: Gradient Boosting
- Models compared: 3
- Average error: about 9 minutes
- R² score: 0.92
- Login: JWT + password hashing
- Real-time: WebSocket, updates every 2 seconds
- Deployment: Docker, Render, Netlify
