# 📸 Runtime Snapshot Debugger

A developer-friendly tool for capturing, debugging, and testing application state during development. Perfect for small teams and new developers who need better debugging capabilities.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install flask requests
   ```

2. **Run the debugger:**
   ```bash
   python app.py
   ```

3. **Open your browser:**
   ```
   http://localhost:5000
   ```

## 🎯 What This Tool Does

### For Small/New Developers:
- **🐛 Real-time Error Tracking** - See what's breaking and why
- **📊 Request Monitoring** - Track all API calls and responses
- **💡 Debugging Tips** - Get helpful suggestions when things go wrong
- **📸 State Snapshots** - Capture application state for later analysis
- **🧪 Auto Test Generation** - Create test cases from your snapshots
- **📈 Performance Insights** - Monitor error rates and uptime

### Key Features:
- **Debug Panel** - Live monitoring of errors, requests, and statistics
- **Snapshot Management** - Create, organize, and replay application states
- **Error Analysis** - Detailed error tracking with debugging tips
- **Test Generation** - Automatically create test files from snapshots
- **Export Capabilities** - Share logs and snapshots with team members

## 🛠️ How to Use

### 1. Debug Panel
The debug panel at the top shows:
- **Total Requests** - How many API calls have been made
- **Total Errors** - Number of errors encountered
- **Error Rate** - Percentage of requests that failed
- **Uptime** - How long the application has been running

### 2. Creating Snapshots
Snapshots capture the current state of your application:

**Manual Creation:**
- Click "➕ Create Snapshot"
- Fill in the form with your API details
- Add tags for organization
- Save the snapshot

**Programmatic Creation:**
```python
import requests

# Create a snapshot
response = requests.post("http://localhost:5000/snapshot/manual", json={
    "label": "User Login",
    "path": "/api/login",
    "tags": ["auth", "user"],
    "json": {"username": "john", "password": "secret"}
})
```

### 3. Error Tracking
The tool automatically tracks errors and provides debugging tips:

- **KeyError** → "Check if all required fields are present"
- **TypeError** → "Verify data types - check if you're passing the right types"
- **ValueError** → "Check input validation - ensure values are within expected ranges"
- **AttributeError** → "Check if the object has the method/attribute you're trying to use"

### 4. Testing and Validation
- **Replay Snapshots** - Test if your current code produces the same results
- **Set Expected Output** - Define what the correct response should be
- **Generate Tests** - Create Python test files automatically
- **Compare Results** - See differences between expected and actual output

## 📁 File Structure

```
Runtime Snapshot Debugger/
├── app.py                 # Main Flask application
├── static/
│   ├── index.html        # Web interface
│   └── style.css         # Styling
├── saved_snapshots/      # JSON files of captured snapshots
├── example_usage.py      # Example of how to use the tool
├── test.py              # Sample test file
└── README.md            # This file
```

## 🔧 API Endpoints

### Snapshot Management
- `GET /snapshots` - List all snapshots
- `POST /snapshot/manual` - Create manual snapshot
- `GET /snapshot/<id>` - Get specific snapshot
- `DELETE /snapshot/<id>` - Delete snapshot
- `POST /snapshot/<id>/replay` - Replay snapshot
- `POST /snapshot/<id>/expected` - Set expected output
- `GET /snapshot/<id>/generate-test` - Generate test file
- `GET /snapshot/<id>/export` - Export snapshot as JSON

### Debug Endpoints
- `GET /debug/stats` - Get debugging statistics
- `GET /debug/errors` - Get recent errors with tips
- `GET /debug/requests` - Get recent requests
- `POST /debug/clear-logs` - Clear all logs
- `GET /debug/export-logs` - Export all logs

## 💡 Best Practices for Small/New Developers

### 1. When to Create Snapshots
- **When you find a bug** - Capture the state before fixing it
- **When testing new features** - Save working states as baselines
- **When debugging complex issues** - Create snapshots at different points
- **When sharing issues** - Export snapshots to share with team members

### 2. Organizing Your Work
- **Use descriptive labels** - "User Login Success" vs "Test"
- **Add meaningful tags** - ["auth", "critical", "bug"] 
- **Set expected outputs** - Define what correct behavior looks like
- **Review error patterns** - Use the debug panel to spot trends

### 3. Debugging Workflow
1. **Monitor the debug panel** - Watch for errors and unusual patterns
2. **Create snapshots when issues occur** - Capture the problematic state
3. **Set expected outputs** - Define what should happen
4. **Fix the issue** - Make your code changes
5. **Replay snapshots** - Verify your fix works
6. **Generate tests** - Create automated tests for the future

### 4. Sharing and Collaboration
- **Export logs** when sharing issues with others
- **Use tags** to organize snapshots by feature or bug type
- **Set expected outputs** so others can understand the intended behavior
- **Generate test files** to help with automated testing

## 🚨 Common Scenarios

### Scenario 1: API Returns Unexpected Data
1. Create a snapshot when you notice the issue
2. Set the expected output to what should be returned
3. Fix your code
4. Replay the snapshot to verify the fix

### Scenario 2: Intermittent Errors
1. Monitor the debug panel for error patterns
2. Create snapshots when errors occur
3. Analyze the error tips for common causes
4. Use the error rate to gauge if your fixes are working

### Scenario 3: Testing New Features
1. Create snapshots of working functionality
2. Set expected outputs as regression tests
3. Make changes to your code
4. Replay snapshots to ensure nothing broke

## 🔍 Example Usage

Run the example file to see the tool in action:

```bash
python example_usage.py
```

This will:
- Create example snapshots for different scenarios
- Test the snapshots
- Show debug statistics
- Generate test files

## 🛠️ Troubleshooting

### Common Issues:

**"Could not connect to server"**
- Make sure `python app.py` is running
- Check that port 5000 is available

**"Invalid JSON" errors**
- Use a JSON validator to check your data
- Make sure all quotes and brackets are properly closed

**"Snapshot not found"**
- Check that the snapshot ID is correct
- Verify the snapshot file exists in `saved_snapshots/`

### Getting Help:
1. Check the debug panel for error details
2. Look at the debugging tips provided
3. Export logs to share with others
4. Use the error rate to identify problematic areas

## 🎯 Why This Tool Helps Small/New Developers

### Reduces Debugging Time
- **Visual error tracking** instead of console logs
- **Automatic debugging tips** for common issues
- **State capture** so you don't lose context

### Improves Code Quality
- **Regression testing** with snapshots
- **Expected output validation** 
- **Automatic test generation**

### Enhances Learning
- **Error patterns** help you understand common mistakes
- **Request monitoring** shows how your app behaves
- **Debugging tips** provide guidance for fixes

### Facilitates Collaboration
- **Export capabilities** for sharing issues
- **Tagged organization** for team coordination
- **Visual interface** that's easy to understand

## 📈 Next Steps

1. **Start using snapshots** for your current debugging needs
2. **Monitor the debug panel** to understand your app's behavior
3. **Set expected outputs** for critical functionality
4. **Generate tests** for important features
5. **Share snapshots** with team members when discussing issues

---

**Happy Debugging! 🐛✨** 