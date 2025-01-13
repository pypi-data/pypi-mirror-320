from typing import List, Dict, Tuple
from Levenshtein import distance as levenshtein_distance
from difflib import SequenceMatcher
import re

def levenshtein_similarity(word1: str, word2: str) -> float:
    """
    Calcule la similarité basée sur la distance de Levenshtein
    Adaptée pour les fautes de frappe et substitutions
    """
    word1, word2 = word1.lower(), word2.lower()
    max_len = max(len(word1), len(word2))
    if max_len == 0:
        return 0
    distance = levenshtein_distance(word1, word2)
    return 1 - (distance / max_len)

def sequence_similarity(word1: str, word2: str) -> float:
    """
    Calcule la similarité de séquence
    Meilleure pour détecter les parties communes
    """
    return SequenceMatcher(None, word1.lower(), word2.lower()).ratio()

def phonetic_similarity(word1: str, word2: str) -> float:
    """
    Calcule une similarité phonétique simple
    Utile pour les erreurs phonétiques courantes
    """
    # Dictionnaire de remplacement pour les sons similaires
    replacements = {
        'a': 'a', 'e': 'a', 'é': 'a', 'è': 'a', 'ê': 'a',
        'i': 'i', 'y': 'i',
        'o': 'o', 'u': 'o',
        'k': 'q', 'c': 'q',
        'z': 's',
        'f': 'v',
        'b': 'p',
        't': 'd',
        'n': 'm'
    }

    # Simplifie les mots en remplaçant les caractères similaires
    def simplify(word: str) -> str:
        return ''.join(replacements.get(c, c) for c in word.lower())

    simple1 = simplify(word1)
    simple2 = simplify(word2)
    return sequence_similarity(simple1, simple2)

def calculate_brand_similarity(word: str, brand: str) -> Dict:
    """
    Calcule tous les scores de similarité entre un mot et une marque
    """
    lev_score = levenshtein_similarity(word, brand)
    seq_score = sequence_similarity(word, brand)
    phon_score = phonetic_similarity(word, brand)

    # Score composite (moyenne des trois scores)
    composite_score = (lev_score + seq_score + phon_score) / 3

    return {
        'found_word': word,
        'matched_brand': brand,
        'composite_score': round(composite_score, 3),
        'details': {
            'levenshtein_score': round(lev_score, 3),
            'sequence_score': round(seq_score, 3),
            'phonetic_score': round(phon_score, 3)
        }
    }

def find_similar_brands(text: str, brands: List[str], threshold: float = 0.7) -> List[Dict]:
    """
    Trouve toutes les marques similaires dans un texte

    Args:
        text: Texte à analyser
        brands: Liste des marques correctes
        threshold: Seuil minimum de similarité (0-1)
    """
    words = text.lower().split()
    matches = []

    for word in words:
        for brand in brands:
            similarity = calculate_brand_similarity(word, brand)
            if similarity['composite_score'] >= threshold:
                matches.append(similarity)

    return sorted(matches, key=lambda x: x['composite_score'], reverse=True)

def correct_brand_names(text: str, brands: List[str], threshold: float = 0.7) -> Tuple[str, List[Dict]]:
    """
    Corrige les noms de marques dans un texte

    Returns:
        (texte_corrigé, liste_corrections)
    """
    words = text.split()
    corrections = []

    for i, word in enumerate(words):
        matches = find_similar_brands(word, brands, threshold)
        if matches:
            best_match = matches[0]
            if best_match['composite_score'] >= threshold:
                original = words[i]
                words[i] = best_match['matched_brand']
                corrections.append({
                    'original': original,
                    'corrected': best_match['matched_brand'],
                    'position': i,
                    'scores': best_match
                })

    return ' '.join(words), corrections
