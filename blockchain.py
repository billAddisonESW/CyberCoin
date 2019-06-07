import hashlib
import json
from time import localtime, strftime
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

import os,time
os.environ['TZ'] = 'Asia/Dubai'
time.tzset()


class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """
        Add a new node to the list of nodes

        :param address: Address of node e.g. 'cyberuser'
        """

        if address in self.nodes or address=="the_blockchain_itself":
            return False
        else:
            self.nodes.add(address)
            return True


    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    # def resolve_conflicts(self):
    #     """
    #     This is our consensus algorithm, it resolves conflicts
    #     by replacing our chain with the longest one in the network.

    #     :return: True if our chain was replaced, False if not
    #     """

    #     neighbours = self.nodes
    #     new_chain = None

    #     # We're only looking for chains longer than ours
    #     max_length = len(self.chain)

    #     # Grab and verify the chains from all the nodes in our network
    #     for node in neighbours:
    #         response = requests.get(f'http://{node}/chain')

    #         if response.status_code == 200:
    #             length = response.json()['length']
    #             chain = response.json()['chain']

    #             # Check if the length is longer and the chain is valid
    #             if length > max_length and self.valid_chain(chain):
    #                 max_length = length
    #                 new_chain = chain

    #     # Replace our chain if we discovered a new, valid chain longer than ours
    #     if new_chain:
    #         self.chain = new_chain
    #         return True

    #     return False

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain

        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': strftime("%a, %d %b %Y %H:%M:%S", localtime()),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:

         - Find a number p' such that hash(pp') contains leading {self.difficulty} zeroes
         - Where p is the previous proof, and p' is the new proof
         
        :param last_block: <dict> last Block
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.

        """
        difficulty = 5 # How many zeroes at the start of a hashed proof of work?
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == "0"*difficulty


# Instantiate the Node
app = Flask(__name__, static_url_path='/', static_folder='static')
CORS(app)

# Generate a globally unique address for this node
node_identifier = "the_blockchain_itself" #str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/')
def client_root():
    return app.send_static_file('index.html')
@app.route('/<path:path>')
def client_files(path):
    return send_from_directory('static', path)

# Provide an easy reset, for use only by the workshop leader
# --BAG 2 Sep 2018
@app.route('/reset', methods=['GET'])
def reset():
    blockchain.__init__()
    response = {'message': 'Blockchain has been reset. Ensure all clients are refreshed.'}
    return jsonify(response), 200


@app.route('/mine', methods=['POST'])
def mine():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['requester']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "the_blockchain_itself" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="the_blockchain_itself",
        recipient=values['requester'],
        amount=100,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'previous_proof': last_block['proof'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/transactions', methods=['GET'])
def list_unconfirmed_transactions():
    response = {
        'unconfirmed_transactions': blockchain.current_transactions
    }
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    # required = ['address']
    # if not all(k in values for k in required):
    #     return 'Missing values', 400

    node_added = blockchain.register_node(values['address'])

    if node_added:
        response = {
            'message': 'New node has been added',
            'nodes': list(blockchain.nodes),
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'A node already exists with this address identifier',
            'nodes': list(blockchain.nodes),
        }
        return jsonify(response), 409


@app.route('/nodes', methods=['GET'])
def list_nodes():
    response = {
        'nodes': list(blockchain.nodes)
    }
    return jsonify(response), 200


# @app.route('/nodes/resolve', methods=['GET'])
# def consensus():
#     replaced = blockchain.resolve_conflicts()

#     if replaced:
#         response = {
#             'message': 'Our chain was replaced',
#             'new_chain': blockchain.chain
#         }
#     else:
#         response = {
#             'message': 'Our chain is authoritative',
#             'chain': blockchain.chain
#         }

#     return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=80, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
