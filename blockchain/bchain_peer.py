# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 15:03:44 2020

@author: rnfr
"""
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):
        self.chain = []
        self.mempool = []
        self.create_block(hash_proof = 1, previous_hash = '0')
        self.peers = set()
        
    def create_block(self, hash_proof, previous_hash):
        block = {
                'index': len(self.chain) + 1,
                'timestamp': str(datetime.datetime.now()),
                'proof': hash_proof,
                'previous_hash': previous_hash,
                'transactions': self.mempool
        }
        self.mempool = []
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def pwork(self, previous):
        proof = 1
        checked = False
        while checked is False:
            hash_operation = hashlib.sha256(str(proof**2 - previous**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                checked = True
            else:
                proof += 1
        return proof
    
    def get_block_hash(self, block):
        encoded = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded).hexdigest()
    
    def validate_chain(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            current_block = chain[block_index]
            linked = current_block['previous_hash'] == self.get_block_hash(previous_block)
            if not linked:
                return False
            previous_proof = previous_block['proof']
            current_proof = current_block['proof']
            hash_operation = hashlib.sha256(str(current_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = current_block
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount):
        new_transaction = {
                'sender': sender,
                'receiver': receiver,
                'amount': amount
        }
        self.mempool.append(new_transaction)
        last_block = self.get_previous_block()
        return last_block['index']
    
    def add_node(self, address):
        parsed = urlparse(address)
        self.peers.add(parsed.netloc)
        
    def replace_chain(self):
        network = self.peers
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['chain_size']
                chain = response.json()['chain']
                if length > max_length and self.validate_chain(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
    
app = Flask(__name__)

blockchain = Blockchain()

node_address = str(uuid4()).replace('-', '')

@app.route('/mine', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    current_proof = blockchain.pwork(previous_proof)
    previous_hash = blockchain.get_block_hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = node_address, amount = 1)
    created_block = blockchain.create_block(current_proof, previous_hash)
    response = {
          'message': 'You created a new block',
          'block': created_block
    }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    response = {
          'chain': blockchain.chain,
          'chain_size': len(blockchain.chain)
    }    
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def is_valid():
    valid_chain = blockchain.validate_chain(blockchain.chain)
    if valid_chain:
        status = {
          'message': 'Blockchain is in valid state'
        }
    else:
        status = {
          'message': 'Blockchain state is invalid'
        }
    return jsonify(status), 200

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    expected_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in expected_keys):
        return 'Missing required transaction data', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {
            'message': f'Transaction will be added to block {index}'
    }
    return jsonify(response), 201

@app.route('/connect_nodes', methods=['POST'])
def connect_nodes():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
            return 'No connectable node address specified', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {
            'message': 'Nodes connected',
            'nodes': list(blockchain.peers)
    }
    return jsonify(response), 201

@app.route('/nodes', methods=['GET'])
def get_nodes():
    response = {
            'message': 'Nodes available',
            'nodes': list(blockchain.peers)
    }
    return jsonify(response), 200

@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_replaced = blockchain.replace_chain()
    if is_replaced:
        status = {
          'message': 'Chain was replaced by the longest one among all nodes',
          'chain': blockchain.chain
        }
    else:
        status = {
          'message': 'Chain is the same is all nodes, no need to replace',
          'chain': blockchain.chain
        }
    return jsonify(status), 200

app.run(host = '0.0.0.0', port = 5001)