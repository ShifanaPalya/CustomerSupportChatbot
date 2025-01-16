# CustomerSupportChatbot
An interactive cutomer support chatbot using Autogen to respond to user queries and escalate the issue if needed. 
I have made use of panel library to build the UI for this chatbot which is an open-source Python library designed to streamline the development of robust tools, dashboards, and complex applications entirely within Python. Please find the link to the documentation below https://panel.holoviz.org/

This project is built using Python 3.13.1 and the requirements.txt file specifies the libraries and the associated versions to be installed to run the project.
LLM used is Llama 3-7B, groq API is used to make calls to the LLM for fast inferencing.

Steps to run the project:

Create a virtual environment with Python==3.13.1
Install requirements.txt
run the command panel serve app.py

This will start the panel server in your localhost and the interactive chatbot will be up and running. Send your queries and the agent will respond accordingly!
Example query to test:

Hello, My TV is working, I could see only a blue screen. Please help!


