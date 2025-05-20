import subprocess
import platform

def ping(host):
    # Determine the ping command based on the operating system
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    
    # Build the ping command (4 pings)
    command = ['ping', param, '1', host]
    
    try:
        # Execute the ping command and capture output
        output = subprocess.run(command, capture_output=True, text=True)
        print(output.stdout)
        
        # Check if the ping was successful
        if output.returncode == 0:
            # print(f"Ping to {host} was successful!")
            pass
        else:
            # print(f"Ping to {host} failed!")
            pass
            
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Ping 8.8.8.8
if __name__ == "__main__":
    ping("8.8.8.8")