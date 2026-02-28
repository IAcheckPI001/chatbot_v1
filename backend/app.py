
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from openai import OpenAI

from dotenv import load_dotenv
import os
from utils import normalize_text, classify
from corn import supabase

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


@app.route('/api/get-chunks', methods=['GET'])
def get_chunks():
    try:
        response = supabase.table("documents") \
            .select("id, procedure_name, text_content, category, subject, is_active, effective_date") \
            .execute()

        if not response.data:
            return jsonify({
                "chunks": [],
                "message": "No chunks available"
            }), 200

        return jsonify({
            "chunks": response.data
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route('/api/get-alias', methods=['GET'])
def get_alias():
    try:
        response = supabase.table("alias") \
            .select("id, document_id, alias_text, normalized_alias") \
            .execute()

        if not response.data:
            return jsonify({
                "alias": [],
                "message": "No alias available"
            }), 200

        return jsonify({
            "alias": response.data
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/create-alias', methods=['POST'])
def create_alias():
    try:
        data = request.json

        # Validate cơ bản
        if not data.get("alias_text"):
            return jsonify({"error": "alias_text is required"}), 400
        
        alias_embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=data.get("alias_text")
        ).data[0].embedding


        new_alias = {
            "document_id": data.get("document_id") or None,
            "alias_text": data.get("alias_text") or '',
            "normalized_alias": normalize_text(data.get("alias_text")) if data.get("alias_text") else '',
            "embedding": alias_embedding
        }

        response = supabase.table("alias") \
            .insert(new_alias) \
            .execute()

        return jsonify({
            "message": "Alias created successfully",
            "data": response.data
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete-alias/<alias_id>', methods=['DELETE'])
def delete_alias(alias_id):
    try:
        response = supabase.table("alias") \
            .delete() \
            .eq("id", alias_id) \
            .execute()

        if not response.data:
            return jsonify({"error": "Alias not found"}), 404

        return jsonify({
            "message": "Alias deleted successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-chunk/<chunk_id>', methods=['PUT'])
def update_chunk(chunk_id):
    try:
        data = request.json

        category = data.get("category")
        text_content = data.get("text_content")

        if category == "thong_tin_phuong":
            normalized_text = normalize_text(text_content)

        response = supabase.table("documents") \
            .update({
                "text_content": data.get("text_content"),
                "normalized_text": normalized_text,
                "category": data.get("category") or None,
                "subject": data.get("subject") or None
            }) \
            .eq("id", chunk_id) \
            .execute()
        
        if not response.data:
            return jsonify({"error": "Chunk not found"}), 404

        return jsonify({
            "message": "Chunk updated successfully",
            "data": response.data
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route('/api/update-alias/<alias_id>', methods=['PUT'])
def update_alias(alias_id):
    try:
        data = request.json

        alias_embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=data.get("alias_text")
        ).data[0].embedding

        response = supabase.table("alias") \
            .update({
                "document_id": data.get("document_id") or None,
                "alias_text": data.get("alias_text") or '',
                "normalized_alias": normalize_text(data.get("alias_text")) or '',
                "embedding": alias_embedding
            }) \
            .eq("id", alias_id) \
            .execute()
        
        if not response.data:
            return jsonify({"error": "Alias not found"}), 404

        return jsonify({
            "message": "Alias updated successfully",
            "data": response.data
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

from flask import Response
import json

@app.route('/api/chat-stream', methods=['POST'])
def chat_stream():

    # ✅ LẤY DATA TRƯỚC
    data = request.json
    user_message = data.get('message', '').strip()

    def generate():

        yield f"data: {json.dumps({'log': f'Nhận message...'})}\n\n"

        q_format = normalize_text(user_message)
        yield f"data: {json.dumps({'log': f'Normalized: {q_format}'})}\n\n"

        category, subject = classify(q_format)
        yield f"data: {json.dumps({'log': f'Category: {category}, Subject: {subject}'})}\n\n"

        query_embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=user_message
        ).data[0].embedding

        response = supabase.rpc(
            "search_documents_full_hybrid_v4",
            {
                "p_query_format": q_format,
                "p_query_embedding": query_embedding,
                "p_tenant": "xa_ba_diem",
                "p_category": category,
                "p_subject": subject,
                "p_limit": 5
            }
        ).execute()

        yield f"data: {json.dumps({'replies': response.data})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Receive user message and return relevant responses
    Request: {"message": "user message"}
    Response: {"replies": [{"content": "...", "score": 0.95}, ...]}
    """
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    q_format = normalize_text(user_message)
    category, subject = classify(q_format)
    print(f"Query: {q_format}\n=> Category: {category}, Subject: {subject}\n")

    log_data = f"""Query: {user_message}\n=> Category: {category}, Subject: {subject}"""

    query_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=user_message
    ).data[0].embedding

    response = supabase.rpc(
        "search_documents_full_hybrid_v4",
        {
            "p_query_format": q_format,
            "p_query_embedding": query_embedding,
            "p_tenant": "xa_ba_diem",
            "p_category": category,
            "p_subject": subject,
            "p_limit": 5
        }
    ).execute()

    # Return all responses from knowledge base (you can add better matching logic here)
    return jsonify({
        "replies": response.data,
        "message": user_message,
        "log_data":log_data,
        "timestamp": datetime.now().isoformat()
    })



@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True)

