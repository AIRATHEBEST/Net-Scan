import { useState } from 'react';
import { Mail, Lock, Eye, EyeOff, Loader } from 'lucide-react';
import { authApi } from '../services/api';

interface LoginProps {
  onLoginSuccess: (token: string) => void;
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const response = await authApi.login(email, password);
        const token = response.data.access_token;
        localStorage.setItem('netscan_token', token);
        onLoginSuccess(token);
      } else {
        const response = await authApi.register(email, password, fullName);
        const token = response.data.access_token;
        localStorage.setItem('netscan_token', token);
        onLoginSuccess(token);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="logo-circle">
            <span className="logo-text">NS</span>
          </div>
          <h1>NetScan</h1>
          <p className="subtitle">Network Intelligence Platform</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <div className="input-wrapper">
              <Mail size={20} className="input-icon" />
              <input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>
          </div>

          {!isLogin && (
            <div className="form-group">
              <label htmlFor="fullName">Full Name</label>
              <input
                id="fullName"
                type="text"
                placeholder="Your Name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                disabled={loading}
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <Lock size={20} className="input-icon" />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
              />
              <button
                type="button"
                className="toggle-password"
                onClick={() => setShowPassword(!showPassword)}
                disabled={loading}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? (
              <>
                <Loader size={20} className="spinner" />
                {isLogin ? 'Signing in...' : 'Creating account...'}
              </>
            ) : (
              isLogin ? 'Sign In' : 'Create Account'
            )}
          </button>
        </form>

        <div className="toggle-auth">
          <p>
            {isLogin ? "Don't have an account? " : 'Already have an account? '}
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
              }}
              disabled={loading}
            >
              {isLogin ? 'Sign Up' : 'Sign In'}
            </button>
          </p>
        </div>
      </div>

      <style>{`
        .login-container {
          min-height: 100vh;
          background: linear-gradient(135deg, #171717 0%, #262626 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 20px;
        }

        .login-card {
          background: #1a1a1a;
          border: 1px solid #2F2F2F;
          border-radius: 20px;
          padding: 48px;
          width: 100%;
          max-width: 420px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }

        .login-header {
          text-align: center;
          margin-bottom: 40px;
        }

        .logo-circle {
          width: 80px;
          height: 80px;
          background: linear-gradient(135deg, #9E7FFF 0%, #7c3aed 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 20px;
          box-shadow: 0 10px 30px rgba(158, 127, 255, 0.3);
        }

        .logo-text {
          font-size: 32px;
          font-weight: 700;
          color: #FFFFFF;
        }

        .login-header h1 {
          font-size: 32px;
          font-weight: 700;
          color: #FFFFFF;
          margin-bottom: 8px;
        }

        .subtitle {
          font-size: 14px;
          color: #A3A3A3;
          margin: 0;
        }

        .login-form {
          display: flex;
          flex-direction: column;
          gap: 24px;
          margin-bottom: 24px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .form-group label {
          font-size: 14px;
          font-weight: 600;
          color: #FFFFFF;
        }

        .input-wrapper {
          position: relative;
          display: flex;
          align-items: center;
        }

        .input-icon {
          position: absolute;
          left: 16px;
          color: #A3A3A3;
          pointer-events: none;
        }

        .form-group input {
          width: 100%;
          padding: 12px 16px 12px 48px;
          background: #262626;
          border: 1px solid #2F2F2F;
          border-radius: 12px;
          color: #FFFFFF;
          font-size: 14px;
          transition: all 0.3s ease;
        }

        .form-group input:focus {
          outline: none;
          border-color: #9E7FFF;
          box-shadow: 0 0 0 3px rgba(158, 127, 255, 0.1);
        }

        .form-group input:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .toggle-password {
          position: absolute;
          right: 16px;
          background: none;
          border: none;
          color: #A3A3A3;
          cursor: pointer;
          padding: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: color 0.2s ease;
        }

        .toggle-password:hover:not(:disabled) {
          color: #FFFFFF;
        }

        .toggle-password:disabled {
          cursor: not-allowed;
          opacity: 0.5;
        }

        .error-message {
          padding: 12px 16px;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.3);
          border-radius: 8px;
          color: #fca5a5;
          font-size: 14px;
          text-align: center;
        }

        .submit-btn {
          padding: 12px 24px;
          background: linear-gradient(135deg, #9E7FFF 0%, #7c3aed 100%);
          border: none;
          border-radius: 12px;
          color: #FFFFFF;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          min-height: 48px;
        }

        .submit-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 10px 30px rgba(158, 127, 255, 0.3);
        }

        .submit-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .spinner {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .toggle-auth {
          text-align: center;
          border-top: 1px solid #2F2F2F;
          padding-top: 24px;
        }

        .toggle-auth p {
          font-size: 14px;
          color: #A3A3A3;
          margin: 0;
        }

        .toggle-auth button {
          background: none;
          border: none;
          color: #9E7FFF;
          cursor: pointer;
          font-weight: 600;
          transition: color 0.2s ease;
          padding: 0;
        }

        .toggle-auth button:hover:not(:disabled) {
          color: #b8a7ff;
        }

        .toggle-auth button:disabled {
          cursor: not-allowed;
          opacity: 0.5;
        }

        @media (max-width: 480px) {
          .login-card {
            padding: 32px 24px;
          }

          .login-header h1 {
            font-size: 28px;
          }

          .logo-circle {
            width: 64px;
            height: 64px;
          }

          .logo-text {
            font-size: 28px;
          }
        }
      `}</style>
    </div>
  );
};

export default Login;
