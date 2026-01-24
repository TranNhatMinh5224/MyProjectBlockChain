import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const PrivateRoute = ({ children, requireMinistry, requireSchool, requireActive }) => {
  const { user, isMinistry, isSchool, isActive, loading } = useAuth();

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '60vh' }}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (requireMinistry && !isMinistry()) {
    return <Navigate to="/" />;
  }

  if (requireSchool && !isSchool()) {
    return <Navigate to="/" />;
  }

  if (requireActive && !isActive()) {
    return (
      <div className="container mt-5">
        <div className="alert alert-warning">
          <h4>Account Not Active</h4>
          <p>Your account is not yet activated. Please submit CSR and wait for Ministry approval.</p>
        </div>
      </div>
    );
  }

  return children;
};

export default PrivateRoute;
