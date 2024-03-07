#!/usr/bin/env python3

"""
This script provides functionalities for processing image files to extract text using Optical Character Recognition
(OCR), correcting the spelling of the extracted text, filtering out words based on similarity and frequency, and
managing file names based on the content of the images. It includes capabilities to rename files either to a hash value
or based on the most  significant words extracted from the images.

Usage:
The script is designed to be run from the command line with arguments specifying the target directory containing the
files to be processed, and optional flags to enable verbose or test modes.

Example Command:
`python script_name.py -d /path/to/directory -v -t`

Dependencies:
- NLTK: Used for natural language processing tasks, such as tokenization and frequency analysis.
- pytesseract: Utilized for extracting text from image files using OCR.
- spellchecker: Employed for spelling correction of the extracted text.
- Python-Levenshtein (or similar): Used for calculating similarity between words to filter out highly similar words.
- argparse, os, hashlib, string, time, textwrap, shutil: Standard Python libraries used for argument parsing, file and
  directory operations, hash generation, string manipulation, timing, and text formatting.

Note:
Ensure all external dependencies are installed, and necessary NLTK data (e.g., corpora, tokenizers) is downloaded
before running the script.  A script is included 'nltk-download.pu' which will download the necessary NLTK files once
the library is installed.

More information and current source code available at:
https://github.com/dwhagar/imageTools
"""

import os, hashlib, argparse, string, time, textwrap, shutil
import nltk, pytesseract
from PIL import Image
from spellchecker import SpellChecker
from difflib import SequenceMatcher

# Instantiate resources that we don't have to do more than once.
corpus_words = nltk.corpus.words.words()
brown_words = nltk.corpus.brown.words()
stemmer = nltk.stem.PorterStemmer()
spell = SpellChecker()

def correct_spelling(input_text, verbose=False, test=False):
    """
    Corrects the spelling of words in the input text and tags them with parts of speech.

    Parameters:
    - input_text (str): The text to be corrected.
    - verbose (bool): If True, prints detailed information about corrections.
    - test (bool): If True, runs in test mode without making permanent changes.

    Returns:
    - tuple: A tuple containing the corrected string and a list of tuples with words and their POS tags.
    """
    corrected_words = []

    # Tokenize the input string into words
    words = nltk.word_tokenize(input_text)

    # Tag words with parts of speech using NLTK
    tagged_words = nltk.pos_tag(words)

    for word, tag in tagged_words:
        # Preserve proper nouns as they are
        if tag in ['NNP', 'NNPS']:
            corrected_words.append(word)
            continue

        # Correct the spelling for words not recognized as proper nouns
        if word not in spell:
            corrected_word = spell.correction(word)

            if corrected_word is None:
                corrected_word = word

            if verbose or test:
                if not (word == corrected_word):
                    print(f"Corrected {word} to {corrected_word}.")
        else:
            # Word is spelled correctly; retain as is
            corrected_word = word

        corrected_words.append(corrected_word)

    corrected_string = ' '.join(corrected_words)
    return corrected_string

def filter_similar_words(words, similarity_threshold=0.80):
    """
    Filters out words that are at least similarity_threshold similar to each other.

    Parameters:
    words (list): A list of words to filter.
    similarity_threshold (float): The threshold for similarity (0 to 1), above which words are considered too similar.

    Returns:
    list: A filtered list of words with highly similar words removed.
    """
    filtered_words = []

    for word in words:
        stem_word = stemmer.stem(word)
        too_similar = False
        if len(word) >= 10 or word in filtered_words:
            too_similar = True
        else:
            for other_word in filtered_words:
                other_stem_word = stemmer.stem(other_word)

                if stem_word == other_stem_word:
                    too_similar = True
                else:
                    word_sim = SequenceMatcher(None, word, other_word).ratio()
                    stem_sim = SequenceMatcher(None, stem_word, other_stem_word).ratio()
                    if word_sim >= similarity_threshold or stem_sim >= similarity_threshold:
                        too_similar = True

        if not too_similar:
            filtered_words.append(word)

    return filtered_words

def sort_words_by_freq(words, freq_dist):
    """
    Sorts a list of words from least frequent to most frequent based on a given frequency distribution.

    Parameters:
    words (list): A list of words to sort.
    freq_dist (FreqDist): An NLTK FreqDist object containing the frequency distribution of words.

    Returns:
    list: The sorted list of words, from least frequent to most frequent.
    """
    # Sort words based on their frequency, using 0 for words not found in the frequency distribution
    sorted_words = sorted(words, key=lambda word: freq_dist.get(word, 0))

    return sorted_words

def generate_brown_freq_dist():
    """
    Generates and returns a frequency distribution object for words in the Brown Corpus.

    Returns:
    FreqDist: An NLTK FreqDist object containing the frequency distribution of words in the Brown Corpus.
    """
    # Calculate the frequency distribution of words
    freq_dist = nltk.probability.FreqDist(brown_words)

    return freq_dist

def get_terminal_width():
    """
    Returns the width of the terminal in characters.

    Returns:
    - int: The width of the terminal.
    """
    # Get terminal size using shutil
    terminal_size = shutil.get_terminal_size()
    return terminal_size.columns

def print_wrapped_text(text):
    """
    Prints the given text, wrapped according to the terminal width.

    Parameters:
    - text (str): The text to be printed.
    """
    # Wrap text to fit within the terminal width
    wrapped_text = textwrap.fill(text, width=get_terminal_width())
    print(wrapped_text)

def get_file_list(directory):
    """
    Returns two lists of files in the given directory: one for image files and another for non-image files.

    Parameters:
    - directory (str): The directory to scan for files.

    Returns:
    - tuple: A tuple containing two lists, one for image files and one for non-image files.
    """
    image_extensions = {'.gif', '.png', '.jpg', '.jpeg'}
    image_files = []
    non_image_files = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path):
            # Classify files based on their extensions
            if os.path.splitext(filename)[1].lower() in image_extensions:
                image_files.append(filename)
            else:
                non_image_files.append(filename)

    return image_files, non_image_files

def append_to_file(filename, text_to_append):
    """
    Appends a given text to the end of a specified file.

    Parameters:
    - filename (str): The name of the file to append the text to.
    - text_to_append (str): The text to append to the file.

    If the file cannot be opened for writing, the function will print an error message and return.
    """
    try:
        # Attempt to open the file in append mode and write the text
        with open(filename, 'a') as file:
            file.write(text_to_append)
            file.write('\n')  # Optionally add a newline after appending
    except Exception as e:
        # Print an error message if there's an issue opening the file
        print(f"An error occurred while trying to open or write to the file '{filename}': {e}")
        return

def process_image(image_file, directory, verbose=False, test=False, outfile=None):
    """
    Processes an image, extracts text using OCR, corrects spelling, and prioritizes proper nouns.

    Parameters:
    - image_path (str): The path to the image to be processed.
    - verbose (bool): If True, prints additional information.
    - test (bool): If True, runs in test mode without making permanent changes.

    Returns:
    - list: A list of words extracted and processed from the image.
    """
    # Preliminary checks for file existence and accessibility
    image_path = os.path.join(directory, image_file)

    if not os.path.exists(image_path) or os.path.getsize(image_path) == 0 or not os.access(image_path, os.R_OK | os.W_OK):
        print(f"File {image_file} cannot be processed.")
        return ""

    try:
        # Open the image and extract text using pytesseract
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image).replace('\n', ' ')
    except Exception as e:
        print(f"ERROR: Unexpected error processing image {image_file}: {e}")
        return ""

    if not text.strip():
        print(f"No text found in image: {image_file}")
        return ""

    if not test:
        append_to_file(outfile, text.strip())

    # Correct spelling and reorder text to prioritize proper nouns
    corrected_text = correct_spelling(text)
    corrected_text = corrected_text.split()

    brown_freq_dist = generate_brown_freq_dist()
    reordered_text = sort_words_by_freq(corrected_text, brown_freq_dist)

    if verbose or test:
        # Print the raw OCRed text in verbose or test mode
        print(f"Raw OCRed Text from {image_file}:")
        print_wrapped_text(text)
        print("")

    # Filter and process words based on criteria
    words = [word.lower().strip(string.punctuation) for word in reordered_text if word.isalpha() and len(word) >= 5]
    words = filter_similar_words(words)

    return words

def generate_md5(file_path):
    """
    Generates an MD5 hash for the contents of a given file.

    Parameters:
    - file_path (str): The path to the file.

    Returns:
    - str: The MD5 hash of the file's contents.
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def rename_file(file_info, directory, test_mode=False, verbose=False):
    """
    Renames a file according to the specified information, in test or verbose mode if requested.

    Parameters:
    - file_info (dict): Information about the file, including current and new names.
    - directory (str): The directory containing the file.
    - test_mode (bool): If True, does not actually rename the file (dry run).
    - verbose (bool): If True, prints detailed information about the renaming process.
    """
    original_path = os.path.join(directory, file_info['filename'])
    new_path = os.path.join(directory, file_info['rename'])

    if original_path == new_path:
        if verbose or test_mode:
            print(f"No need to rename '{file_info['filename']}', already done.")
            return

    if verbose or test_mode:
        print(f"Renaming '{file_info['filename']}' to '{os.path.basename(new_path)}'")

    if not test_mode:
        try:
            os.rename(original_path, new_path)
        except OSError as e:
            print(f"ERROR: Unable to rename '{original_path}' to '{new_path}'")
            print(f"ERROR: {e.errno} - {e.strerror}")

def main():
    """
    Main function to parse arguments, process files, and rename them based on OCR text or MD5 hashes.
    """
    start_time = time.time()

    parser = argparse.ArgumentParser(description="Modular OCR-based File Renamer with Verbose Option")
    parser.add_argument("-d", "--directory", required=True, help="Directory containing files to process")
    parser.add_argument("-t", "--test", action="store_true", help="Test mode: show intended actions without renaming")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode: print actions during renaming")
    parser.add_argument("-o", "--output_text", type=str, help="Output raw text from all scanned images to this file. The -t argument will override.")

    args = parser.parse_args()

    if not os.path.isdir(args.directory) or not os.access(args.directory, os.R_OK | os.W_OK):
        print("Directory does not exist or cannot be accessed.")
        return

    if args.output_text:
        # Check if the file does not exist or is not writable
        if not os.access(args.output_text, os.W_OK):
            print(f"Warning: The file '{args.output_text}' does not exist or is not writable.")
        else:
            if args.verbose or args.test:
                print(f"The file '{args.output_text}' is writable.")

        print(f"Initializing the file '{args.output_text}'.")
        with open(args.output_text, 'w') as file:
            pass

    # Get lists of image and non-image files
    image_list, not_image_list = get_file_list(args.directory)

    if args.verbose or args.test:
        print(f"Found {len(image_list)} image files and {len(not_image_list)} non-image files in '{args.directory}'.")

    file_infos = []

    # Process non-image files
    print("Planning rename of non-image files to MD5 hashes...")
    for filename in not_image_list:
        if filename[0] == '.':
            continue

        _, extension = os.path.splitext(filename)
        file_info = {
            'filename': filename,
            'words': "",
            'rename': generate_md5(os.path.join(args.directory, filename)) + extension
        }
        if args.verbose or args.test:
            print(f"Planning to rename {file_info['filename']} -> {file_info['rename']}.")

        file_infos.append(file_info)

    # Process image files for text, renaming those without sufficient text to MD5 hash
    print("Planning rename of image files, if no image text can be found images will be renamed to MD5 hash...")
    for filename in image_list:
        if filename[0] == '.':
            continue

        words = process_image(filename, args.directory, verbose=args.verbose, test=args.test, outfile=args.output_text)
        _, extension = os.path.splitext(filename)

        # Determine the rename value, ensuring to keep the original extension
        if not words or len(words) < 2:
            rename_value = generate_md5(os.path.join(args.directory, filename)) + extension
        else:
            rename_value = ' '.join(words[:5]) + extension

        file_info = {
            'filename': filename,
            'words': words,
            'rename': rename_value
        }
        file_infos.append(file_info)

        if args.verbose or args.test:
            print(f"Planning to rename {file_info['filename']} -> {file_info['rename']}.\n")

    # Rename files as necessary
    print("Renaming files where needed...")
    for file_info in file_infos:
        if file_info['rename']:
            rename_file(file_info, args.directory, test_mode=args.test, verbose=args.verbose)

    end_time = time.time()
    duration = end_time - start_time
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"Program completed in {int(hours):02}h:{int(minutes):02}m:{int(seconds):02}s.")

if __name__ == "__main__":
    main()
