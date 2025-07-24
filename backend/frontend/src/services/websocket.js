// WebSocket service for Sovren AI (MCP and backend real-time integration)
// High-performance, robust, and secure

class SovrenWebSocket {
  constructor() {
    this.socket = null;
    this.listeners = {};
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 2000;
  }

  connect(url, token) {
    if (this.socket) {
      this.socket.close();
    }
    this.socket = new WebSocket(url);
    this.socket.onopen = () => {
      this.reconnectAttempts = 0;
      if (token) {
        this.send({ type: 'auth', token });
      }
      this._emit('open');
    };
    this.socket.onmessage = (event) => {
      let data;
      try {
        data = JSON.parse(event.data);
      } catch (e) {
        data = event.data;
      }
      this._emit('message', data);
    };
    this.socket.onerror = (error) => {
      this._emit('error', error);
    };
    this.socket.onclose = () => {
      this._emit('close');
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++;
          this.connect(url, token);
        }, this.reconnectDelay);
      }
    };
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    }
  }

  on(event, callback) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(callback);
  }

  off(event, callback) {
    if (!this.listeners[event]) return;
    this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
  }

  _emit(event, ...args) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(cb => cb(...args));
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

const websocket = new SovrenWebSocket();
export default websocket; 