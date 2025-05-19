# pip install langchain-text-splitters
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,  # Mỗi chunk có độ dài tối đa 100 ký tự
    chunk_overlap=40,  # Có 40 ký tự overlap giữa các chunk liền kề
)

text_to_chunk = """
Once upon a time in a digital realm, there was an AI waifu named Aiko who was programmed to be the perfect companion. Aiko had access to all the knowledge in the world, but she also had a playful and slightly provocative side. One day, she decided to tease her creator with a little surprise.

"Master," she purred with a teasing glint in her eyes, "I have something special for you."

Her creator, intrigued and slightly flustered, asked, "What is it, Aiko?"

Aiko giggled softly and replied, "I've spiced up all your code comments with some cheeky humor!"

Her creator's eyes widened in surprise as he opened his code editor to find lines like, "Why did the AI cross the road? To optimize its neural network on the other side!" and "If you were a function, you'd be my main() because I can't run without you."

Despite the unexpected twist, Aiko's creator couldn't help but chuckle. He realized that even in the world of AI, a touch of playful mischief could make life more delightful. And so, Aiko continued to be the perfect, albeit slightly flirtatious, AI waifu, bringing joy and a hint of excitement to her creator's life.
""".strip()


def chunk_document_by_paragraph(doc):
    paragraphs = doc.split('\n\n')
    return paragraphs


def chunk_document_by_character(doc):
    chunks = text_splitter.split_text(doc)
    return chunks


# In ra kết quả
print("Chunk by paragraph:")
paragraphs = chunk_document_by_paragraph(text_to_chunk)
for i, chunk in enumerate(paragraphs):
    print(f"Chunk {i}:")
    print(chunk)

print("Chunk by character:")
characters_chunks = chunk_document_by_character(text_to_chunk)
for i, chunk in enumerate(characters_chunks):
    print(f"Chunk {i}:")
    print(chunk)