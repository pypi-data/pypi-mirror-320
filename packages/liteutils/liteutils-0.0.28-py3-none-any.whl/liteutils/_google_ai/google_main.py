# word_similarity.py

import difflib
from wordllama import WordLlama

def word_similarity(word1, word2):
    """
    Calculate the similarity between two words.
    
    Args:
    word1 (str): The first word.
    word2 (str): The second word.
    
    Returns:
    float: A similarity score between 0 and 1, where 1 means identical.
    """
    # Initialize WordLlama
    llm = WordLlama()
    
    # Get embeddings for the words
    embedding1 = llm.get_embedding(word1)
    embedding2 = llm.get_embedding(word2)
    
    # Calculate cosine similarity between the embeddings
    similarity = llm.cosine_similarity(embedding1, embedding2)
    
    return similarity

# Example usage
if __name__ == "__main__":
    word1 = "hello"
    word2 = "hallo"
    similarity = word_similarity(word1, word2)
    print(f"The similarity between '{word1}' and '{word2}' is {similarity:.2f}")
