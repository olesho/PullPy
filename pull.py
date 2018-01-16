#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import urllib
import git
import json
from subprocess import call
import os
import logging
import subprocess

#defaults
logging.basicConfig(filename='pull.log',level=logging.DEBUG)
hostName = "localhost"
hostPort = 5000

with open('config.json') as config_file:
	conf = json.load(config_file)
	hostName = conf.get('Host')
	hostPort = conf.get('Port')

logging.info("Will listen to "+hostName+":"+str(hostPort))


with open('repos.json') as data_file:
	repos = json.load(data_file)

def match_repo(name, code):
	res = []
	for k, v in enumerate(repos):
		if (name == v.get('name')) and (code == v.get('code')) and (v.get('enabled')):
			res.append(v)
	print(res)
	return res

def pull(path, repoName, branch, script):
	if script:
		subprocess.call([script])
		return
	repo = git.Repo(path)
	o = repo.remotes.origin
	o.fetch()
	repo.head.ref.set_tracking_branch(o.refs[branch])
	res = o.pull()
	logging.info(res)
	logging.info('Done: '+repo.remotes.origin.url)

for k, repo in enumerate(repos):
	if (repo.get('enabled')):
		pull(repo.get('path'), repo.get('name'), repo.get('branch'), repo.get('script'))


class PullServer(BaseHTTPRequestHandler):
	def do_POST(self):
		fields = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

		codes = fields.get('code')
		code = codes[0] if codes else None
		names = fields.get('name')
		name = names[0] if names else None

		repos = match_repo(name, code)
		if (len(repos) > 0):
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write("Success".encode())
		else:
			logging.info("No repo found")
			self.send_response(404)

		for repo in repos:
			path = repo.get('path')
			name = repo.get('name')
			branch = repo.get('branch')
			script = repo.get('script')
			pull(path, name, branch, script)

myServer = HTTPServer((hostName, hostPort), PullServer)
logging.info(time.asctime() + " Server Starts - %s:%s" % (hostName, str(hostPort)))

try:
	myServer.serve_forever()
except KeyboardInterrupt:
	pass

myServer.server_close()
logging.info(time.asctime() + "Server Stops - %s:%s" % (hostName, hostPort))
