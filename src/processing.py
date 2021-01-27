import binascii
import re
from types import prepare_class

# List of stopwords comes from the "nltk" package
STOPWORDS = ["ourselves", "hers", "between", "yourself", "but", "again", "there", "about", "once", "during", "out", "very", "having", "with", "they", "own", "an", "be", "some", "for", "do", "its", "yours", "such", "into", "of", "most", "itself", "other", "off", "is", "s", "am", "or", "who", "as", "from", "him", "each", "the", "themselves", "until", "below", "are", "we", "these", "your", "his", "through", "don", "nor", "me", "were", "her", "more", "himself", "this", "down", "should", "our", "their", "while",
             "above", "both", "up", "to", "ours", "had", "she", "all", "no", "when", "at", "any", "before", "them", "same", "and", "been", "have", "in", "will", "on", "does", "yourselves", "then", "that", "because", "what", "over", "why", "so", "can", "did", "not", "now", "under", "he", "you", "herself", "has", "just", "where", "too", "only", "myself", "which", "those", "i", "after", "few", "whom", "t", "being", "if", "theirs", "my", "against", "a", "by", "doing", "it", "how", "further", "was", "here", "than"]
# Regex for matching reference: https://stackoverflow.com/questions/19560498/faster-way-to-remove-stop-words-in-python
STOPWORDS_REGEX = re.compile(r"\b(" + r"|".join(STOPWORDS) + r")\b\s*")
# Matches everything that is not whitespace or alphanumerical
PUNCTUATION_REGEX = re.compile(r"[^\w\s]")


# stopword removal, capitalization removal, punctuation removal
def pre_processing(doc: str, **kwargs) -> str:
    if kwargs.get("capitalization"):
        doc = doc.lower()

    if kwargs.get('punctuation'):
        doc = re.sub(PUNCTUATION_REGEX, "", doc)

    if kwargs.get('stopwords'):
        doc = re.sub(STOPWORDS_REGEX, "", doc)

    return doc


# combine two CRC32s to create a 64-bit result (no built-in CRC64 but this should suffice)
def longcrc(shingle):
    bytestr = str.encode(" ".join(shingle))
    shingle.reverse()
    bytestr2 = str.encode(" ".join(shingle))
    lower = binascii.crc32(bytestr) % (1 << 32)
    upper = binascii.crc32(bytestr2) % (1 << 32)
    return lower | (upper << 32)


# turns a document into a set of hashed shingles
def to_shingles(doc, k=3):
    shingles = set()
    # doc = pre_processing(doc, punctuation=True, stopwords=True, capitalization=True)
    doc = doc.split()
    for i in range(0, len(doc)-k+1):
        # shingles.add(hash(tuple(doc[i:i+k])))
        # if doc[i] in STOPWORDS:
        shingles.add(longcrc(doc[i:i+k]))
    return shingles


if __name__ == "__main__":
    teststring = "ThiS IS A test StR.Ing,, 5589.48q,"
    print(pre_processing(teststring, punctuation=True,
                         stopwords=True, capitalization=True))
