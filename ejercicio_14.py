import os
import anthropic
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.embeddings.base import Embeddings

load_dotenv()

# ─── Embedding minimalista — sin dependencias extra ──────────────
class SimpleEmbedding(Embeddings):
    """Embedding basado en hash — para desarrollo sin costo adicional."""
    def embed_documents(self, texts):
        return [self._hash_embed(t) for t in texts]
    def embed_query(self, text):
        return self._hash_embed(text)
    def _hash_embed(self, text):
        import hashlib
        h = hashlib.md5(text.encode()).digest()
        return [b/255.0 for b in h]

# ─── Paso 1: Cargar documentos ───────────────────────────────────
print("Cargando documentos...")
loader = DirectoryLoader(
    "documentos/",
    glob="*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}
)
docs = loader.load()
print(f"✓ {len(docs)} documentos cargados")

# ─── Paso 2: Dividir en chunks ───────────────────────────────────
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " "]
)
chunks = splitter.split_documents(docs)
print(f"✓ {len(chunks)} chunks de {len(docs)} documentos")

# ─── Paso 3: Base vectorial ──────────────────────────────────────
print("Creando base vectorial...")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=SimpleEmbedding(),
    persist_directory="./chroma_db"
)
print("✓ Base vectorial creada en ./chroma_db")

# ─── Paso 4: Preguntas con RAG ───────────────────────────────────
cliente = anthropic.Anthropic()

def preguntar_con_rag(pregunta):
    print(f"\n{'='*60}")
    print(f"PREGUNTA: {pregunta}")

    # Recuperar chunks relevantes
    chunks_relevantes = vectorstore.similarity_search(pregunta, k=3)

    # Construir contexto
    contexto = "\n\n---\n\n".join([
        f"[Fuente: {os.path.basename(c.metadata.get('source','?'))}]\n{c.page_content}"
        for c in chunks_relevantes
    ])

    # Llamar a Claude con el contexto inyectado
    respuesta = cliente.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        temperature=0.1,
        system="""Eres el asistente farmaceutico de Farmacia Universal.
Responde UNICAMENTE basandote en las fichas tecnicas proporcionadas.
Si la informacion no esta en las fichas, indicalo explicitamente.
Cita siempre el nombre del medicamento fuente de tu respuesta.
Nunca recomiendes medicamentos para sintomas — solo informa sobre los consultados.
Responde en espanol de forma concisa y profesional.""",
        messages=[{
            "role": "user",
            "content": f"Fichas tecnicas disponibles:\n\n{contexto}\n\nPregunta: {pregunta}"
        }]
    )

    print(f"\nRESPUESTA:")
    print(respuesta.content[0].text)
    print(f"\nFuentes consultadas:")
    for c in chunks_relevantes:
        print(f"  └ {os.path.basename(c.metadata.get('source','?'))}")

# ─── Preguntas de prueba ─────────────────────────────────────────
preguntas = [
    "¿Cuál es la dosis máxima diaria de Metformina?",
    "¿Qué medicamentos NO se pueden tomar con Enalapril?",
    "¿La Atorvastatina se puede tomar con el estómago vacío?",
    "¿Qué efectos adversos graves debo conocer de estos tres medicamentos?",
]

for pregunta in preguntas:
    preguntar_con_rag(pregunta)