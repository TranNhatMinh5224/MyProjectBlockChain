import React, { useEffect, useState } from 'react';
import { Container, Card, Table, Badge, Button, Modal, Form, Alert, Spinner } from 'react-bootstrap';
import { FaCheckCircle, FaTimesCircle, FaEye } from 'react-icons/fa';
import { ministryAPI } from '../../services/api';
import { formatDate } from '../../utils/helpers';

const MinistryCSRManagement = () => {
  const [csrList, setCSRList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('PENDING');
  const [selectedCSR, setSelectedCSR] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState(''); // 'approve' or 'reject'
  const [modalData, setModalData] = useState({
    ministry_private_key: '',
    registered_date: new Date().toISOString().split('T')[0],
    reason: '',
  });
  const [error, setError] = useState('');
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchCSRList();
  }, [filter]);

  const fetchCSRList = async () => {
    setLoading(true);
    try {
      const response = await ministryAPI.listCSR(filter);
      setCSRList(response.data.data || []);
    } catch (error) {
      console.error('Error fetching CSR list:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleShowModal = (csr, type) => {
    setSelectedCSR(csr);
    setModalType(type);
    setShowModal(true);
    setError('');
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedCSR(null);
    setModalData({
      ministry_private_key: '',
      registered_date: new Date().toISOString().split('T')[0],
      reason: '',
    });
    setError('');
  };

  const handleApprove = async () => {
    setProcessing(true);
    setError('');

    try {
      await ministryAPI.approveCSR(selectedCSR.id, {
        ministry_private_key: modalData.ministry_private_key,
        registered_date: modalData.registered_date,
      });

      handleCloseModal();
      fetchCSRList();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to approve CSR');
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async () => {
    setProcessing(true);
    setError('');

    try {
      await ministryAPI.rejectCSR(selectedCSR.id, {
        reason: modalData.reason,
      });

      handleCloseModal();
      fetchCSRList();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to reject CSR');
    } finally {
      setProcessing(false);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      PENDING: 'warning',
      APPROVED: 'success',
      REJECTED: 'danger',
    };
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
  };

  return (
    <Container className="py-5">
      <h2 className="mb-4 fw-bold">CSR Management</h2>

      {/* Filter Buttons */}
      <Card className="mb-4 shadow-sm">
        <Card.Body>
          <div className="btn-group w-100" role="group">
            <button
              type="button"
              className={`btn ${filter === 'PENDING' ? 'btn-warning' : 'btn-outline-warning'}`}
              onClick={() => setFilter('PENDING')}
            >
              Pending
            </button>
            <button
              type="button"
              className={`btn ${filter === 'APPROVED' ? 'btn-success' : 'btn-outline-success'}`}
              onClick={() => setFilter('APPROVED')}
            >
              Approved
            </button>
            <button
              type="button"
              className={`btn ${filter === 'REJECTED' ? 'btn-danger' : 'btn-outline-danger'}`}
              onClick={() => setFilter('REJECTED')}
            >
              Rejected
            </button>
            <button
              type="button"
              className={`btn ${!filter ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setFilter(null)}
            >
              All
            </button>
          </div>
        </Card.Body>
      </Card>

      {/* CSR Table */}
      <Card className="shadow-sm">
        <Card.Body>
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" variant="primary" />
              <p className="mt-3 text-muted">Loading CSRs...</p>
            </div>
          ) : csrList.length === 0 ? (
            <Alert variant="info">No CSRs found for the selected filter.</Alert>
          ) : (
            <div className="table-responsive">
              <Table hover>
                <thead className="table-light">
                  <tr>
                    <th>School ID</th>
                    <th>School Name</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Submitted</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {csrList.map((csr) => (
                    <tr key={csr.id}>
                      <td className="fw-bold">{csr.schoolId}</td>
                      <td>{csr.schoolName}</td>
                      <td>{csr.email}</td>
                      <td>{getStatusBadge(csr.status)}</td>
                      <td>{formatDate(csr.createdAt)}</td>
                      <td>
                        {csr.status === 'PENDING' ? (
                          <div className="btn-group btn-group-sm">
                            <Button
                              variant="success"
                              size="sm"
                              onClick={() => handleShowModal(csr, 'approve')}
                            >
                              <FaCheckCircle className="me-1" />
                              Approve
                            </Button>
                            <Button
                              variant="danger"
                              size="sm"
                              onClick={() => handleShowModal(csr, 'reject')}
                            >
                              <FaTimesCircle className="me-1" />
                              Reject
                            </Button>
                          </div>
                        ) : (
                          <Badge bg="secondary">Processed</Badge>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          )}
        </Card.Body>
      </Card>

      {/* Approve/Reject Modal */}
      <Modal show={showModal} onHide={handleCloseModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {modalType === 'approve' ? (
              <>
                <FaCheckCircle className="text-success me-2" />
                Approve CSR
              </>
            ) : (
              <>
                <FaTimesCircle className="text-danger me-2" />
                Reject CSR
              </>
            )}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedCSR && (
            <>
              <Alert variant="info">
                <strong>School:</strong> {selectedCSR.schoolName} ({selectedCSR.schoolId})
                <br />
                <strong>Email:</strong> {selectedCSR.email}
              </Alert>

              {error && <Alert variant="danger">{error}</Alert>}

              {modalType === 'approve' ? (
                <>
                  <Form.Group className="mb-3">
                    <Form.Label className="fw-bold">Ministry Private Key *</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={2}
                      value={modalData.ministry_private_key}
                      onChange={(e) =>
                        setModalData({ ...modalData, ministry_private_key: e.target.value })
                      }
                      placeholder="0x..."
                      required
                      className="font-monospace small"
                    />
                    <Form.Text className="text-muted">
                      Your Ministry private key to sign the certificate
                    </Form.Text>
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label className="fw-bold">Registration Date *</Form.Label>
                    <Form.Control
                      type="date"
                      value={modalData.registered_date}
                      onChange={(e) =>
                        setModalData({ ...modalData, registered_date: e.target.value })
                      }
                      required
                    />
                  </Form.Group>

                  <Alert variant="warning">
                    <strong>⚠️ Important:</strong> By approving this CSR, you are authorizing this
                    school to issue diplomas on the blockchain. Make sure all information is correct.
                  </Alert>
                </>
              ) : (
                <>
                  <Form.Group className="mb-3">
                    <Form.Label className="fw-bold">Rejection Reason *</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={4}
                      value={modalData.reason}
                      onChange={(e) => setModalData({ ...modalData, reason: e.target.value })}
                      placeholder="Please provide a reason for rejection..."
                      required
                    />
                  </Form.Group>

                  <Alert variant="info">
                    The school will be notified of the rejection and can submit a new CSR after
                    addressing the issues.
                  </Alert>
                </>
              )}
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseModal} disabled={processing}>
            Cancel
          </Button>
          <Button
            variant={modalType === 'approve' ? 'success' : 'danger'}
            onClick={modalType === 'approve' ? handleApprove : handleReject}
            disabled={processing}
          >
            {processing ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Processing...
              </>
            ) : modalType === 'approve' ? (
              'Approve CSR'
            ) : (
              'Reject CSR'
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default MinistryCSRManagement;
