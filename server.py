from flask import Flask, request
import os
import subprocess

app = Flask(__name__)

# Helper function to check if the URL is from YouTube or Wikipedia
def is_youtube_url(url):
    return url.startswith("https://www.youtube.com/")

def is_wikipedia_url(url):
    return url.startswith("https://en.wikipedia.org/") or url.startswith("https://fr.wikipedia.org/")

# Function to strip URL after '?' if it exists
def strip_url_query(url):
    if '?' in url:
        url = url.split('?')[0]
    return url

# Function to automatically commit and push changes to GitHub
def commit_and_push_to_github(commit_message):
    try:
        # Stage all changes
        subprocess.run(['git', 'add', '.'], check=True)
        print("Files staged for commit.")

        # Commit the changes with a message
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        print(f"Changes committed with message: {commit_message}")

        # Push the changes to the remote repository (adjust 'origin' and 'main' as needed)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("Changes pushed to GitHub successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")
        return f"Error during Git operations: {e}", 500

@app.route('/process_url', methods=['POST'])
def process_url():
    url = request.form['url']
    print(f"Original URL received: {url}")

    # Strip query parameters if present
    url = strip_url_query(url)
    print(f"Processed URL (without query parameters): {url}")

    # Check if the URL is from YouTube or Wikipedia
    if is_youtube_url(url):
        log_file_path = "youtube_logs.txt"
    elif is_wikipedia_url(url):
        log_file_path = "wikipedia_logs.txt"
    else:
        # If the URL is not valid, return a 400 Bad Request
        return "Invalid URL: Only YouTube and Wikipedia URLs are allowed", 400

    # Check if the log file exists and has content
    file_exists = os.path.exists(log_file_path)
    
    # Read the file contents to check if it's non-empty
    if file_exists:
        with open(log_file_path, "r") as log_file:
            contents = log_file.read().strip()  # Strip any trailing whitespace or newlines
    else:
        contents = ""
    
    # Open the respective log file in append mode
    with open(log_file_path, "a") as log_file:
        if contents:
            # If the file already has content, append a comma before the new URL
            log_file.write(f",{url}")
        else:
            # If the file is empty, write the first URL without a leading comma
            log_file.write(f"{url}")

    # Run wikiGetter.py at the end of the process
    try:
        result = subprocess.run(['python', 'wikiGetter.py'], check=True)  # You can adjust this based on your environment
        print("wikiGetter.py executed successfully!")

        # If execution was successful, clear the wikipedia_logs.txt file
        if log_file_path == "wikipedia_logs.txt":
            with open(log_file_path, "w") as log_file:
                log_file.write("")  # Clear the file content
            print("wikipedia_logs.txt cleared.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running wikiGetter.py: {e}")
        return f"Error running wikiGetter.py: {e}", 500

    # Automatically commit and push the changes to GitHub
    commit_message = f"Processed URL: {url}"
    commit_result = commit_and_push_to_github(commit_message)

    # Return success message if everything worked
    return f"URL {url} received, saved, wikiGetter.py executed, and changes pushed to GitHub!"

if __name__ == '__main__':
    app.run(debug=True)
