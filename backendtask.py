import http.server
import socketserver
import urllib.parse
import json

# defining the port we are using
PORT = 8000

# defining the path for the text file
TEXT_FILE_PATH = 'data.txt'

# defining all the required tags
BRANCH = {
    "A1": "chemical",
    "A2": "civil",
    "A3": "eee",
    "A4": "mechanical",
    "A5": "bpharm",
    "A6": "???",
    "A7": "cs",
    "A8": "eni",
    "AA": "ece",
    "AB": "manu",
    "B1": "bio",
    "B2": "chem",
    "B3": "eco",
    "B4": "math",
    "B5": "phy"
}

CAMPUS = {
    "P": "pilani",
    "G": "goa",
    "H": "hyderabad"
}

YEAR = {
    "1": "2024",
    "2": "2023",
    "3": "2022",
    "4": "2021",
    "5": "2020"
}

# defining our request handler
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # searching the url for the parameters
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        # checking if the path is /data and displaying accordingly
        if parsed_path.path == '/data':
            try:
                # reading the file and creating a list of ids
                with open(TEXT_FILE_PATH, 'r') as file:
                    ids = [line.strip() for line in file if line.strip()]
                # checking branch parameter
                branch = query_params.get('branch', [None])[0]
                
                # filtering based on requested branch
                if branch and branch.lower() in BRANCH.values():
                    branch_code = [k for k, v in BRANCH.items() if v == branch.lower()][0]
                    ids = [id_ for id_ in ids if branch_code in id_]
                
                # checking the year parameter
                year_code = query_params.get('year', [None])[0]

                # filtering based on requested year
                if year_code and year_code in YEAR:
                    year = YEAR[year_code]
                    ids = [id_ for id_ in ids if id_.startswith(year)]
                
                # checking for id parameter
                id = query_params.get('id', [None])[0]
                
                if id:
                    # displaying json with details
                    if id in ids:
                        # taking out the required components
                        year_code = id[:4]
                        branch_code = id[4:6]
                        uid = id[8:12]
                        campus_code = id[-1]
                        
                        # Generate email based on year, uid, and campus
                        email_prefix = f"{year_code}{uid}"
                        email_domain = CAMPUS.get(campus_code, "unknown") + ".bits-pilani.ac.in"
                        email = f"f{email_prefix}@{email_domain}"
                        
                        # Construct a detailed JSON response
                        detailed_info = {
                            "id": id,
                            "year": [k for k, v in YEAR.items() if v == year_code][0],  # Convert year to code
                            "branch": BRANCH.get(branch_code, "unknown"),
                            "campus": CAMPUS.get(campus_code, "unknown"),
                            "uid": uid,
                            "email": email
                        }
                        
                        # Send response with the detailed JSON object
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(detailed_info, indent=2).encode())
                    else:
                        # If the ID is not found, return a 404
                        self.send_error(404, "ID Not Found")
                    return
                # determine response format, displaying in text form only if specified
                response_format = query_params.get('format', ['json'])[0]
                
                if response_format == 'text':
                    # if text requested, displaying in that form
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write("\n".join(ids).encode())
                else:
                    # displaying with json as default
                    response_data = {"id": ids}
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data, indent=2).encode())
                

            except IOError:
                self.send_error(404, "File Not Found")
            
            
        else:
            # serve a 404 error for any other path
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")


# server set up
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
