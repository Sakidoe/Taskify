# Taskify: All-in-one Task Management App

## Intro
Welcome to Taskify! A project that is an all-in-one task management web application, including a task manager, calendar, and teams app. Users create accounts through Dex or Google OAuth, and data is kept through Docker and MongoDB. 

[Initial Github with Commit History](https://github.com/Sakidoe/ECS162-Final-Project) 

## Usage
- To build the project, have Docker open and installed through VSCode and running on your local device.
- Create a `.env` file, and a `.env.dev` file,  and copy `.env.example` to the two new files. Correct the parameters of account details as needed.
- run `docker-compose -f docker-compose_dev.yml up --build`

## Testing
Create an account, or utilize the following credentials to login:
email: admin@hw3.com	password: password

Local Dev frontend will be on http://localhost:5173/, with backend on http://localhost:8000/

