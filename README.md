# Sanitization Server

LMS needs to load data from various sources.
This server cleans that data and loads them in a specific format.

### Usage

1.  Run the python server

        python3 server.py

### <b>/upload</b>

Send a Post request here with the file as multipart/form

<b>Required Params:</b>

- source : Can be "cd"(college duniya), "sk"(siksha), "x"(custom)
- file : The file
