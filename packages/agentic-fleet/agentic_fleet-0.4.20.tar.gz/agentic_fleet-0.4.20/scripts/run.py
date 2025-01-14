import os
import subprocess

def main():
    script_path = os.path.join(os.path.dirname(__file__), "run.sh")
    subprocess.run([script_path], check=True)

if __name__ == "__main__":
    main()