try:
    # Python 3
    import html
except ImportError:
    # Python 2
    from HTMLParser import HTMLParser
    html = HTMLParser()
    html.unescape = html.unescape  # Make it work like Python 3's html.unescape
    html.escape = lambda s, quote=True: (s.replace("&", "&amp;")
                                        .replace('"', "&quot;" if quote else '"')
                                        .replace("'", "&#x27;")
                                        .replace(">", "&gt;")
                                        .replace("<", "&lt;"))

import argparse
import xml.dom.minidom
import re
import logging

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def format_input(input_str):
    """
    Format and beautify XML input string.
    
    Args:
        input_str: Input XML string to format
        
    Returns:
        tuple: Tuple containing (escaped_output, formatted_output)
    """
    logger.info("Starting XML formatting process...")
    
    # Step 1: Decode HTML entities to get the original XML string
    logger.debug("Decoding HTML entities...")
    decoded_str = html.unescape(input_str)
    
    # Step 2: Unescape Java-style escape sequences (\n, \", etc.)
    logger.debug("Processing escape sequences...")
    decoded_str = decoded_str.replace("\\n", "\n").replace('\\"', '"')
    
    # Step 3: Beautify XML for better readability
    try:
        logger.debug("Beautifying XML...")
        dom = xml.dom.minidom.parseString(decoded_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        logger.info("XML beautification successful!")
    except Exception as e:
        logger.error("Error formatting XML: %s" % str(e))
        pretty_xml = "Error formatting XML: %s" % str(e)
    
    # Step 4: Escape the XML for output
    logger.debug("Escaping XML for output...")
    escaped_str = html.escape(decoded_str)
    
    logger.info("XML formatting completed successfully!")
    return escaped_str, pretty_xml

def main():
    logger.info("Starting XML Formatter...")
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Deserializes and formats the input string")
    parser.add_argument("input_str", nargs='?', type=str, help="The input string to process")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # If input is not provided as an argument, prompt the user for input
    if not args.input_str:
        logger.info("Waiting for user input...")
        try:
            # Python 2
            args.input_str = raw_input("Please enter the string to format: ")
        except NameError:
            # Python 3
            args.input_str = input("Please enter the string to format: ")
    
    # Format the input
    escaped_output, formatted_output = format_input(args.input_str)
    
    # Print the escaped output and formatted output
    print("\nFormatted Output:")
    print(formatted_output)
    
    logger.info("XML Formatter completed successfully!")

if __name__ == "__main__":
    main()
