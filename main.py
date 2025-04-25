import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os

from collections import OrderedDict, Counter
def extract_text_per_chapter(epub_path):
    """
    Extracts text content from each document item (chapter/section) in an EPUB file.

    Args:
        epub_path (str): The path to the EPUB file.

    Returns:
        OrderedDict or None: An OrderedDict where keys are item names/ids
                             and values are the extracted text for that item,
                             or None if an error occurs.
    """
    chapter_texts = OrderedDict() # Use OrderedDict to keep items in order

    try:
        book = epub.read_epub(epub_path)

        for item in book.get_items():
            # We are interested in document items (usually HTML files containing text)
            if item.get_type() == ebooklib.ITEM_DOCUMENT:

                item_name = item.get_name() 

                if "chapter" in item_name[:7].lower():

                    content = item.get_content()

                    html_content = content.decode('utf-8')

                    # Use BeautifulSoup to parse the HTML content
                    # 'lxml' parser is generally fast and robust
                    soup = BeautifulSoup(html_content, 'lxml')


                    # separator='\n' adds a newline between elements,
                    # strip=True removes leading/trailing whitespace.
                    text = soup.get_text(separator = " ", strip=True)

                    # Store the extracted text with the item name as the key
                    chapter_texts[item_name] = text

    except FileNotFoundError:
        print(f"Error: EPUB file not found at '{epub_path}'")
        return None
    except Exception as e:
        print(f"Error processing EPUB file: {e}")
        return None

    return chapter_texts

import re
import string

def tokenize_text(text):
    """
    Tokenizes text into words, removing punctuation and converting to lowercase.

    Args:
        text (str): The input text content.

    Returns:
        list: A list of words extracted from the text.
    """
    if not text:
        return []
    
    text = text.translate(str.maketrans('', '', string.punctuation))

    text = text.lower()

    # Split text into words using regular expression to handle various whitespace
    # \s+ matches one or more whitespace characters (space, tab, newline, etc.)
    words = re.split(r'\s+', text)

    words = [word for word in words if word]
    return words

if __name__ == "__main__":
    # Example usage
    epub_path = 'Books/Harry_Potter_i_Wiezien_Azkabanu.epub'
    chapter_texts = extract_text_per_chapter(epub_path)

    if chapter_texts:
        print(f"Text extraction successful. Found {len(chapter_texts)} document items (potential chapters/sections).")

        chapter_word_counts = {}

        all_book_words = []

        # Process each chapter's text
        for item_name, text in chapter_texts.items():
            print(f"\n--- Processing Item: {item_name} ---")

            # Tokenize the text for the current chapter
            chapter_words = tokenize_text(text)
            print(f"  Extracted {len(chapter_words)} words from this item.")

            # Count word frequencies for the current chapter
            chapter_word_counts[item_name] = Counter(chapter_words)

            # Add the chapter's words to the list for the whole book
            all_book_words.extend(chapter_words)

        # Calculate word frequencies for the entire book
        total_book_word_counts = Counter(all_book_words)

        print("\n--- Overall Book Word Counts ---")
        print(f"Total unique words in the book: {len(total_book_word_counts)}")
        print("Most common words in the entire book:")

        # Print the most common words for the entire book (e.g., top 20)
        for word, count in total_book_word_counts.most_common(20):
            print(f"  '{word}': {count}")

    else:
        print("No text content was extracted from the EPUB file.")