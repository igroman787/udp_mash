#!/usr/bin/env python3
# -*- coding: utf_8 -*-

from udp_lib.schemes_lib import Scheme
from udp_lib.utils_lib import ip2uint, uint2ip
from utils_lib import try_several_times


def get_peers_len_method(peer):
	message_id = peer.send_encrypted_message("get_peers_len")
	message_bytes = peer.read_encrypted_message(message_id)
	if message_bytes == None:
		raise Exception("get_peers_len_method error: message_bytes == None")
	scheme = Scheme("peers = peers_len:uint32")
	message = scheme.deserialize(message_bytes)
	return message.peers_len
#end define

def get_peers_method(peer):
	nodes = dict()
	peers_len = get_peers_len_method(peer)
	for peer_id in range(0, peers_len):
		peer_addr, pubkey = try_several_times(get_peer_method, peer, peer_id)
		nodes[peer_addr] = pubkey
	peer.buff.last_know_peers_len = peers_len
	return nodes
#end define

def get_peer_method(peer, peer_id):
	outgoing_scheme = Scheme("get_peer = id:uint32")
	incoming_scheme = Scheme("peer = id:uint32, ip:uint32, port:uint16, pubkey:#32")
	outgoing_message = outgoing_scheme.serialize(id=peer_id)
	message_id = peer.send_encrypted_message("get_peer", outgoing_message)
	message_bytes = peer.read_encrypted_message(message_id)
	if message_bytes == None:
		raise Exception("get_peer_method error: message_bytes == None")
	message = incoming_scheme.deserialize(message_bytes)
	peer_ip = uint2ip(message.ip)
	peer_addr = (peer_ip, message.port)
	return peer_addr, message.pubkey
#end define

def get_peer_ip_method(peer):
	message_id = peer.send_encrypted_message("get_peer_ip")
	message_bytes = peer.read_encrypted_message(message_id)
	if message_bytes == None:
		raise Exception("get_peer_ip_method error: message_bytes == None")
	scheme = Scheme("peer = ip:uint32")
	message = scheme.deserialize(message_bytes)
	return uint2ip(message.ip)
#end define

def get_hostname_method(peer):
	message_id = peer.send_encrypted_message("get_hostname")
	message_bytes = peer.read_encrypted_message(message_id)
	if message_bytes == None:
		raise Exception("get_hostname_method error: message_bytes == None")
	scheme = Scheme("response = hostname_len:uint32, hostname:#hostname_len")
	message = scheme.deserialize(message_bytes)
	return message.hostname.decode("utf-8")
#end define

def get_peers_statistics_method(peer):
	nodes = get_peers_method(peer)
	peers_len = get_peers_len_method(peer)
	for peer_addr in nodes:
		nodes[peer_addr] = try_several_times(get_peer_statistics_method, peer, peer_addr)
	peer.buff.last_know_peers_len = peers_len
	return nodes
#end define

def get_peer_statistics_method(peer, peer_addr):
	outgoing_scheme = Scheme("get_peer_statistics = ip:uint32, port:uint16")
	incoming_scheme = Scheme("peer_statistics = pings_ok:uint32, connects_ok:uint32, connects_error:uint32")
	peer_ip = ip2uint(peer_addr[0])
	peer_port = peer_addr[1]
	outgoing_message = outgoing_scheme.serialize(ip=peer_ip, port=peer_port)
	message_id = peer.send_encrypted_message("get_peer", outgoing_message)
	message_bytes = peer.read_encrypted_message(message_id)
	if message_bytes == None:
		raise Exception("get_peer_statistics_method error: message_bytes == None")
	message = incoming_scheme.deserialize(message_bytes)
	return message
#end define
