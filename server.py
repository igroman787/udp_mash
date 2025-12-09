#!/usr/bin/env python3
# -*- coding: utf_8 -*-

from os.path import isfile
from nacl.signing import SigningKey
import requests
from time import sleep
from random import randint

from udp_lib.udp_lib import UdpSocket
from udp_lib.bytes_lib import BytesReader, BytesWriter
from udp_lib.schemes_lib import Scheme
from udp_lib.utils_lib import (
	bcolors,
	get_time_str,
	create_udp_url,
	parse_udp_url,
	ip2uint,
	uint2ip
)
from utils_lib import (
	print_table,
	start_thread,
	start_cycle,
	try_function
)
from methods import (
	get_peers_len_method,
	get_peers_method,
	get_peer_ip_method,
	get_hostname_method
)
from reactions import (
	get_peers_len_reaction,
	get_peer_reaction,
	get_peer_ip_reaction,
	get_hostname_reaction,
	get_peer_statistics_reaction
)

FIRST_NODES = """
xei57Oo2lP2f55EEaV3SY7cqQH8ODk424ld23375ONfF6Z4z7O99zZoC/r0=
xeiwYrxKZj318M/Nq1DL/ba4ELmIu3gxECBsbCj8WQF2RDnZLXXjww8rzsc=
"""



class UdpMash():
	def __init__(self):
		privkey, port = load_config()
		self.udp_socket = UdpSocket(privkey, port)
		self.host = None
		self.udp_url = None

		self.add_nodes(load_nodes("nodes.list"))
		self.old_nodes = self.get_nodes_from_peers(self.udp_socket.peers)

		self.udp_socket.add_reaction("get_peers_len", get_peers_len_reaction)
		self.udp_socket.add_reaction("get_peer", get_peer_reaction)
		self.udp_socket.add_reaction("get_peer_ip", get_peer_ip_reaction)
		self.udp_socket.add_reaction("get_hostname", get_hostname_reaction)
		self.udp_socket.add_reaction("get_peer_statistics", get_peer_statistics_reaction)
		
		start_cycle(self.connecting, sec=3)
		start_cycle(self.scanning, sec=30)
		start_cycle(self.saving, sec=3)
	#end define

	def connecting(self):
		peers_copy = self.udp_socket.peers.copy()
		for addr, peer in peers_copy.items():
			if peer and peer.is_allive():
				continue
			if peer and not peer.is_ready_to_connect():
				continue
			self.connect(addr, peer.pubkey)
	#end define

	def connect(self, addr, pubkey):
		peer = self.udp_socket.connect(addr, pubkey)
		if peer is None:
			return
		self.udp_socket.peers[addr] = peer
	#end define

	def scanning(self):
		peers_copy = self.udp_socket.peers.copy()
		for addr, peer in peers_copy.items():
			if not peer.is_allive():
				continue
			nodes = try_function(get_peers_method, peer)
			if nodes == None:
				continue
			self.add_nodes(nodes)
	#end define

	def add_nodes(self, nodes):
		for addr, pubkey in nodes.items():
			self.add_node(addr, pubkey)
	#end define

	def add_node(self, addr, pubkey):
		know_peer = self.udp_socket.peers.get(addr)
		if know_peer and know_peer.pubkey == pubkey:
			return
		if self.udp_socket.local_pub == pubkey:
			return
		self.connect(addr, pubkey)
	#end define

	def saving(self):
		file_path = "nodes.list"
		nodes = self.get_nodes_from_peers(self.udp_socket.peers)
		if nodes == self.old_nodes:
			return
		text = ""
		for addr, pubkey in nodes.items():
			text += create_udp_url(addr[0], addr[1], pubkey) + '\n'
		with open(file_path, 'wt') as file:
			file.write(text)
		self.old_nodes = nodes.copy()
	#end define

	def get_nodes_from_peers(self, peers):
		result = dict()
		for addr, peer in peers.copy().items():
			result[addr] = peer.pubkey
		return result
	#end define

	def get_my_ip(self):
		if self.host:
			return self.host
		buff = dict()
		peers_copy = self.udp_socket.peers.copy()
		for addr, peer in peers_copy.items():
			if not peer.is_allive():
				continue
			ip = try_function(get_peer_ip_method, peer)
			if ip is None:
				continue
			if ip in buff:
				buff[ip] +=  1
			else:
				buff[ip] =  1
		if len(buff) == 0:
			requests.packages.urllib3.util.connection.HAS_IPV6 = False
			self.host = requests.get("https://ifconfig.me/ip").text
			return self.host
		self.host = max(buff, key=buff.get)
		return self.host
	#end define

	def get_my_url(self):
		if self.udp_url:
			return self.udp_url
		self.udp_url = self.udp_socket.get_url(server.host)
		return self.udp_url
	#end define
#end class

def load_nodes(file_path):
	if isfile(file_path):
		nodes = load_nodes_from_file(file_path)
	else:
		nodes = load_first_nodes()
	return nodes
#end define

def load_first_nodes():
	urls = FIRST_NODES.split('\n')
	nodes = load_urls(urls)
	return nodes
#end define

def load_nodes_from_file(file_path):
	with open(file_path, 'rt') as file:
		text = file.read()
	urls = text.split('\n')
	nodes = load_urls(urls)
	return nodes
#end define

def load_urls(urls):
	nodes = dict()
	for url in urls:
		if len(url) == 0:
			continue
		addr, pubkey = parse_udp_url(url)
		nodes[addr] = pubkey
	return nodes
#end define

def load_config(file_path="private.key"):
	if isfile(file_path):
		privkey, port = read_config(file_path)
	else:
		privkey, port = generate_config(file_path)
	return privkey, port
#end define

def read_config(file_path):
	with open(file_path, 'rb') as file:
		reader = BytesReader(file.read())
	privkey = reader.read(32)
	port = reader.read_uint16()
	return privkey, port
#end define

def generate_config(keypath):
	port = randint(2000, 65000)
	privkey = SigningKey.generate().encode()
	writer = BytesWriter()
	writer.write(privkey)
	writer.write_uint16(port)
	with open(keypath, 'wb') as file:
		file.write(writer.data)
	return privkey, port
#end define

def get_peer_hostname(peer):
	if peer.buff.hostname:
		return peer.buff.hostname
	if not peer.is_allive():
		return
	hostname = try_function(get_hostname_method, peer)
	if hostname:
		peer.buff.hostname = hostname
	return hostname
#end define

def print_peers(udp_socket):
	table = [["Peer", "Hostname", "Pings", "Connections", "Connect ago", "Ping ago", "Allive"]]
	for addr, peer in udp_socket.peers.items():
		ip = addr[0]
		port = addr[1]
		addr_str = f"{ip}:{port}"
		hostname = get_peer_hostname(peer)
		pings = peer.statistics.pings_ok
		connections = f"{peer.statistics.connects_ok}/{peer.statistics.connects_error}"
		if peer.is_allive():
			allive = f"{bcolors.green} true {bcolors.endc}"
		else:
			allive = f"{bcolors.red} false {bcolors.endc}"
		connect_ago = f"{peer.get_milli_connecting_ago()//1000}/{peer.delta_connect_time//1000}"
		ping_ago = peer.get_milli_ping_ago() // 1000
		table += [[addr_str, hostname, pings, connections, connect_ago, ping_ago, allive]]
	print_table(table)
#end define

def run_peer_table():
	sleep(3)
	while True:
		print('\033c', end='')

		server.host = server.get_my_ip()
		server.udp_url = server.get_my_url()

		print("url:", server.udp_url)
		print("host:", f"{server.host}:{server.udp_socket.port}")
		print("time:", get_time_str())
		print_peers(server.udp_socket)
		sleep(1)
	#end while
#end define




server = UdpMash()
run_peer_table()











