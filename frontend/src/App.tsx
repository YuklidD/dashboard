import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { WebSocketProvider } from './context/WebSocketContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Honeypots from './pages/Honeypots';
import Observability from './pages/Observability';
import CVEs from './pages/CVEs';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
    return (
        <Router>
            <AuthProvider>
                <WebSocketProvider>
                    <Routes>
                        <Route path="/login" element={<Login />} />

                        <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                            <Route path="/" element={<Navigate to="/dashboard" replace />} />
                            <Route path="/dashboard" element={<Dashboard />} />
                            <Route path="/honeypots" element={<Honeypots />} />
                            <Route path="/observability" element={<Observability />} />
                            <Route path="/cves" element={<CVEs />} />
                        </Route>
                    </Routes>
                </WebSocketProvider>
            </AuthProvider>
        </Router>
    );
}

export default App;
