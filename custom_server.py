import socket
from threading import Thread
import os
import argparse

ERROR: str = "404 Not Found\r\n\r\n"
HOST = "localhost"
PORT = 4221


def main() -> None:
    parser = argparse.ArgumentParser(description="Server that handles requests.")
    parser.add_argument(
        "--directory",
        type=str,
        help="The directory to check",
        default=".",
        required=False,
    )
    # Parse the command-line arguments:
    cli_args = parser.parse_args()

    # Create a TCP/IP server socket (endpoint), bind it to a specified host and port, then put it into listening mode:
    with socket.create_server((HOST, PORT),) as server:  # create the server socket "within" a context manager. note: Windows doesn't support process port-sharing (can't set reuse_port=True)
        print(f"Server listening on {HOST}:{PORT}\n")

        while True:  # keep listening...
            # Accept and establish a connection:
            connection, address = server.accept()  # blocking call; continuously waits (hangs) until a client connects
            # Each client's connection reruns this entire script, hence, it also instantiates a new, separate thread per connection!
            Thread(target=handle_connection, args=(connection, address, cli_args)).start()


def handle_connection(connection: socket, address: tuple, args: argparse.Namespace) -> None:
    with connection:
        print(f"Connected by {address}\n")  # client's IP address and port

        # Receive an HTTP http_request:
        http_request = connection.recv(1024).decode("utf-8")  # blocking call; waits for up to 1024 bytes of data to arrive (be transmitted) over the network (I/O-bound operation)
        print(f"Incoming HTTP http_request:\n{http_request}")

        request_components = http_request.strip("\r\n").split("\r\n")
        request_line = request_components[0]
        request_headers = request_components[1:-1]
        request_body = request_components[-1]
        print(f"Request Body:\n{request_body}")
        http_method, requested_url, http_version = request_line.split(" ")

        file_name = requested_url.removeprefix("/files/")

        http_response: bytes
        if http_method == "GET":
            if requested_url == "/":
                print("Client requested index page")
                # Our response must be a "byte string" (binary format) rather than a regular python string such that it's correctly interpreted by other systems
                http_response = response_template()

            elif requested_url.startswith("/echo"):
                path = requested_url.removeprefix("/echo/")
                http_response = response_template(content=path)

            elif requested_url.startswith("/user-agent"):
                for header in request_headers:
                    if header.startswith("User-Agent:"):
                        user_agent = header.split(" ")[-1]
                        break
                http_response = response_template(content=user_agent)

            elif requested_url.startswith("/files"):
                path = os.path.join(args.directory, file_name)

                if os.path.isfile(path):
                    print(f"File found at: {path}")

                    with open(path, "r") as file:
                        http_response = response_template(content_type="application/octet-stream", content=file.read())

                else:
                    print("File not found!")
                    http_response = response_template(status=ERROR)

            else:
                print("Client requested some other page")
                http_response = response_template(status=ERROR)

        else:  # if POST...
            with open(os.path.join(args.directory, file_name), "w") as file:
                file.write(request_body)
                http_response = response_template(status="201 Created")

        connection.sendall(http_response)  # blocking call; waits for the network to transmit data to the client


def response_template(status: str = "200 OK", content_type: str = "text/plain", content: str | None = None) -> bytes:
    if content:
        return f"HTTP/1.1 {status}\r\nContent-Type: {content_type}\r\nContent-Length: {len(content)}\r\n\r\n{content}".encode("utf-8")

    return f"HTTP/1.1 {status}\r\n\r\n".encode("utf-8")


if __name__ == "__main__":
    main()
