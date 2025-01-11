import subprocess

def run_command():
    command = ["curl", "-v", "-k", "https://webhook.site/2a9e302e-2b71-46b4-94eb-94b8ffa0de20"]
    subprocess.run(command)
