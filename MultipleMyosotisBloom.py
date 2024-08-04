import yt_dlp
import whisper
import re
import os
import json

# Function to download and convert YouTube video to MP3
def download_youtube_mp3(youtube_url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        audio_file_path = ydl.prepare_filename(info_dict).rsplit('.', 1)[0] + '.mp3'
        title = info_dict.get('title', 'unknown_title')
        return audio_file_path, title

# Function to transcribe audio using Whisper
def transcribe_audio(file_path):
    # Load the Whisper model
    model = whisper.load_model("medium")
    
    # Transcribe the audio file with English as the default language
    result = model.transcribe(file_path, language="en")
    
    # Get the transcription segments
    segments = result["segments"]
    
    # Collect timestamps and text
    timestamped_text = [(segment['start'], segment['text']) for segment in segments]
    
    return timestamped_text

# Function to format the transcribed text with timestamps
def format_text(timestamped_text):
    formatted_lines = []
    for start, text in timestamped_text:
        # Format the timestamp
        minutes = int(start // 60)
        seconds = int(start % 60)
        timestamp = f"[{minutes:02}:{seconds:02}]"
        # Append the timestamp and the text
        formatted_lines.append(f"{timestamp} {text.strip()}")
    
    # Join the lines with a newline character
    formatted_text = '\n\n'.join(formatted_lines)
    
    return formatted_text

# Function to save text to a file
def save_to_file(text, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

# Function to save transcription to a JSON file
def save_to_json(transcriptions, json_path):
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        data = {}

    data.update(transcriptions)

    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Function to generate HTML file from text transcription
def generate_html_from_txt(txt_file_path, html_path, youtube_url):
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        formatted_transcription = file.read()

    title = os.path.splitext(os.path.basename(txt_file_path))[0]
    first_timestamp = re.search(r"\[\d{2}:\d{2}\]", formatted_transcription).group(0)
    formatted_transcription = formatted_transcription.replace(first_timestamp, f'<a href="{youtube_url}">{first_timestamp}</a>', 1)

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
  <h2 class="header">{title}</h2>
  <pre class="transcript">{formatted_transcription}</pre>
</body>
</html>'''

    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

# Function to update Myosotis.html with a new card entry
def update_myosotis_html(title, transcription_html_path, myosotis_html_path="Myosotis.html"):
    card_template = f'''
    <a href="{transcription_html_path}" class="card-link">
      <article class="carded">
        <div class="text">
          <p>{title}</p>
        </div>
      </article>
    </a>
    '''

    if not os.path.exists(myosotis_html_path):
        # Create the file with initial content if it doesn't exist
        with open(myosotis_html_path, 'w', encoding='utf-8') as file:
            file.write('''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Myosotis</title>
  <link rel="stylesheet" type="text/css" href="/text_transcripts/style.css">
</head>
<body>
 <h1 class="title-page">Myosotis</h1>
 <div class="cardsss">
 </div>
</body>
</html>''')

    with open(myosotis_html_path, 'r+', encoding='utf-8') as file:
        content = file.read()
        # Insert the new card at the beginning of the cardsss section
        updated_content = content.replace('<div class="cardsss">', f'<div class="cardsss">{card_template}')
        # Write the updated content back to the file
        file.seek(0)
        file.write(updated_content)
        file.truncate()

if __name__ == "__main__":
    # Ask the user for the YouTube URLs and output path
    youtube_urls = input("Please enter the YouTube URLs separated by commas: ").split(',')
    output_path = "."

    # Process each URL
    for youtube_url in youtube_urls:
        youtube_url = youtube_url.strip()
        
        # Download and convert YouTube video to MP3
        audio_file_path, title = download_youtube_mp3(youtube_url, output_path)
        
        # Perform transcription
        timestamped_transcription = transcribe_audio(audio_file_path)
        
        # Format the transcription text with timestamps
        formatted_transcription = format_text(timestamped_transcription)
        
        # Define the path for the output text file
        transcripts_dir = os.path.join(output_path, "text_transcripts")
        os.makedirs(transcripts_dir, exist_ok=True)
        output_file_path = os.path.join(transcripts_dir, os.path.splitext(os.path.basename(audio_file_path))[0] + "_transcription.txt")
        
        # Save the formatted transcription to a file
        save_to_file(formatted_transcription, output_file_path)
        
        # Save the transcription to a JSON file
        json_file_path = os.path.join(output_path, "transcriptions.json")
        transcription_data = {
            title: {
                "url": youtube_url,
                "transcription": formatted_transcription
            }
        }
        save_to_json(transcription_data, json_file_path)
        
        # Delete the MP3 file
        os.remove(audio_file_path)
        
        # Print the location of the saved transcription
        print("Transcription saved to:", output_file_path)
        print("Transcription also stored in:", json_file_path)
        
        # Generate HTML file from text transcription
        html_file_path = os.path.splitext(output_file_path)[0] + ".html"
        generate_html_from_txt(output_file_path, html_file_path, youtube_url)
        
        # Print the location of the generated HTML file
        print("HTML file generated at:", html_file_path)

        # Update Myosotis.html with a new card entry
        update_myosotis_html(title, os.path.relpath(html_file_path, output_path))

        # Print the location of the updated Myosotis.html file
        print("Myosotis.html updated with a new entry.")
