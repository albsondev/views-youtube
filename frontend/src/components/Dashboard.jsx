import { useState, useEffect } from 'react';
import { api } from '../services/api';
import './Dashboard.css';

export default function Dashboard() {
    const [status, setStatus] = useState(null);
    const [activities, setActivities] = useState([]);
    const [config, setConfig] = useState({
        channel_url: '',
        video_limit: 5,
        should_subscribe: true,
        should_like: true,
        should_comment: true
    });
    const [credentials, setCredentials] = useState({ email: '', password: '' });
    const [showLogin, setShowLogin] = useState(false);

    useEffect(() => {
        loadStatus();
        loadActivities();

        const interval = setInterval(() => {
            loadStatus();
            loadActivities();
        }, 3000);

        return () => clearInterval(interval);
    }, []);

    const loadStatus = async () => {
        try {
            const data = await api.getStatus();
            setStatus(data);
        } catch (error) {
            console.error('Failed to load status:', error);
        }
    };

    const loadActivities = async () => {
        try {
            const data = await api.getActivities(30);
            setActivities(data.activities || []);
        } catch (error) {
            console.error('Failed to load activities:', error);
        }
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            await api.login(credentials.email, credentials.password);
            setShowLogin(false);
            setCredentials({ email: '', password: '' });
            loadStatus();
        } catch (error) {
            alert('Login failed: ' + error.message);
        }
    };

    const handleStart = async () => {
        try {
            await api.startAutomation(config);
            loadStatus();
        } catch (error) {
            alert('Failed to start: ' + error.message);
        }
    };

    const handleStop = async () => {
        try {
            await api.stopAutomation();
            loadStatus();
        } catch (error) {
            alert('Failed to stop: ' + error.message);
        }
    };

    const handleClearLogs = async () => {
        try {
            await api.clearActivities();
            setActivities([]);
        } catch (error) {
            alert('Failed to clear logs: ' + error.message);
        }
    };

    const getStatusColor = () => {
        if (!status) return 'gray';
        if (status.is_running) return 'green';
        if (status.status === 'error') return 'red';
        return 'blue';
    };

    return (
        <div className="dashboard">
            <header className="header">
                <h1>🤖 YouTube Automation Agent</h1>
                <div className="status-badge" style={{ backgroundColor: getStatusColor() }}>
                    {status?.status || 'loading'}
                </div>
            </header>

            <div className="grid">
                <div className="card">
                    <h2>📊 Status</h2>
                    <div className="status-info">
                        <div className="info-row">
                            <span>Logged In:</span>
                            <strong>{status?.is_logged_in ? '✅ Yes' : '❌ No'}</strong>
                        </div>
                        <div className="info-row">
                            <span>Running:</span>
                            <strong>{status?.is_running ? '🟢 Active' : '⚪ Idle'}</strong>
                        </div>
                        <div className="info-row">
                            <span>Current Task:</span>
                            <strong>{status?.current_task || 'None'}</strong>
                        </div>
                    </div>

                    {!status?.is_logged_in && !showLogin && (
                        <button className="btn btn-primary" onClick={() => setShowLogin(true)}>
                            🔐 Login to Google
                        </button>
                    )}

                    {showLogin && (
                        <form onSubmit={handleLogin} className="login-form">
                            <input
                                type="email"
                                placeholder="Email"
                                value={credentials.email}
                                onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
                                required
                            />
                            <input
                                type="password"
                                placeholder="Password"
                                value={credentials.password}
                                onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                                required
                            />
                            <div className="form-actions">
                                <button type="submit" className="btn btn-primary">Login</button>
                                <button type="button" className="btn btn-secondary" onClick={() => setShowLogin(false)}>
                                    Cancel
                                </button>
                            </div>
                        </form>
                    )}
                </div>

                <div className="card">
                    <h2>⚙️ Configuration</h2>
                    <div className="config-form">
                        <label>
                            Channel URL:
                            <input
                                type="text"
                                placeholder="https://www.youtube.com/@channel"
                                value={config.channel_url}
                                onChange={(e) => setConfig({ ...config, channel_url: e.target.value })}
                            />
                        </label>

                        <label>
                            Video Limit:
                            <input
                                type="number"
                                min="1"
                                max="20"
                                value={config.video_limit}
                                onChange={(e) => setConfig({ ...config, video_limit: parseInt(e.target.value) })}
                            />
                        </label>

                        <div className="checkbox-group">
                            <label>
                                <input
                                    type="checkbox"
                                    checked={config.should_subscribe}
                                    onChange={(e) => setConfig({ ...config, should_subscribe: e.target.checked })}
                                />
                                Subscribe to channel
                            </label>

                            <label>
                                <input
                                    type="checkbox"
                                    checked={config.should_like}
                                    onChange={(e) => setConfig({ ...config, should_like: e.target.checked })}
                                />
                                Like videos
                            </label>

                            <label>
                                <input
                                    type="checkbox"
                                    checked={config.should_comment}
                                    onChange={(e) => setConfig({ ...config, should_comment: e.target.checked })}
                                />
                                Post comments
                            </label>
                        </div>

                        <div className="control-buttons">
                            <button
                                className="btn btn-success"
                                onClick={handleStart}
                                disabled={!status?.is_logged_in || status?.is_running}
                            >
                                ▶️ Start Automation
                            </button>
                            <button
                                className="btn btn-danger"
                                onClick={handleStop}
                                disabled={!status?.is_running}
                            >
                                ⏹️ Stop
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="card activity-log">
                <div className="log-header">
                    <h2>📝 Activity Log</h2>
                    <button className="btn btn-small" onClick={handleClearLogs}>
                        Clear
                    </button>
                </div>
                <div className="log-content">
                    {activities.length === 0 ? (
                        <p className="empty-state">No activities yet</p>
                    ) : (
                        activities.map((activity, idx) => (
                            <div key={idx} className={`log-entry ${activity.status}`}>
                                <span className="log-time">
                                    {new Date(activity.timestamp).toLocaleTimeString()}
                                </span>
                                <span className="log-action">{activity.action}</span>
                                <span className="log-details">{activity.details}</span>
                            </div>
                        ))
                    )}
                </div>
            </div>

            <footer className="footer">
                <p>⚠️ Educational project only - Use responsibly</p>
            </footer>
        </div>
    );
}
