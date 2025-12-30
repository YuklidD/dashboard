import paramiko
import time
import sys

def simulate_attacker():
    print("Simulating attacker session...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("Connecting to honeypot...")
        client.connect('localhost', port=2222, username='root', password='password')
        channel = client.invoke_shell()
        
        commands = [
            "whoami",
            "ls -la",
            "cat /etc/passwd",
            "pwd",
            "echo 'Hello HaaS Dashboard!'",
            "exit"
        ]
        
        for cmd in commands:
            print(f"Sending command: {cmd}")
            channel.send(cmd + "\n")
            time.sleep(2) # Wait to let the user see the update in dashboard
            
            # Read output (just to clear buffer)
            if channel.recv_ready():
                channel.recv(1024)
                
        client.close()
        print("Simulation complete.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simulate_attacker()
