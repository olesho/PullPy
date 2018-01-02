#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import urllib
import git
import json
from subprocess import call
import os


# eval not working yet
'''
import subprocess
def c(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print(proc_stdout)

c('eval `ssh-agent -s`')
c('ssh-add ~/.ssh/wellmux')
'''

hostName = "46.101.219.50"
hostPort = 5000

with open('repos.json') as data_file:
	repos = json.load(data_file)

def match_repo(name, code):
	print('Match?:', name, code)
	for k, v in enumerate(repos):
		if (name == v.get('name')) and (code == v.get('code')):
			print('Success match:', name, code)
			return v.get('path')
	return False

def pull(path, repoName):
	print(repoName, 'pull started')
	print('Path:', path)
	repo = git.Repo(path)
	o = repo.remotes.origin
	print('Origin:', repo.remotes.origin.url)
	o.fetch()
	repo.head.ref.set_tracking_branch(o.refs.master)
	o.pull()
	print('Done:', repoName)

for k, v in enumerate(repos):
	if (v.get('enabled')):
#		print(v.get('path'))
#		print(v.get('name'))
		pull(v.get('path'), v.get('name'))


class MyServer(BaseHTTPRequestHandler):
	def do_POST(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

		fields = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

		codes = fields.get('code')
		code = codes[0] if codes else None
		names = fields.get('name')
		name = names[0] if names else None

		path = match_repo(name, code)	
		if path:
			pull(path, name)

	def do_GET(self):
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                fields = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

                codes = fields.get('code')
                code = codes[0] if codes else None
                names = fields.get('name')
                name = names[0] if names else None

                path = match_repo(name, code)
                if path:
                        pull(path, name)

myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
	myServer.serve_forever()
except KeyboardInterrupt:
	pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
