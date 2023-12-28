from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import urllib.parse
import json
import os

luaDirectory = "/home/brendoncintas/.config/rpcs3/dev_hdd0/game/NPIA00010/USRDIR/MINIGAMES/FLYING_SAUCER/"

def formatResponse(data):
    luaEncodeCode = f"print(Jamin.encode({json.dumps(data)}))"
    jaminEncodedData = runLuaScript(luaEncodeCode)
    return f"<ohs>{jaminEncodedData}</ohs>"

def runLuaScript(luaCode):

    luaFiles = [f for f in os.listdir(luaDirectory) if f.endswith('.lua')]
    requireStatements = '\n'.join([f"require '{os.path.abspath(os.path.join(luaDirectory, f)).replace(os.sep, '/')}'" for f in luaFiles])

    luaFull = f"{requireStatements}\n{luaCode}"

    result = subprocess.run(['lua', '-e', luaFull], capture_output=True, text=True)
    return result.stdout.strip()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path.startswith("/SCEA/SaucerPop/leaderboard/requestbyrank/"):
            self.handleRequestByRank()
        elif self.path.startswith("/SCEA/SaucerPop/user/getwritekey/"):
            self.handleGetWriteKey()
        elif self.path.startswith("/SCEA/SaucerPop/leaderboard/updatesameentry/"):
            self.handleUpdateSameEntry()

    def handleUpdateSameEntry(self):
        contentLength = int(self.headers['Content-Length'])
        postData = self.rfile.read(contentLength).decode('utf-8')
        print("Raw POST Data:", postData)

        response = formatResponse(postData)
        self.send_response(200)
        self.send_header('Content-type', 'application/xml')
        self.end_headers()
        self.wfile.write(response.encode())

    def handleGetWriteKey(self):
        writeKey = "static-key"  # In a real application, this should be generated or retrieved securely.
        responseData = {"writeKey": writeKey}
        print(b"Response Data:", responseData)
        response = formatResponse(responseData)
        self.send_response(200)
        self.send_header('Content-type', 'application/xml')
        self.end_headers()
        self.wfile.write(response.encode())

    def handleRequestByRank(self):
        contentLength = int(self.headers['Content-Length'])
        postData = self.rfile.read(contentLength).decode('utf-8')
        print(b"Raw POST Data:", postData)

        leaderboardType = urllib.parse.parse_qs(postData).get('type', ['alltime'])[0]

        if leaderboardType == 'daily':
            luaLeaderboardCode = "print(getDailyLeaderboard())"
        else:
            luaLeaderboardCode = "print(getAllTimeLeaderboard())"

        leaderboardData = runLuaScript(luaLeaderboardCode)

        response = formatResponse(leaderboardData)
        self.send_response(200)
        self.send_header('Content-type', 'application/xml')
        self.end_headers()
        self.wfile.write(response.encode())


if __name__ == '__main__':
    serverAddress = ('localhost', 8080)
    httpd = HTTPServer(serverAddress, SimpleHTTPRequestHandler)
    print("Server started at http://localhost:8080")
    httpd.serve_forever()
