import sys
import argparse
import heapq
import pickle
from collections import defaultdict

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def calculate_frequencies(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        sys.exit(1)

    frequencies = defaultdict(int)
    for char in text:
        frequencies[char] += 1
    
    return frequencies, text

def build_huffman_tree(frequencies):
    heap = [Node(char, freq) for char, freq in frequencies.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0]  # root of the Huffman tree

def generate_codes(node, prefix="", codebook=None):
    if codebook is None:
        codebook = {}

    if node.char is not None:  # It's a leaf node
        codebook[node.char] = prefix
    else:
        generate_codes(node.left, prefix + "0", codebook)
        generate_codes(node.right, prefix + "1", codebook)

    return codebook

def encode_text(text, codebook):
    encoded_text = ''.join(codebook[char] for char in text)
    return encoded_text

def write_header(filename, codebook):
    with open(filename, 'wb') as file:
        pickle.dump(codebook, file)  # Serialize the codebook using pickle

def write_encoded_text(filename, text, codebook):
    encoded_text = encode_text(text, codebook)
    # Convert the bit string to bytes
    padded_encoded_text = encoded_text + '0' * ((8 - len(encoded_text) % 8) % 8)
    byte_array = bytearray(int(padded_encoded_text[i:i+8], 2) for i in range(0, len(padded_encoded_text), 8))
    
    with open(filename, 'ab') as file:
        file.write(byte_array)

def read_header(filename):
    with open(filename, 'rb') as file:
        codebook = pickle.load(file)
    return codebook

def decode_text(encoded_text, codebook):
    reverse_codebook = {v: k for k, v in codebook.items()}
    current_code = ""
    decoded_text = []

    for bit in encoded_text:
        current_code += bit
        if current_code in reverse_codebook:
            decoded_text.append(reverse_codebook[current_code])
            current_code = ""

    return ''.join(decoded_text)

def read_encoded_text(filename, codebook):
    with open(filename, 'rb') as file:
        file.seek(len(pickle.dumps(codebook)))  # Skip the header
        byte_data = file.read()

    encoded_text = ''.join(f'{byte:08b}' for byte in byte_data)
    return decode_text(encoded_text, codebook)

def compress_file(input_file, output_file):
    frequencies, text = calculate_frequencies(input_file)
    huffman_tree = build_huffman_tree(frequencies)
    codebook = generate_codes(huffman_tree)
    
    write_header(output_file, codebook)
    write_encoded_text(output_file, text, codebook)
    print(f"File '{input_file}' compressed and saved as '{output_file}'.")

def decompress_file(input_file, output_file):
    codebook = read_header(input_file)
    decoded_text = read_encoded_text(input_file, codebook)
    
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(decoded_text)
    
    print(f"File '{input_file}' decompressed and saved as '{output_file}'.")

def main():
    parser = argparse.ArgumentParser(description="Huffman Compression CLI Tool")
    parser.add_argument("action", choices=["compress", "decompress"], help="Action to perform: compress or decompress")
    parser.add_argument("input_file", help="Input file path")
    parser.add_argument("output_file", help="Output file path")

    args = parser.parse_args()

    if args.action == "compress":
        compress_file(args.input_file, args.output_file)
    elif args.action == "decompress":
        decompress_file(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
