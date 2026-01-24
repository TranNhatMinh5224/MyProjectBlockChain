import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Container, Card, Form, Button, Alert, InputGroup } from 'react-bootstrap';
import { FaSignInAlt, FaEye, FaEyeSlash } from 'react-icons/fa';
import { authAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  // UI State
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const { login } = useAuth();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const loginData = {
        username: formData.username.trim(),
        password: formData.password.trim(),
      };
      const response = await authAPI.login(loginData);
      const { access_token, user } = response.data.data;

      login(access_token, user);

      // Navigate based on role
      if (user.role === 'MINISTRY') {
        navigate('/ministry/dashboard');
      } else if (user.role === 'SCHOOL') {
        navigate('/school/dashboard');
      } else {
        navigate('/');
      }
    } catch (err) {
      if (err.response?.status === 401) {
        setError('Tài khoản hoặc mật khẩu của bạn không đúng, xin vui lòng thử lại.');
      } else {
        setError(err.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng thử lại.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="py-5">
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-5">
          <Card className="shadow-lg border-0 rounded-3">
            <Card.Body className="p-5">
              <div className="text-center mb-4">
                <div className="bg-primary bg-opacity-10 d-inline-block p-3 rounded-circle mb-3">
                  <FaSignInAlt size={40} className="text-primary" />
                </div>
                <h2 className="fw-bold text-dark">Welcome Back</h2>
                <p className="text-muted small">Sign in to access your dashboard</p>
              </div>

              {error && <Alert variant="danger" className="text-center border-0 bg-danger-subtle text-danger py-2 mb-4">{error}</Alert>}

              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label className="fw-bold small text-muted">Username or Email</Form.Label>
                  <Form.Control
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    placeholder="Enter username or email"
                    className="py-2"
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Label className="fw-bold small text-muted">Password</Form.Label>
                  <InputGroup>
                    <Form.Control
                      type={showPassword ? "text" : "password"}
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="Enter password"
                      className="py-2 border-end-0"
                      required
                    />
                    <InputGroup.Text
                      className="bg-white border-start-0 cursor-pointer"
                      style={{ cursor: 'pointer' }}
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <FaEyeSlash className="text-muted" /> : <FaEye className="text-muted" />}
                    </InputGroup.Text>
                  </InputGroup>
                </Form.Group>

                <Button
                  variant="primary"
                  type="submit"
                  className="w-100 mb-3 py-2 fw-bold shadow-sm"
                  disabled={loading}
                >
                  {loading ? 'Authenticating...' : 'Sign In'}
                </Button>

                <div className="text-center mt-4">
                  <p className="small text-muted mb-0">
                    Don't have an account? <Link to="/register" className="text-primary fw-bold text-decoration-none">Create Account</Link>
                  </p>
                </div>
              </Form>

              <hr className="my-4" />

              <div className="text-center bg-light p-3 rounded">
                <small className="text-muted d-block mb-1 fw-bold">Demo Credentials:</small>
                <div className="d-flex justify-content-center gap-3">
                  <small className="text-secondary">
                    <span className="fw-bold">Ministry:</span> admin/admin123
                  </small>
                </div>
              </div>
            </Card.Body>
          </Card>
        </div>
      </div>
    </Container>
  );
};

export default Login;
