from langchain_community.llms import Ollama
import os
os.environ['NO_PROXY']='localhost,127.0.0.1'
class HealthAgent:
    def __init__(self):
        # Ensure you have 'ollama run llama3' installed on your PC
        self.model = Ollama(model="llama3")

    def verify_and_act(self, role, task, context):
        prompt = f"""
        System: You are a Medical Security Agent.
        User Role: {role}
        Task: {task}
        Context: {context}
        
        Decision: Should the user access the decrypted medical images/reports? 
        If yes, explain why based on medical necessity. If no, explain the privacy breach.
        """
        return self.model.invoke(prompt)