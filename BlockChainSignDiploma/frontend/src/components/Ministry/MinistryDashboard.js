import React, { useEffect, useState } from 'react';
import { Container, Card, Row, Col, Alert } from 'react-bootstrap';
import { FaUniversity, FaCheckCircle, FaClock, FaTimesCircle } from 'react-icons/fa';
import { ministryAPI } from '../../services/api';

const MinistryDashboard = () => {
  const [stats, setStats] = useState({
    pending: 0,
    approved: 0,
    rejected: 0,
    total: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await ministryAPI.listCSR(null);
      const csrs = response.data.data || [];

      const pending = csrs.filter((c) => c.status === 'PENDING').length;
      const approved = csrs.filter((c) => c.status === 'APPROVED').length;
      const rejected = csrs.filter((c) => c.status === 'REJECTED').length;

      setStats({
        pending,
        approved,
        rejected,
        total: csrs.length,
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="py-5">
      <h2 className="mb-4 fw-bold">Ministry Dashboard</h2>

      {/* Welcome Section */}
      <Card className="mb-4 shadow-sm border-0 bg-primary text-white">
        <Card.Body className="p-4">
          <h4 className="mb-3">
            <FaUniversity className="me-2" />
            Ministry of Education
          </h4>
          <p className="mb-0">
            Manage and approve schools for blockchain diploma issuance
          </p>
        </Card.Body>
      </Card>

      {/* Statistics */}
      <Row className="g-4 mb-4">
        <Col md={3}>
          <Card className="h-100 shadow-sm border-warning border-2">
            <Card.Body className="text-center p-4">
              <FaClock size={40} className="text-warning mb-3" />
              <h3 className="fw-bold mb-0">{stats.pending}</h3>
              <p className="text-muted mb-0">Pending CSRs</p>
            </Card.Body>
          </Card>
        </Col>

        <Col md={3}>
          <Card className="h-100 shadow-sm border-success border-2">
            <Card.Body className="text-center p-4">
              <FaCheckCircle size={40} className="text-success mb-3" />
              <h3 className="fw-bold mb-0">{stats.approved}</h3>
              <p className="text-muted mb-0">Approved</p>
            </Card.Body>
          </Card>
        </Col>

        <Col md={3}>
          <Card className="h-100 shadow-sm border-danger border-2">
            <Card.Body className="text-center p-4">
              <FaTimesCircle size={40} className="text-danger mb-3" />
              <h3 className="fw-bold mb-0">{stats.rejected}</h3>
              <p className="text-muted mb-0">Rejected</p>
            </Card.Body>
          </Card>
        </Col>

        <Col md={3}>
          <Card className="h-100 shadow-sm border-primary border-2">
            <Card.Body className="text-center p-4">
              <FaUniversity size={40} className="text-primary mb-3" />
              <h3 className="fw-bold mb-0">{stats.total}</h3>
              <p className="text-muted mb-0">Total CSRs</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Card className="shadow-sm">
        <Card.Header className="bg-light">
          <h5 className="mb-0">Quick Actions</h5>
        </Card.Header>
        <Card.Body>
          {stats.pending > 0 ? (
            <Alert variant="warning" className="mb-0">
              <strong>Action Required:</strong> You have {stats.pending} pending CSR
              {stats.pending > 1 ? 's' : ''} waiting for review.
              <br />
              <a href="/ministry/csr" className="alert-link">
                Go to CSR Management →
              </a>
            </Alert>
          ) : (
            <Alert variant="success" className="mb-0">
              <strong>All Clear!</strong> No pending CSRs at the moment.
            </Alert>
          )}
        </Card.Body>
      </Card>

      {/* Info */}
      <Card className="mt-4 shadow-sm">
        <Card.Header className="bg-light">
          <h5 className="mb-0">Ministry Responsibilities</h5>
        </Card.Header>
        <Card.Body>
          <ul className="mb-0">
            <li className="mb-2">
              <strong>Review CSRs:</strong> Examine Certificate Signing Requests from schools
            </li>
            <li className="mb-2">
              <strong>Approve Schools:</strong> Authorize legitimate schools to issue diplomas
            </li>
            <li className="mb-2">
              <strong>Sign Certificates:</strong> Provide digital certificates to approved schools
            </li>
            <li className="mb-2">
              <strong>Blockchain Registration:</strong> Register schools on the Hyperledger Fabric network
            </li>
            <li>
              <strong>Revoke Access:</strong> Revoke school access if necessary
            </li>
          </ul>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default MinistryDashboard;
