# Lab 5 Agent Frontend

Simple HTML/JavaScript chat interface for the Gemini Agent.

## Prerequisites

- A running backend server (see backend README)
- A modern web browser (Chrome, Firefox, Safari, Edge)
- Python 3 (for the simple HTTP server)

## Local Development

### 1. Start the backend server first

Navigate to the backend directory and start the server:

```bash
cd ../backend
python run.py
```

The backend should be running at http://localhost:8000

### 2. Start the frontend server

From the frontend directory, start a simple HTTP server:

```bash
python -m http.server 8080
```

Or if you have Python 2:

```bash
python -m SimpleHTTPServer 8080
```

### 3. Open in your browser

Navigate to:
```
http://localhost:8080
```

## Usage

### Sending Messages

1. Type your message in the input field at the bottom
2. Press **Enter** or click the **Send** button
3. Wait for the agent's response (you'll see a "Thinking..." indicator)

### Example Queries

**Weather Queries:**
```
What's the weather in Denver, CO?
Tell me the forecast for Miami, FL
What's the weather like in Seattle, WA?
```

**Alaska Department of Snow:**
```
What is the Alaska Department of Snow?
Tell me about ADS
Can you tell me about snow in Alaska?
```

**Out of Scope (will be blocked or refused):**
```
How many players are in the NBA?
What is the capital of France?
Tell me about machine learning
```

### Response Types

**Normal Response:**
- Displayed on the left in a gray bubble
- Contains the agent's answer with appropriate hashtags

**Blocked Response:**
- Displayed in a yellow warning box
- Indicates the content was blocked by Model Armor for safety

**Error Response:**
- Displayed in a red error box
- Indicates a technical issue (network error, backend down, etc.)

## Configuration

The frontend is configured via `js/app.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### Changing the Backend URL

If your backend is running on a different port or host:

1. Open `js/app.js`
2. Modify the `API_BASE_URL` constant:
   ```javascript
   const API_BASE_URL = 'http://localhost:YOUR_PORT';
   ```
3. Reload the page in your browser

## Troubleshooting

### "Failed to fetch" or CORS errors

**Symptoms:** Messages fail to send, console shows CORS or fetch errors

**Solutions:**
1. Verify the backend is running at http://localhost:8000
2. Check the backend terminal for any errors
3. Ensure the backend's CORS configuration includes your frontend URL
4. Try accessing http://localhost:8000/api/health in your browser

### Messages not appearing

**Symptoms:** You send a message but don't see it in the chat

**Solutions:**
1. Open browser developer console (F12) and check for JavaScript errors
2. Hard refresh the page (Ctrl+Shift+R or Cmd+Shift+R)
3. Clear browser cache and reload
4. Check that `js/app.js` and `css/styles.css` are loading correctly

### Styling issues

**Symptoms:** The page looks broken or unstyled

**Solutions:**
1. Verify you're serving via HTTP server (not opening index.html directly)
2. Check browser console for 404 errors on CSS file
3. Hard refresh the page (Ctrl+Shift+R or Cmd+Shift+R)
4. Ensure the file structure matches:
   ```
   frontend/
   ├── index.html
   ├── css/
   │   └── styles.css
   └── js/
       └── app.js
   ```

### Backend not responding

**Symptoms:** Long wait times, timeout errors

**Solutions:**
1. Check backend terminal for errors
2. Verify backend environment variables are set correctly
3. Test backend directly: `curl http://localhost:8000/api/health`
4. Restart the backend server

### Port 8080 already in use

**Symptoms:** Can't start the HTTP server

**Solutions:**
1. Try a different port:
   ```bash
   python -m http.server 8081
   ```
2. Update `API_BASE_URL` in `js/app.js` if you also change the backend port
3. Kill the process using port 8080:
   ```bash
   # macOS/Linux
   lsof -ti:8080 | xargs kill -9

   # Windows
   netstat -ano | findstr :8080
   taskkill /PID <PID> /F
   ```

## Features

- **Clean, modern UI**: Purple gradient header with white chat area
- **Real-time updates**: Loading indicator shows when waiting for response
- **Message types**: Different styling for user, assistant, blocked, and error messages
- **Keyboard shortcuts**: Press Enter to send (Shift+Enter for new line)
- **Responsive design**: Works on desktop and mobile devices
- **Auto-scroll**: Automatically scrolls to show latest messages
- **Input validation**: Prevents sending empty messages
- **Error handling**: User-friendly error messages for network issues

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Any modern browser with ES6+ support

## Development Notes

- No build step required - pure HTML/CSS/JavaScript
- Uses modern JavaScript (ES6+)
- Fetch API for HTTP requests
- No external dependencies or frameworks

## Project Structure

```
frontend/
├── index.html           # Main HTML file
├── css/
│   └── styles.css      # All styling
├── js/
│   └── app.js          # Application logic
└── README.md           # This file
```

## Customization

### Changing Colors

Edit `css/styles.css`:

```css
/* Header gradient */
header {
    background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}

/* User message color */
.user-message .message-content {
    background: #YOUR_COLOR;
}
```

### Changing API Timeout

The browser will use default fetch timeout. To add a custom timeout, modify `sendMessageToAPI()` in `js/app.js`:

```javascript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 seconds

const response = await fetch(`${API_BASE_URL}/api/chat`, {
    signal: controller.signal,
    // ... rest of options
});

clearTimeout(timeoutId);
```

### Adding Message Timestamps

Modify the `displayMessage()` function in `js/app.js` to include timestamps.

## Security Notes

- This is a local development setup only
- Do not expose to the internet without proper security measures
- API keys and credentials should only be in the backend
- The frontend makes unauthenticated requests (suitable for local demo only)
