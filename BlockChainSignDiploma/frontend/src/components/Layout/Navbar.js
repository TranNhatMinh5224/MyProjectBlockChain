import React from 'react';
import { Link, useNavigate, NavLink } from 'react-router-dom';
import { Navbar, Nav, Container, Button, Badge } from 'react-bootstrap';
import { FaUserCircle, FaSignOutAlt, FaShieldAlt } from 'react-icons/fa';
import { useAuth } from '../../contexts/AuthContext';

const NavigationBar = () => {
  const { user, logout, isMinistry, isSchool } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Helper to style active links
  const navLinkStyle = ({ isActive }) => ({
    fontWeight: isActive ? 'bold' : 'normal',
    color: isActive ? '#0dcaf0' : 'rgba(255, 255, 255, 0.75)', // Cyan for active, gray-white for inactive
    borderBottom: isActive ? '2px solid #0dcaf0' : '2px solid transparent',
    paddingBottom: '2px',
    transition: 'all 0.3s ease'
  });

  return (
    <Navbar bg="dark" variant="dark" expand="lg" className="shadow-sm py-3">
      <Container>
        <Navbar.Brand as={Link} to="/" className="fw-bold fs-4 text-white d-flex align-items-center">
          <FaShieldAlt className="me-2 text-info" />
          Blockchain Diploma
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto ms-lg-4 gap-2">
            <Nav.Link as={NavLink} to="/" style={navLinkStyle} end>Home</Nav.Link>
            <Nav.Link as={NavLink} to="/verify" style={navLinkStyle}>Verify</Nav.Link>
            <Nav.Link as={NavLink} to="/crypto-tools" style={navLinkStyle}>Tools</Nav.Link>
            <Nav.Link as={NavLink} to="/sign-file" style={navLinkStyle}>Sign File</Nav.Link>

            {user && isSchool() && (
              <>
                <Nav.Link as={NavLink} to="/school/dashboard" style={navLinkStyle}>Dashboard</Nav.Link>
                <Nav.Link as={NavLink} to="/school/diplomas" style={navLinkStyle}>Diplomas</Nav.Link>
                <Nav.Link as={NavLink} to="/school/csr" style={navLinkStyle}>CSR</Nav.Link>
                <Nav.Link as={NavLink} to="/school/push-diploma" style={navLinkStyle}>Push Diploma</Nav.Link>
              </>
            )}

            {user && isMinistry() && (
              <>
                <Nav.Link as={NavLink} to="/ministry/dashboard" style={navLinkStyle}>Dashboard</Nav.Link>
                <Nav.Link as={NavLink} to="/ministry/schools" style={navLinkStyle}>Schools</Nav.Link>
                <Nav.Link as={NavLink} to="/ministry/csr" style={navLinkStyle}>Manage CSR</Nav.Link>
              </>
            )}
          </Nav>

          <Nav className="align-items-center mt-3 mt-lg-0">
            {user ? (
              <>
                <Nav.Item className="d-flex align-items-center me-3 text-light">
                  <FaUserCircle className="me-2 text-info" size={24} />
                  <div className="lh-1">
                    <div className="fw-bold small">{user.email || user.username}</div>
                    <div className="d-flex align-items-center mt-1">
                      <Badge bg={isMinistry() ? 'primary' : 'info'} className="me-1" style={{ fontSize: '0.65rem' }}>
                        {user.role}
                      </Badge>
                      <Badge bg={user.status === 'ACTIVE' ? 'success' : 'warning'} style={{ fontSize: '0.65rem' }}>
                        {user.status}
                      </Badge>
                    </div>
                  </div>
                </Nav.Item>
                <Button variant="outline-light" size="sm" onClick={handleLogout} className="px-3">
                  <FaSignOutAlt className="me-1" />
                  Logout
                </Button>
              </>
            ) : (
              <div className="d-flex gap-2">
                <Button as={Link} to="/login" variant="outline-info" size="sm" className="px-3 fw-bold">Login</Button>
                <Button as={Link} to="/register" variant="light" size="sm" className="px-3 fw-bold">Register</Button>
              </div>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default NavigationBar;
