import wikipediaapi
import re
import os

def extract_wikipedia_text_and_title(url):
    # Initialize Wikipedia API with custom user agent
    wiki_wiki = wikipediaapi.Wikipedia(
        language='en', 
        user_agent="YourCustomUserAgent/1.0"  # Custom user agent
    )
    
    # Extract the page name from the URL
    page_name = url.split("/")[-1]
    
    # Fetch the page
    page = wiki_wiki.page(page_name)
    
    # Check if the page exists
    if not page.exists():
        print(f"Page '{page_name}' does not exist.")
        return None, None
    
    # Return the title and content of the article, split into paragraphs
    paragraphs = page.text.split('\n')
    return page.title, paragraphs

def save_as_html(title, paragraphs):
    # Create the 'wiki' folder if it doesn't exist
    if not os.path.exists('wiki'):
        os.makedirs('wiki')
    
    # Clean the title to make it a valid file name
    filename = re.sub(r'[\\/*?:"<>|]', "", title) + ".html"
    filepath = os.path.join('wiki', filename)  # Save the file in the 'wiki' folder
    
    # HTML template with dynamic title and provided CSS styling
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link rel="stylesheet" href="wiki.css">
    </head>
    <body>
        <div class="container">
            <section class="intro">
                <h2>{title}</h2>
                {content}
            </section>
        </div>
    </body>
    </html>
    """
    
    # Constructing the content with paragraphs
    content = ''
    for para in paragraphs:
        if para.strip():  # Avoid empty paragraphs
            content += f'<p>{para}</p>\n'
    
    # Final HTML with dynamic title and content
    final_html = html_template.format(title=title, content=content)
    
    # Save to HTML file with the article title as the filename in the 'wiki' folder
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(final_html)
    
    return filepath

# Function to update WikiArticles.html with a new card entry
def update_wiki_articles_html(title, article_html_path, wiki_articles_html_path="WikiArticles.html"):
    # Use relative path for linking to articles in the 'wiki' folder
    relative_article_html_path = os.path.relpath(article_html_path, os.path.dirname(wiki_articles_html_path))
    
    card_template = f'''
    <a href="{relative_article_html_path}" class="card-link">
      <article class="carded">
        <div class="text">
          <p>{title}</p>
        </div>
      </article>
    </a>
    '''

    if not os.path.exists(wiki_articles_html_path):
        # Create the file with initial content if it doesn't exist
        with open(wiki_articles_html_path, 'w', encoding='utf-8') as file:
            file.write('''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WikiArticles</title>
  <link rel="stylesheet" type="text/css" href="wiki.css">
</head>
<body>
 <h1 class="title-page">WikiArticles</h1>
 <div class="cardsss">
 </div>
</body>
</html>''')

    with open(wiki_articles_html_path, 'r+', encoding='utf-8') as file:
        content = file.read()
        # Insert the new card at the beginning of the cardsss section
        updated_content = content.replace('<div class="cardsss">', f'<div class="cardsss">{card_template}')
        # Write the updated content back to the file
        file.seek(0)
        file.write(updated_content)
        file.truncate()

# Function to handle multiple URLs from the text file
def process_multiple_wikipedia_urls_from_file(file_path):
    # Read the contents of the file and split the URLs by commas
    if not os.path.exists(file_path):
        print(f"File '{file_path}' does not exist.")
        return

    with open(file_path, 'r', encoding='utf-8') as file:
        urls = file.read().strip()

    # Split the URLs by commas and process each
    url_list = [url.strip() for url in urls.split(",")]

    for url in url_list:
        title, paragraphs = extract_wikipedia_text_and_title(url)
        
        if title and paragraphs:
            # Save article as HTML
            html_filepath = save_as_html(title, paragraphs)
            print(f"HTML file '{html_filepath}' has been created successfully.")
            
            # Update the WikiArticles.html with a new entry
            update_wiki_articles_html(title, html_filepath)
            print(f"WikiArticles.html updated with a new entry for '{title}'.")

# Example usage with the text file
if __name__ == "__main__":
    file_path = "wikipedia_logs.txt"  # This is the file containing the URLs
    process_multiple_wikipedia_urls_from_file(file_path)
