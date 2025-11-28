from fastapi import APIRouter, UploadFile, File, Form
import numpy as np
import cv2
from keras_facenet import FaceNet
from mtcnn import MTCNN
import os
import pickle
from scipy.spatial.distance import cosine

router = APIRouter(prefix="/face", tags=["Face Recognition"])

# Inisialisasi FaceNet dan MTCNN
embedder = FaceNet()   
detector = MTCNN()

# Folder untuk menyimpan embedding (relatif ke Backend_api)
EMBEDDINGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "embeddings")
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

# Threshold cosine similarity
THRESHOLD = 0.4

# ========================
# Endpoint registrasi wajah
# ========================

@router.post("/register")
async def register_face(file: UploadFile = File(...), username: str = Form(...)):
    """
    Registrasi wajah baru untuk face recognition
    """
    try:
        # Baca file gambar
        image_bytes = await file.read()
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Deteksi wajah
        faces = detector.detect_faces(img)
        if len(faces) == 0:
            return {"status": "error", "message": "Wajah tidak terdeteksi"}

        # Ambil wajah pertama
        x, y, w, h = faces[0]['box']
        face_crop = img[y:y+h, x:x+w]

        # Buat embedding
        embedding = embedder.embeddings([face_crop])[0]

        # Simpan embedding ke file
        embedding_path = os.path.join(EMBEDDINGS_DIR, f"{username}.pkl")
        with open(embedding_path, "wb") as f:
            pickle.dump(embedding, f)

        return {"status": "success", "message": f"Wajah {username} terdaftar"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ========================
# Endpoint face recognition
# ========================

@router.post("/recognize")
async def recognize_face(file: UploadFile = File(...)):
    """
    Mengenali wajah dari gambar yang diupload
    """
    try:
        # Baca file gambar
        image_bytes = await file.read()
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Deteksi wajah
        faces = detector.detect_faces(img)
        if len(faces) == 0:
            return {"status": "error", "message": "Wajah tidak terdeteksi"}

        x, y, w, h = faces[0]['box']
        face_crop = img[y:y+h, x:x+w]
        embedding_new = embedder.embeddings([face_crop])[0]

        # Bandingkan dengan semua embedding yang tersimpan
        results = []
        if os.path.exists(EMBEDDINGS_DIR):
            for file_name in os.listdir(EMBEDDINGS_DIR):
                if file_name.endswith('.pkl'):
                    with open(os.path.join(EMBEDDINGS_DIR, file_name), "rb") as f:
                        embedding_registered = pickle.load(f)
                    distance = cosine(embedding_registered, embedding_new)
                    if distance < THRESHOLD:
                        results.append({
                            "username": file_name.replace(".pkl", ""), 
                            "distance": float(distance),
                            "confidence": float(1 - distance)
                        })

        # Sort by distance (lowest = best match)
        results.sort(key=lambda x: x['distance'])

        if results:
            return {"status": "success", "recognized": results}
        else:
            return {"status": "success", "recognized": None, "message": "Wajah tidak dikenali"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ========================
# Endpoint list registered faces
# ========================

@router.get("/registered")
async def list_registered_faces():
    """
    Melihat daftar wajah yang sudah terdaftar
    """
    try:
        if not os.path.exists(EMBEDDINGS_DIR):
            return {"status": "success", "registered": []}
        
        registered = []
        for file_name in os.listdir(EMBEDDINGS_DIR):
            if file_name.endswith('.pkl'):
                registered.append(file_name.replace(".pkl", ""))
        
        return {"status": "success", "registered": registered, "count": len(registered)}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ========================
# Endpoint delete registered face
# ========================

@router.delete("/register/{username}")
async def delete_registered_face(username: str):
    """
    Menghapus registrasi wajah
    """
    try:
        embedding_path = os.path.join(EMBEDDINGS_DIR, f"{username}.pkl")
        
        if not os.path.exists(embedding_path):
            return {"status": "error", "message": f"Wajah {username} tidak ditemukan"}
        
        os.remove(embedding_path)
        return {"status": "success", "message": f"Wajah {username} berhasil dihapus"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
