#!/usr/bin/env python3
# -*- coding: utf_8 -*-

import socket
from udp_lib.schemes_lib import Scheme
from udp_lib.utils_lib import ip2uint, uint2ip


def get_online_peers(peers):
	result = dict()
	peers_copy = peers.copy()
	for addr, peer in peers_copy.items():
		if peer.delta_connect_time < 9000:
			result[addr] = peer
	return result
#end define

def get_peers_len_reaction(udp_socket, **kwargs):
	# outgoing_message
	peers = get_online_peers(udp_socket.peers)
	peers_len = len(peers)
	scheme = Scheme("peers = peers_len:uint32")
	outgoing_message = scheme.serialize(peers_len=peers_len)
	return outgoing_message
#end define

def get_peer_reaction(udp_socket, message, **kwargs):
	# incoming_message
	scheme = Scheme("get_peer = id:uint32")
	incoming_message = scheme.deserialize(message)
	peer_id = incoming_message.id

	# outgoing_message
	scheme = Scheme("peer = id:uint32, ip:uint32, port:uint16, pubkey:#32")
	peers = get_online_peers(udp_socket.peers)
	peers_list = list(peers.keys())
	peer_addr = peers_list[peer_id]
	peer_pubkey = peers.get(peer_addr).pubkey
	peer_ip = ip2uint(peer_addr[0])
	peer_port = peer_addr[1]
	outgoing_message = scheme.serialize(id=peer_id, ip=peer_ip, port=peer_port, pubkey=peer_pubkey)
	return outgoing_message
#end define

def get_peer_ip_reaction(udp_socket, peer, **kwargs):
	# outgoing_message
	peer_ip = ip2uint(peer.addr[0])
	scheme = Scheme("peer = ip:uint32")
	outgoing_message = scheme.serialize(ip=peer_ip)
	return outgoing_message
#end define

def get_hostname_reaction(udp_socket, peer, **kwargs):
	# outgoing_message
	hostname = socket.gethostname().encode("utf-8")
	scheme = Scheme("response = hostname_len:uint32, hostname:#hostname_len")
	outgoing_message = scheme.serialize(hostname_len=len(hostname), hostname=hostname)
	return outgoing_message
#end define

def get_peer_statistics_reaction(udp_socket, peer, **kwargs):
	# incoming_message
	scheme = Scheme("get_peer_statistics = ip:uint32, port:uint16")
	incoming_message = scheme.deserialize(message)
	peer_ip = uint2ip(incoming_message.ip)
	peer_addr = (peer_ip, incoming_message.port)

	# outgoing_message
	scheme = Scheme("peer_statistics = pings_ok:uint32, connects_ok:uint32, connects_error:uint32")
	need_peer = peers.get(peer_addr)
	outgoing_message = scheme.serialize(
		pings_ok=need_peer.statistics.pings_ok, 
		connects_ok=need_peer.statistics.connects_ok, 
		connects_error=need_peer.statistics.connects_error
	)
	return outgoing_message
#end define
