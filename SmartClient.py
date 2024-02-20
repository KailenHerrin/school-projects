import socket
import ssl
import sys
import re

RESPONSE_SIZE = 1000000
ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

# Create a context to use later
context = ssl.create_default_context()
context.set_alpn_protocols(['http/1.1', 'h2']) 

# Function Declarations

# Take a uri, and a port as arguments then print a message stating if the website supports http2
def print_http2(uri, port):
    # Check if website supports HTTP2
    server = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=uri)
    server.connect((uri, port))
    foo = [server.selected_alpn_protocol()]
    if 'h2' in foo:
        print("1. Supports http2: yes")
    else:
        print("1. Supports http2: no")

# Given a uri get an HTTP response from an http server
def get_response_http(uri, path): 
    # Create socket
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((uri, 80))
    except:
        print("Oops! Invalid address please try again")
        sys.exit()

    # Send Request
    request = "GET " + path + " HTTP/1.1\r\nHost:" + uri + " \r\n\r\n"
    server.sendall(request.encode())

    # Get HTTP response and close server
    http_response = server.recv(RESPONSE_SIZE).decode()
    server.close()

    # Return response
    return http_response

# Given a uri get an HTTP response from an https server
def get_response_https(uri, path):
    # Create and wrap socket
    try:
        server = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=uri)
        server.connect((uri, 443))
    except:
        print("Oops! Invalid address please try again")
        sys.exit()

    # Send Request
    request = "GET " + path + " HTTP/1.1\r\nHost:" + uri + " \r\n\r\n" # / is not always the right thing.. ex /docs
    server.sendall(request.encode())

    # Get HTTP response and close server
    http_response = server.recv(RESPONSE_SIZE).decode()
    server.close()

    # Return response
    return http_response

# Prints a list of cookies when given some output from a server
def print_cookies(server_output):
    cookies = re.findall(r"Set-Cookie: .*", server_output)

    print("2. List of Cookies:")
    for cookie in cookies:
        print("cookie name: " + cookie[12:])

# Prints if a server is password-protected when given some output from a server
def print_password_protected(server_output):
    
    if "HTTP/1.1 401" in server_output:
        print("3. Password-protected: yes")
    else:
        print("3. Password-protected: no")

# Takes a URI string as input and extracts any use extra information out of it
# Returns 3 values, a bool value indicating if the website is secure
# a url
# a file path
def parse_uri(uri):
    new_secure = False
    new_file_path = "/"
    if "https://" in uri:
        new_secure = True
        uri = uri[7+1:]
    elif "http://" in uri:
        uri = uri[6+1:]

    path_start = uri.find("/")

    if path_start != -1:
        new_file_path = uri[path_start:]
        uri = uri[:path_start] 
    
    return new_secure, uri, new_file_path

# Main
def main():
    
    # Take initial URI from stdin
    next_uri = str(sys.argv[1])

    # Parse the input string
    secure, next_uri, file_path = parse_uri(next_uri)

    # Follow redirects and handle errors
    while True:
        # Try and get a response using http or https
        if secure is False:
            response = get_response_http(next_uri, file_path)
        else:
            response = get_response_https(next_uri, file_path)

        # Check if this is the final destination, if so break
        if ("HTTP/1.1 301" not in response and "HTTP/1.1 302" not in response and 
            "HTTP/1.0 301" not in response and "HTTP/1.0 302" not in response):
            break

        # Handle redirect
        loc = re.findall(r"Location: .*", response) # Get new location
        temp_addr = loc[0][10:]
        
        while temp_addr[-1] not in ALPHABET:
            temp_addr = temp_addr[:len(temp_addr)-1]
        
        secure, next_uri, file_path = parse_uri(temp_addr)

    # Check what the response is in case 404 or 505
    if "HTTP/1.1 404" in response:
        print("Oops! The page you requested is not available")
    elif "HTTP/1.1 505" in response:
        print("Oops! HTTP version not supported")
    else:
        # Print output
        print_http2(next_uri, 443)
        print_cookies(response)
        print_password_protected(response)
    
if __name__ == "__main__":
    main()