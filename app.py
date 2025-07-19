import os
import json
import time
import uuid
import traceback
import sys
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, make_response

app = Flask(__name__)
snapshots = {}
SNAPSHOT_DIR = "saved_snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

# Global error tracking
error_log = []
request_log = []

def log_error(error, context=None):
    """Log errors with context for debugging"""
    error_entry = {
        "timestamp": time.time(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        "context": context or {},
        "request_path": request.path if request else None,
        "request_method": request.method if request else None
    }
    error_log.append(error_entry)
    return error_entry

def log_request():
    """Log request details for debugging"""
    request_entry = {
        "timestamp": time.time(),
        "path": request.path,
        "method": request.method,
        "headers": dict(request.headers),
        "args": request.args.to_dict(),
        "form": request.form.to_dict(),
        "json": request.get_json(silent=True),
        "ip": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', '')
    }
    request_log.append(request_entry)
    return request_entry

def get_environment_info():
    """Capture environment variables and system info"""
    env_vars = {}
    # Only capture non-sensitive environment variables
    safe_vars = ['PATH', 'PYTHONPATH', 'FLASK_ENV', 'FLASK_DEBUG', 'DATABASE_URL', 'REDIS_URL']
    for var in safe_vars:
        if var in os.environ:
            env_vars[var] = os.environ[var]
    
    return {
        "python_version": sys.version,
        "platform": sys.platform,
        "environment_variables": env_vars,
        "working_directory": os.getcwd()
    }

def snapshot(label, extra_data=None, tags=None):
    snap_id = str(uuid.uuid4())
    
    # Capture current request details
    current_request = log_request()
    
    snap = {
        "id": snap_id,
        "timestamp": time.time(),
        "label": label,
        "tags": tags or [],
        "expected_output": None,
        "request": current_request,
        "env": get_environment_info(),
        "memory": extra_data or {},
        "logs": [],
        "errors": [e for e in error_log[-10:]],  # Last 10 errors
        "debug_info": {
            "total_requests": len(request_log),
            "total_errors": len(error_log),
            "session_duration": time.time() - (request_log[0]["timestamp"] if request_log else time.time())
        }
    }

    snapshots[snap_id] = snap
    with open(os.path.join(SNAPSHOT_DIR, f"{snap_id}.json"), "w") as f:
        json.dump(snap, f, indent=2)
    return snap_id

def load_snapshot(snap_id):
    if snap_id in snapshots:
        return snapshots[snap_id]
    path = os.path.join(SNAPSHOT_DIR, f"{snap_id}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            snapshots[snap_id] = data
            return data
    return None

@app.route('/snapshot/<snap_id>/expected', methods=['POST'])
def set_expected_output(snap_id):
    snap = load_snapshot(snap_id)
    if not snap:
        return jsonify({"error": "Snapshot not found"}), 404
    data = request.get_json()
    snap["expected_output"] = data.get("expected_output")
    with open(os.path.join(SNAPSHOT_DIR, f"{snap_id}.json"), "w") as f:
        json.dump(snap, f, indent=2)
    return jsonify({"message": "Expected output saved."})

@app.route('/snapshot/<snap_id>/replay', methods=['POST'])
def replay_snapshot(snap_id):
    snap = load_snapshot(snap_id)
    if not snap:
        return jsonify({"error": "Snapshot not found"}), 404
    req_json = snap['request'].get('json', {})
    amount = req_json.get("amount")
    user_id = req_json.get("user_id")
    replay_state = {
        "amount": amount,
        "user_id": user_id,
        "status": "replayed"
    }

    match = snap.get("expected_output") == replay_state

    return jsonify({
        "message": "Replayed payment logic",
        "replayed_state": replay_state,
        "expected_output": snap.get("expected_output"),
        "match": match
    })

@app.route('/snapshot/<snap_id>/generate-test', methods=['GET'])
def generate_test_case(snap_id):
    snap = load_snapshot(snap_id)
    if not snap:
        return jsonify({"error": "Snapshot not found"}), 404

    route = snap['request']['path']
    body = json.dumps(snap['request'].get('json', {}), indent=2)
    expected = json.dumps(snap.get("expected_output", {}), indent=2)

    test_code = f'''import requests

def test_snapshot_replay():
    url = "http://localhost:5000{route}"
    headers = {{"Content-Type": "application/json"}}
    payload = {body}

    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 200
    expected = {expected}
    assert response.json().get("replayed_state") == expected
    print("✅ Test passed!")
'''

    response = make_response(test_code)
    response.headers.set('Content-Type', 'text/x-python')
    response.headers.set('Content-Disposition', f'attachment; filename=test_snapshot_{snap_id}.py')
    return response

@app.route('/snapshots', methods=['GET'])
def list_snapshots():
    snapshot_list = []
    for filename in os.listdir(SNAPSHOT_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(SNAPSHOT_DIR, filename)
            with open(filepath, "r") as f:
                data = json.load(f)
                snapshot_list.append({
                    "id": data["id"],
                    "timestamp": data["timestamp"],
                    "label": data.get("label", ""),
                    "tags": data.get("tags", []),
                    "path": data["request"].get("path", ""),
                    "has_errors": len(data.get("errors", [])) > 0,
                    "error_count": len(data.get("errors", []))
                })
    return jsonify(snapshot_list)

@app.route('/snapshot/manual', methods=['POST'])
def create_manual_snapshot():
    data = request.get_json()
    label = data.get('label', 'manual')
    path = data.get('path', '/manual')
    json_body = data.get('json', {})
    tags = data.get('tags', [])

    request_data = {
        "path": path,
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "args": {},
        "form": {},
        "json": json_body
    }

    snap_id = str(uuid.uuid4())
    snap = {
        "id": snap_id,
        "timestamp": time.time(),
        "label": label,
        "tags": tags,
        "expected_output": None,
        "request": request_data,
        "env": get_environment_info(),
        "memory": {},
        "logs": [],
        "errors": [e for e in error_log[-10:]],
        "debug_info": {
            "total_requests": len(request_log),
            "total_errors": len(error_log),
            "session_duration": time.time() - (request_log[0]["timestamp"] if request_log else time.time())
        }
    }

    snapshots[snap_id] = snap
    with open(os.path.join(SNAPSHOT_DIR, f"{snap_id}.json"), "w") as f:
        json.dump(snap, f, indent=2)

    return jsonify({"message": "Manual snapshot created", "snapshot_id": snap_id})

@app.route('/snapshot/<snap_id>', methods=['GET'])
def get_snapshot(snap_id):
    snap = load_snapshot(snap_id)
    if not snap:
        return jsonify({"error": "Snapshot not found"}), 404
    return jsonify(snap)

@app.route('/snapshot/<snap_id>/export', methods=['GET'])
def export_snapshot(snap_id):
    file_path = os.path.join(SNAPSHOT_DIR, f"{snap_id}.json")
    if not os.path.exists(file_path):
        return jsonify({"error": "Snapshot not found"}), 404
    with open(file_path, 'rb') as f:
        response = make_response(f.read())
        response.headers.set('Content-Type', 'application/json')
        response.headers.set('Content-Disposition', f'attachment; filename={snap_id}.json')
        return response

@app.route('/snapshot/<snap_id>', methods=['DELETE'])
def delete_snapshot(snap_id):
    path = os.path.join(SNAPSHOT_DIR, f"{snap_id}.json")
    if os.path.exists(path):
        os.remove(path)
        snapshots.pop(snap_id, None)
        return jsonify({"message": "Snapshot deleted"})
    return jsonify({"error": "Snapshot not found"}), 404

@app.route('/snapshot/<snap_id>/tag', methods=['POST'])
def update_snapshot_tags(snap_id):
    snap = load_snapshot(snap_id)
    if not snap:
        return jsonify({"error": "Snapshot not found"}), 404
    data = request.get_json()
    new_tags = data.get("tags", [])
    snap["tags"] = list(set(snap.get("tags", []) + new_tags))
    with open(os.path.join(SNAPSHOT_DIR, f"{snap_id}.json"), "w") as f:
        json.dump(snap, f, indent=2)
    snapshots[snap_id] = snap
    return jsonify({"message": "Tags updated", "tags": snap["tags"]})

# New developer-friendly endpoints
@app.route('/debug/errors', methods=['GET'])
def get_errors():
    """Get recent errors with debugging tips"""
    recent_errors = error_log[-20:]  # Last 20 errors
    for error in recent_errors:
        # Add debugging tips based on error type
        error_type = error.get("error_type", "")
        if "KeyError" in error_type:
            error["debug_tip"] = "Check if all required fields are present in your request"
        elif "TypeError" in error_type:
            error["debug_tip"] = "Verify data types - check if you're passing the right types"
        elif "ValueError" in error_type:
            error["debug_tip"] = "Check input validation - ensure values are within expected ranges"
        elif "AttributeError" in error_type:
            error["debug_tip"] = "Check if the object has the method/attribute you're trying to use"
        else:
            error["debug_tip"] = "Review the traceback and check your code logic"
    
    return jsonify({
        "errors": recent_errors,
        "total_errors": len(error_log),
        "error_rate": len(error_log) / max(len(request_log), 1) * 100
    })

@app.route('/debug/requests', methods=['GET'])
def get_requests():
    """Get recent requests for debugging"""
    return jsonify({
        "requests": request_log[-20:],
        "total_requests": len(request_log)
    })

@app.route('/debug/stats', methods=['GET'])
def get_debug_stats():
    """Get debugging statistics"""
    return jsonify({
        "total_snapshots": len(snapshots),
        "total_errors": len(error_log),
        "total_requests": len(request_log),
        "error_rate": len(error_log) / max(len(request_log), 1) * 100,
        "uptime": time.time() - (request_log[0]["timestamp"] if request_log else time.time()),
        "most_common_errors": get_most_common_errors(),
        "most_common_paths": get_most_common_paths()
    })

def get_most_common_errors():
    """Get most common error types"""
    error_types = {}
    for error in error_log:
        error_type = error.get("error_type", "Unknown")
        error_types[error_type] = error_types.get(error_type, 0) + 1
    return sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]

def get_most_common_paths():
    """Get most common request paths"""
    paths = {}
    for req in request_log:
        path = req.get("path", "Unknown")
        paths[path] = paths.get(path, 0) + 1
    return sorted(paths.items(), key=lambda x: x[1], reverse=True)[:5]

@app.route('/debug/clear-logs', methods=['POST'])
def clear_logs():
    """Clear error and request logs"""
    global error_log, request_log
    error_log = []
    request_log = []
    return jsonify({"message": "Logs cleared"})

@app.route('/debug/export-logs', methods=['GET'])
def export_logs():
    """Export all logs for analysis"""
    logs_data = {
        "errors": error_log,
        "requests": request_log,
        "export_timestamp": time.time()
    }
    response = make_response(json.dumps(logs_data, indent=2))
    response.headers.set('Content-Type', 'application/json')
    response.headers.set('Content-Disposition', f'attachment; filename=debug_logs_{int(time.time())}.json')
    return response

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
