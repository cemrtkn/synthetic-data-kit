from synthetic_data_kit.utils.text import split_into_chunks
from chonkie import RecursiveChunker, RecursiveRules, RecursiveLevel, OverlapRefinery
import os
import time


def conditional_overlap(chunks, required_length=800, overlap_size=0.1, overlapper=None):
    """Apply overlap only to chunks under the specified character threshold"""
    overlapped_chunks = []
    
    for i, chunk in enumerate(chunks):
        if  len(chunk.text)/required_length < (1 - overlap_size):
            # Create a mini-list with current chunk and adjacent chunks for context
            chunk_subset = []
            
            if i > 0:
                chunk_subset.append(chunks[i-1])
            
            chunk_subset.append(chunk)
            
            if i < len(chunks) - 1:
                chunk_subset.append(chunks[i+1])
            
            overlapped_subset = overlapper(chunk_subset)
            
            # Extract the overlapped version of our target chunk
            target_idx = 1 if i > 0 else 0  # Adjust index based on whether we included previous chunk
            overlapped_chunks.append(overlapped_subset[target_idx])
        else:
            overlapped_chunks.append(chunk)
    
    return overlapped_chunks

chunker_rules = RecursiveRules([
    RecursiveLevel(delimiters=["\n\n"], include_delim=None),  # Paragraph boundaries
    RecursiveLevel(delimiters=[". ", "! ", "? "], include_delim="prev"),  # Sentence boundaries
])

overlapper_rules = RecursiveRules([
    RecursiveLevel(whitespace=True),  # Paragraph boundaries
])

chunk_size = 800
overlap_size = 0.25

# Initialize the chunker
chunker = RecursiveChunker(chunk_size=chunk_size, min_characters_per_chunk=400, rules=chunker_rules)
overlapper = OverlapRefinery(tokenizer_or_token_counter="character", context_size=overlap_size, method="suffix", rules=overlapper_rules, inplace=False)

data_dir = "sample_data/"
files = [data_dir + f for f in os.listdir(data_dir)]

files = [files[1]]

for file in files:
    with open(file, "r") as f:
        text = f.read()
    chonkie_chunks = chunker(text)
    overlapped_chunks = conditional_overlap(chonkie_chunks, required_length=chunk_size, overlap_size=overlap_size, overlapper=overlapper)
    sdk_chunks = split_into_chunks(text, chunk_size=200, overlap=20)
    print("Number of chunks: chonkie", len(chonkie_chunks), "sdk", len(sdk_chunks))
    for idx,chunk in enumerate(chonkie_chunks):
        print("Overlapped chunks:")
        print(overlapped_chunks[idx])
        print("-" * 100)
        print("Chonkie chunks:")
        print(chonkie_chunks[idx])
        print("-" * 100)
        """print("SDK chunks:")
        print(sdk_chunks[idx])
        print("-" * 100)"""
        time.sleep(2)
        