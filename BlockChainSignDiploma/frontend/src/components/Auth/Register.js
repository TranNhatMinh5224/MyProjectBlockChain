import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Container, Card, Form, Button, Alert, InputGroup } from 'react-bootstrap';
import { FaUserPlus, FaEye, FaEyeSlash } from 'react-icons/fa';
import { authAPI } from '../../services/api';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    schoolId: '',
    schoolName: '',
  });

  // UI State
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordMatch, setPasswordMatch] = useState(true);

  // Form Status State
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  // Validate password match in real-time
  useEffect(() => {
    if (formData.confirmPassword) {
      setPasswordMatch(formData.password === formData.confirmPassword);
    } else {
      setPasswordMatch(true); // Don't show error if confirm field is empty
    }
  }, [formData.password, formData.confirmPassword]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    // Validate password match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password strength
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      const registerData = {
        email: formData.email.trim(),
        password: formData.password.trim(),
        schoolId: formData.schoolId.trim(),
        schoolName: formData.schoolName.trim(),
      };

      await authAPI.register(registerData);
      setSuccess(true);

      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="py-5">
      <div className="row justify-content-center">
        <div className="col-md-8 col-lg-6">
          <Card className="shadow-lg border-0 rounded-3">
            <Card.Body className="p-5">
              <div className="text-center mb-4">
                <div className="bg-primary bg-opacity-10 d-inline-block p-3 rounded-circle mb-3">
                  <FaUserPlus size={40} className="text-primary" />
                </div>
                <h2 className="fw-bold text-dark">School Registration</h2>
                <p className="text-muted small">Register your school to start issuing blockchain diplomas</p>
              </div>

              {error && <Alert variant="danger" className="text-center border-0 bg-danger-subtle text-danger">{error}</Alert>}
              {success && (
                <Alert variant="success" className="text-center border-0 bg-success-subtle text-success">
                  <strong>Registration successful!</strong> Redirecting to login...
                </Alert>
              )}

              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label className="fw-bold small text-muted">Organization Email</Form.Label>
                  <Form.Control
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="name@school.edu.vn"
                    className="py-2"
                    required
                  />
                </Form.Group>

                <div className="row">
                  <div className="col-md-4">
                    <Form.Group className="mb-3">
                      <Form.Label className="fw-bold small text-muted">School ID</Form.Label>
                      <Form.Control
                        type="text"
                        name="schoolId"
                        value={formData.schoolId}
                        onChange={handleChange}
                        placeholder="e.g. HUST"
                        className="py-2 font-monospace text-uppercase"
                        required
                      />
                    </Form.Group>
                  </div>
                  <div className="col-md-8">
                    <Form.Group className="mb-3">
                      <Form.Label className="fw-bold small text-muted">School Name</Form.Label>
                      <Form.Control
                        type="text"
                        name="schoolName"
                        value={formData.schoolName}
                        onChange={handleChange}
                        placeholder="e.g. Hanoi University of Science..."
                        className="py-2"
                        required
                      />
                    </Form.Group>
                  </div>
                </div>

                <Form.Group className="mb-3">
                  <Form.Label className="fw-bold small text-muted">Password</Form.Label>
                  <InputGroup>
                    <Form.Control
                      type={showPassword ? "text" : "password"}
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="Min. 8 characters"
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

                <Form.Group className="mb-4">
                  <Form.Label className="fw-bold small text-muted">Confirm Password</Form.Label>
                  <InputGroup hasValidation>
                    <Form.Control
                      type={showConfirmPassword ? "text" : "password"}
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      placeholder="Re-enter password"
                      className={`py-2 border-end-0 ${!passwordMatch ? 'is-invalid' : ''}`}
                      required
                    />
                    <InputGroup.Text
                      className={`bg-white border-start-0 cursor-pointer ${!passwordMatch ? 'border-danger' : ''}`}
                      style={{ cursor: 'pointer' }}
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? <FaEyeSlash className="text-muted" /> : <FaEye className="text-muted" />}
                    </InputGroup.Text>
                    {!passwordMatch && (
                      <Form.Control.Feedback type="invalid">
                        Passwords do not match
                      </Form.Control.Feedback>
                    )}
                  </InputGroup>
                </Form.Group>

                <Button
                  variant="primary"
                  type="submit"
                  className="w-100 mb-3 py-2 fw-bold shadow-sm"
                  disabled={loading || success || !passwordMatch}
                >
                  {loading ? 'Creating Account...' : 'Create Account'}
                </Button>

                <div className="text-center mt-4">
                  <p className="small text-muted mb-0">
                    Already have an account? <Link to="/login" className="text-primary fw-bold text-decoration-none">Sign In</Link>
                  </p>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </div>
      </div>
    </Container>
  );
};

export default Register;
