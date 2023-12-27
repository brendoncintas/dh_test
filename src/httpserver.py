from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import urllib.parse
import json
import os

# jaminLuaPath = "/home/brendoncintas/.config/rpcs3/dev_hdd0/game/NPIA00010/USRDIR/MINIGAMES/FLYING_SAUCER/JAMIN.LUA"
# saucerLeaderboardLuaPath = "/home/brendoncintas/.config/rpcs3/dev_hdd0/game/NPIA00010/USRDIR/MINIGAMES/FLYING_SAUCER/SAUCERLEADERBOARD.LUA"
luaDirectory = "~/.config/rpcs3/dev_hdd0/game/NPIA00010/USRDIR/MINIGAMES/FLYING_SAUCER/"

""" # Function to run Lua script
def runLuaScript(luaCode):
    command = f"require '{os.path.abspath(jaminLuaPath).replace(os.sep, '/')}'\n" \
              f"require '{os.path.abspath(saucerLeaderboardLuaPath).replace(os.sep, '/')}'\n{luaCode}"
    result = subprocess.run(['lua', '-e', command], capture_output=True, text=True)
    return result.stdout.strip() """

def runLuaScript(luaCode):

    luaFiles = [f for f in os.listdir(luaDirectory) if f.endswith('.lua')]
    requireStatements = '\n'.join([f"require '{os.path.abspath(os.path.join(luaDirectory, f)).replace(os.sep, '/')}'" for f in luaFiles])

    luaFull = f"{requireStatements}\n{luaCode}"

    result = subprocess.run(['lua', '-e', luaFull], capture_output=True, text=True)
    return result.stdout.strip()

def formatResponse(data):
    luaEncodeCode = f"print(encode({json.dumps(data)}))"
    jaminEncodedData = runLuaScript(luaEncodeCode)
    return f"<ohs>{jaminEncodedData}</ohs>"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path.startswith("/SCEA/SaucerPop/leaderboard/requestbyrank/"):
            self.handleRequestByRank()

    def handleRequestByRank(self):
        contentLength = int(self.headers['Content-Length'])
        postData = self.rfile.read(contentLength)
        leaderboardType = urllib.parse.parse_qs(postData.decode()).get('type', ['alltime'])[0]

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
