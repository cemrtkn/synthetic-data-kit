# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.
# Text processing utilities
import re
import json
from typing import List, Dict, Any

def split_into_chunks(text: str, chunk_size: int = 4000, overlap: int = 200) -> List[str]:
    """Split text into chunks with optional overlap"""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append(current_chunk)
            # Keep some overlap for context
            sentences = current_chunk.split('. ')
            if len(sentences) > 3:
                current_chunk = '. '.join(sentences[-3:]) + "\n\n" + para
            else:
                current_chunk = para
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Extract JSON from text that might contain markdown or other content"""
    text = text.strip()
    
    # Try to parse as complete JSON
    if text.startswith('{') and text.endswith('}') or text.startswith('[') and text.endswith(']'):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    
    # Look for JSON within Markdown code blocks
    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    match = re.search(json_pattern, text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
    
    # Try a more aggressive pattern
    json_pattern = r'\{[\s\S]*\}|\[[\s\S]*\]'
    match = re.search(json_pattern, text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    
    raise ValueError("Could not extract valid JSON from the response")



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