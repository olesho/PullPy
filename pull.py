#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import urllib
import git
import json
from subprocess import call
import os

#defaults
hostName = "localhost"
hostPort = 5000

with open('config.json') as config_file:
	conf = json.load(config_file)
	hostName = conf.get('Host')
	hostPort = conf.get('Port')

print("Will listen to", hostName+":"+str(hostPort))


with open('repos.json') as data_file:
	repos = json.load(data_file)

def match_repo(name, code):
	for k, v in enumerate(repos):
		if (name == v.get('name')) and (code == v.get('code')):
			return v
	return False

def pull(path, repoName, branch):
	repo = git.Repo(path)
	o = repo.remotes.origin
	o.fetch()
	repo.head.ref.set_tracking_branch(o.refs[branch])
	res = o.pull()
	print(res)
	print('Done:', repo.remotes.origin.url)

for k, repo in enumerate(repos):
	if (repo.get('enabled')):
		pull(repo.get('path'), repo.get('name'), repo.get('branch'))


class PullServer(BaseHTTPRequestHandler):
	def do_POST(self):
		fields = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

		codes = fields.get('code')
		code = codes[0] if codes else None
		names = fields.get('name')
		name = names[0] if names else None

		repo = match_repo(name, code)
		if repo:
			if repo.get('enabled'):
				path = repo.get('path')
				name = repo.get('name')
				branch = repo.get('branch')
				print("Repo found. Path:", path, "Name:", name, "Branch:", branch)

				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()
				self.wfile.write("Success".encode())

				pull(path, name, branch)
		else:
			print("No repo found")

			self.send_response(404)
			self.end_headers()

myServer = HTTPServer((hostName, hostPort), PullServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
	myServer.serve_forever()
except KeyboardInterrupt:
	pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
