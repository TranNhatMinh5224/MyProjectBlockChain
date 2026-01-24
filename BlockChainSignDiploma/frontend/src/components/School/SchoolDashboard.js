import React, { useEffect, useState } from 'react';
import { Container, Card, Row, Col, Alert, Badge, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaCheckCircle, FaClock, FaTimesCircle, FaFileAlt, FaPlus } from 'react-icons/fa';
import { useAuth } from '../../contexts/AuthContext';
import { csrAPI } from '../../services/api';
import { formatDate } from '../../utils/helpers';

const SchoolDashboard = () => {
  const { user, isActive } = useAuth();
  const [csrStatus, setCsrStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCSRStatus();
  }, []);

  const fetchCSRStatus = async () => {
    try {
      const response = await csrAPI.getStatus();
      setCsrStatus(response.data.data);
    } catch (error) {
      console.error('Error fetching CSR status:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'ACTIVE':
      case 'APPROVED':
        return <FaCheckCircle className="text-success" size={40} />;
      case 'PENDING':
        return <FaClock className="text-warning" size={40} />;
      case 'REJECTED':
        return <FaTimesCircle className="text-danger" size={40} />;
      default:
        return <FaClock className="text-secondary" size={40} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE':
      case 'APPROVED':
        return 'success';
      case 'PENDING':
        return 'warning';
      case 'REJECTED':
        return 'danger';
      default:
        return 'secondary';
    }
  };

  if (loading) {
    return (
      <Container className="py-5 text-center mt-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </Container>
    );
  }

  return (
    <Container className="py-5">
      <h2 className="mb-4 fw-bold">School Dashboard</h2>

      {/* Welcome Section */}
      <Card className="mb-4 shadow-sm border-0 bg-primary text-white">
        <Card.Body className="p-4">
          <h4 className="mb-3">Welcome, {user?.schoolName || user?.username}!</h4>
          <p className="mb-0">School ID: <strong>{user?.schoolId}</strong></p>
        </Card.Body>
      </Card>

      {/* Status Overview */}
      <Row className="g-4 mb-4">
        <Col md={6}>
          <Card className="h-100 shadow-sm">
            <Card.Body className="text-center p-4">
              {getStatusIcon(user?.status)}
              <h5 className="mt-3 mb-2">Account Status</h5>
              <Badge bg={getStatusColor(user?.status)} className="px-3 py-2">
                {user?.status || 'UNKNOWN'}
              </Badge>
              {user?.status === 'PENDING' && (
                <p className="text-muted small mt-3 mb-0">
                  Please submit CSR to get approved
                </p>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card className="h-100 shadow-sm">
            <Card.Body className="text-center p-4">
              {csrStatus?.csr ? (
                <>
                  <FaFileAlt size={40} className="text-info mb-3" />
                  <h5 className="mb-2">CSR Status</h5>
                  <Badge bg={getStatusColor(csrStatus.csr.status)} className="px-3 py-2">
                    {csrStatus.csr.status}
                  </Badge>
                  {csrStatus.csr.status === 'PENDING' && (
                    <p className="text-muted small mt-3 mb-0">
                      Waiting for Ministry approval
                    </p>
                  )}
                </>
              ) : (
                <>
                  <FaFileAlt size={40} className="text-muted mb-3" />
                  <h5 className="mb-2">No CSR Submitted</h5>
                  <Button as={Link} to="/school/csr" variant="primary" className="mt-2">
                    Submit CSR Now
                  </Button>
                </>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* CSR Details */}
      {csrStatus?.csr && (
        <Card className="mb-4 shadow-sm">
          <Card.Header className="bg-light">
            <h5 className="mb-0">CSR Details</h5>
          </Card.Header>
          <Card.Body>
            <Row>
              <Col md={6}>
                <p className="mb-2">
                  <strong>School ID:</strong> {csrStatus.csr.schoolId}
                </p>
                <p className="mb-2">
                  <strong>School Name:</strong> {csrStatus.csr.schoolName}
                </p>
                <p className="mb-2">
                  <strong>Email:</strong> {csrStatus.csr.email}
                </p>
                <p className="mb-2">
                  <strong>Status:</strong>{' '}
                  <Badge bg={getStatusColor(csrStatus.csr.status)}>
                    {csrStatus.csr.status}
                  </Badge>
                  {csrStatus.csr.status === 'REJECTED' && (
                    <div className="mt-2">
                      <Link to="/school/csr" className="btn btn-sm btn-outline-danger">
                        <FaFileAlt className="me-1" /> Re-submit Request
                      </Link>
                    </div>
                  )}
                </p>
              </Col>
              <Col md={6}>
                <p className="mb-2">
                  <strong>Submitted At:</strong> {formatDate(csrStatus.csr.createdAt)}
                </p>
                {csrStatus.csr.approvedAt && (
                  <p className="mb-2">
                    <strong>Approved At:</strong> {formatDate(csrStatus.csr.approvedAt)}
                  </p>
                )}
                {csrStatus.csr.rejectionReason && (
                  <Alert variant="danger" className="mt-3">
                    <strong>Rejection Reason:</strong>
                    <p className="mb-0 mt-2">{csrStatus.csr.rejectionReason}</p>
                  </Alert>
                )}
              </Col>
            </Row>
          </Card.Body>
        </Card>
      )}

      {/* Actions */}
      <Card className="shadow-sm">
        <Card.Header className="bg-light">
          <h5 className="mb-0">Quick Actions</h5>
        </Card.Header>
        <Card.Body>
          <Row className="g-3">
            {(!csrStatus?.csr || csrStatus?.csr?.status === 'REJECTED') && (
              <Col md={4}>
                <Button
                  as={Link}
                  to="/school/csr"
                  variant={csrStatus?.csr?.status === 'REJECTED' ? 'danger' : 'primary'}
                  className="w-100"
                >
                  <FaFileAlt className="me-2" />
                  {csrStatus?.csr?.status === 'REJECTED' ? 'Re-submit CSR' : 'Submit CSR'}
                </Button>
              </Col>
            )}

            {isActive() && (
              <Col md={4}>
                <Button
                  as={Link}
                  to="/school/push-diploma"
                  variant="success"
                  className="w-100"
                >
                  <FaPlus className="me-2" />
                  Push New Diploma
                </Button>
              </Col>
            )}

            <Col md={4}>
              <Button
                as={Link}
                to="/school/diplomas"
                variant="secondary"
                className="w-100"
              >
                <FaFileAlt className="me-2" />
                Manage Diplomas
              </Button>
            </Col>

            <Col md={4}>
              <Button
                as={Link}
                to="/crypto-tools"
                variant="info"
                className="w-100"
              >
                Generate Keypair
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Instructions */}
      {!isActive() && (
        <Alert variant="info" className="mt-4">
          <h5>Getting Started</h5>
          <ol className="mb-0">
            <li>Generate a keypair using Crypto Tools</li>
            <li>Submit CSR with your public key</li>
            <li>Wait for Ministry to approve your CSR</li>
            <li>Once approved, you can start issuing diplomas!</li>
          </ol>
        </Alert>
      )}
    </Container>
  );
};

export default SchoolDashboard;
