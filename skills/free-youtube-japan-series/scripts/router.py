#!/usr/bin/env python3
"""
LLM Router v1 — Free Model Proxy (Zero dependencies)
Chạy: python3 router.py
Test: curl http://localhost:8080/v1/chat/completions -d '{"model":"gemini-2.5-flash","messages":[{"role":"user","content":"Xin chào"}]}'
"""

import os, json, http.server, urllib.request, urllib.error, sys

PORT = int(os.getenv("PORT", "8080"))

# ── Free Models ──
MODELS = {
    "gemini-2.5-flash": {
        "provider": "gemini",
        "env_key": "GEMINI_API_KEY",
        "base": "https://generativelanguage.googleapis.com/v1beta/openai",
        "note": "Google Gemini 2.5 Flash — Free 60rpm"
    },
    "gemini-2.0-flash": {
        "provider": "gemini",
        "env_key": "GEMINI_API_KEY",
        "base": "https://generativelanguage.googleapis.com/v1beta/openai",
        "note": "Google Gemini 2.0 Flash — Free"
    },
    "llama-3.3-70b": {
        "provider": "groq",
        "env_key": "GROQ_API_KEY",
        "base": "https://api.groq.com/openai/v1",
        "note": "Groq Llama 3.3 70B — Free 30rpm"
    },
    "mixtral-8x7b": {
        "provider": "groq",
        "env_key": "GROQ_API_KEY",
        "base": "https://api.groq.com/openai/v1",
        "note": "Groq Mixtral 8x7B — Free"
    },
    "llama-3.1-8b": {
        "provider": "groq",
        "env_key": "GROQ_API_KEY",
        "base": "https://api.groq.com/openai/v1",
        "note": "Groq Llama 3.1 8B — Free, siêu nhanh"
    },
    "deepseek-chat": {
        "provider": "deepseek",
        "env_key": "DEEPSEEK_API_KEY",
        "base": "https://api.deepseek.com/v1",
        "note": "DeepSeek V3 — $0.14/M tokens"
    },
}

def find_best_model(wanted=None):
    """Find model by name or pick best available."""
    if wanted and wanted in MODELS:
        info = MODELS[wanted]
        if os.getenv(info["env_key"]):
            return wanted, info
    # Fallback: first available
    for mid, info in MODELS.items():
        if os.getenv(info["env_key"]):
            return mid, info
    return None, None

def call_provider(model_id, info, body):
    """Call a provider and return JSON response."""
    key = os.getenv(info["env_key"])
    base = info["base"].rstrip("/")
    
    body["model"] = model_id
    data = json.dumps(body).encode()
    
    if info["provider"] == "gemini":
        # Gemini: dùng REST API trực tiếp (OpenAI compat có vấn đề)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={key}"
        # Chuyển từ OpenAI format sang Gemini format
        gemini_contents = []
        for msg in body.get("messages", []):
            gemini_contents.append({"role": msg["role"], "parts": [{"text": msg["content"]}]})
        # Map roles: system → user (Gemini không support system role free tier)
        gemini_data = {"contents": gemini_contents}
        data = json.dumps(gemini_data).encode()
        headers = {"Content-Type": "application/json"}
    else:
        # Standard OpenAI-compatible
        url = f"{base}/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    
    req = urllib.request.Request(url, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read())
            # Convert Gemini response to OpenAI format
            if info["provider"] == "gemini":
                text = ""
                if "candidates" in raw and raw["candidates"]:
                    parts = raw["candidates"][0].get("content", {}).get("parts", [])
                    text = " ".join(p.get("text", "") for p in parts)
                return {
                    "id": f"chatcmpl-{model_id}",
                    "object": "chat.completion",
                    "choices": [{"index": 0, "message": {"role": "assistant", "content": text},
                                 "finish_reason": "stop"}],
                    "usage": raw.get("usageMetadata", {})
                }
            return raw
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimitError(f"{model_id}: rate limited")
        err_body = e.read().decode()[:200]
        raise ProviderError(f"{model_id}: HTTP {e.code} — {err_body}")
    except Exception as e:
        raise ProviderError(f"{model_id}: {str(e)[:200]}")

class RateLimitError(Exception): pass
class ProviderError(Exception): pass

class RouterHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        sys.stderr.write(f"[LLM-Router] {args[0]} {args[1]} {args[2]}\n")
    
    def _send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    
    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length > 0:
            return json.loads(self.rfile.read(length))
        return {}
    
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
    
    def do_GET(self):
        if self.path == "/v1/models":
            models = [{"id": mid, "object": "model", "owned_by": info["provider"], "note": info["note"]}
                      for mid, info in MODELS.items()]
            self._send_json({"object": "list", "data": models})
        elif self.path == "/health":
            keys = {}
            for info in MODELS.values():
                p = info["provider"]
                if p not in keys:
                    keys[p] = "✅" if os.getenv(info["env_key"]) else "❌"
            self._send_json({"status": "ok", "api_keys": keys, "models": len(MODELS)})
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self._send_json({"error": "Not found"}, 404)
            return
        
        try:
            body = self._read_body()
        except Exception as e:
            self._send_json({"error": f"Invalid JSON: {e}"}, 400)
            return
        
        wanted = body.get("model", "")
        
        # Try models with fallback
        last_error = None
        tried = []
        
        # Try wanted model first
        mid, info = find_best_model(wanted)
        if mid:
            tried.append(mid)
            try:
                result = call_provider(mid, info, body)
                self._send_json(result)
                return
            except (RateLimitError, ProviderError) as e:
                last_error = str(e)
                print(f"  ⚠️ {mid} failed: {e}")
        
        # Fallback: try all other models
        for mid, info in MODELS.items():
            if mid in tried: continue
            if not os.getenv(info["env_key"]): continue
            tried.append(mid)
            try:
                result = call_provider(mid, info, body)
                print(f"  ✅ Fallback to {mid}")
                self._send_json(result)
                return
            except (RateLimitError, ProviderError) as e:
                last_error = str(e)
                print(f"  ⚠️ {mid} failed: {e}")
        
        self._send_json({"error": f"All providers exhausted. Last: {last_error}"}, 503)

def main():
    print("🚀 LLM Router — Free Model Proxy")
    print(f"   Port: {PORT}")
    print(f"   Endpoint: http://localhost:{PORT}/v1/chat/completions")
    print()
    print("   Available models:")
    for mid, info in MODELS.items():
        key = os.getenv(info["env_key"])
        status = "✅" if key else "❌"
        print(f"   {status} {mid:25s} — {info['note']}")
    print()
    print(f"   Health: http://localhost:{PORT}/health")
    
    server = http.server.HTTPServer(("0.0.0.0", PORT), RouterHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()
