import React, { useEffect, useState } from 'react';
import { Container, Card, Table, Badge, Button, Modal, Form, Alert, Spinner } from 'react-bootstrap';
import { FaFileAlt, FaBan, FaExternalLinkAlt } from 'react-icons/fa';
import { schoolAPI } from '../../services/api';
import SuccessModal from '../Common/SuccessModal';

const SchoolDiplomas = () => {
    const [diplomas, setDiplomas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Revoke Modal State
    const [showRevokeModal, setShowRevokeModal] = useState(false);
    const [showSuccessModal, setShowSuccessModal] = useState(false); // Success Modal State
    const [selectedDiploma, setSelectedDiploma] = useState(null);
    const [revokeReason, setRevokeReason] = useState('');
    const [revoking, setRevoking] = useState(false);

    useEffect(() => {
        fetchDiplomas();
    }, []);

    const fetchDiplomas = async () => {
        try {
            setLoading(true);
            // Fetch all diplomas (pagination can be added later)
            const response = await schoolAPI.getDiplomas(100, 0);
            setDiplomas(response.data.data.diplomas || []);
        } catch (err) {
            console.error('Error fetching diplomas:', err);
            setError('Failed to load diplomas. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleRevokeClick = (diploma) => {
        setSelectedDiploma(diploma);
        setRevokeReason('');
        setShowRevokeModal(true);
    };

    const handleRevokeSubmit = async (e) => {
        e.preventDefault();
        if (!selectedDiploma || !revokeReason) return;

        try {
            setRevoking(true);
            const formData = new FormData(); // Define formData here

            // Get checked file_hash from form input (it might have been edited by user)
            const formElements = e.target.elements;
            const fileHashInput = formElements.fileHash.value;

            formData.append('file_hash', fileHashInput);
            formData.append('reason', revokeReason);

            await schoolAPI.revokeDiploma(formData);

            // Success
            setShowRevokeModal(false);
            setShowSuccessModal(true);

            // Auto close success modal and refresh list after 1.5s
            setTimeout(() => {
                setShowSuccessModal(false);
                fetchDiplomas(); // Refresh list to show new status
            }, 1500);

        } catch (err) {
            console.error('Revoke failed:', err);
            alert('Failed to revoke diploma: ' + (err.response?.data?.detail || err.message));
        } finally {
            setRevoking(false);
        }
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'ISSUED':
            case 'ACTIVE': // Depending on what chaincode returns default
                return <Badge bg="success">VALID</Badge>;
            case 'REVOKED':
                return <Badge bg="danger">REVOKED</Badge>;
            default:
                return <Badge bg="secondary">{status}</Badge>;
        }
    };

    if (loading) {
        return (
            <Container className="py-5 text-center">
                <Spinner animation="border" variant="primary" />
                <p className="mt-2">Loading diplomas...</p>
            </Container>
        );
    }

    return (
        <Container className="py-5">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h2 className="fw-bold mb-0">Issued Diplomas</h2>
                <Button variant="primary" onClick={fetchDiplomas}>
                    Refresh List
                </Button>
            </div>

            {error && <Alert variant="danger">{error}</Alert>}

            <Card className="shadow-sm border-0">
                <Card.Body className="p-0">
                    <Table responsive hover className="mb-0">
                        <thead className="bg-light">
                            <tr>
                                <th className="py-3 ps-4">Student</th>
                                <th className="py-3">Major / Grade</th>
                                <th className="py-3">Issue Date</th>
                                <th className="py-3">Status</th>
                                <th className="py-3 text-end pe-4">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {diplomas.length > 0 ? (
                                diplomas.map((diploma) => (
                                    <tr key={diploma.id || diploma.diplomaId}>
                                        <td className="ps-4 align-middle">
                                            <div className="fw-bold">{diploma.studentName}</div>
                                            <div className="text-muted small">ID: {diploma.studentId}</div>
                                        </td>
                                        <td className="align-middle">
                                            <div>{diploma.major}</div>
                                            <div className="text-muted small">{diploma.grade}</div>
                                        </td>
                                        <td className="align-middle">
                                            {diploma.issueDate}
                                        </td>
                                        <td className="align-middle">
                                            {getStatusBadge(diploma.status)}
                                        </td>
                                        <td className="text-end pe-4 align-middle">
                                            <Button
                                                variant="outline-info"
                                                size="sm"
                                                className="me-2"
                                                href={`/verify?hash=${diploma.fileHash}`}
                                                target="_blank"
                                                title="View/Verify"
                                            >
                                                <FaExternalLinkAlt />
                                            </Button>

                                            {diploma.status !== 'REVOKED' && (
                                                <Button
                                                    variant="outline-danger"
                                                    size="sm"
                                                    onClick={() => handleRevokeClick(diploma)}
                                                    title="Revoke Diploma"
                                                >
                                                    <FaBan /> Revoke
                                                </Button>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="text-center py-5">
                                        <div className="text-muted">
                                            <FaFileAlt size={40} className="mb-3 opacity-50" />
                                            <p>No diplomas found.</p>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </Table>
                </Card.Body>
            </Card>

            {/* Revoke Modal */}
            <Modal show={showRevokeModal} onHide={() => setShowRevokeModal(false)} centered>
                <Modal.Header closeButton>
                    <Modal.Title className="text-danger fw-bold">
                        <FaBan className="me-2" />
                        Revoke Diploma
                    </Modal.Title>
                </Modal.Header>
                <Form onSubmit={handleRevokeSubmit}>
                    <Modal.Body>
                        <Alert variant="warning" className="border-warning bg-warning-subtle">
                            <p className="mb-0 small">
                                <strong>Warning:</strong> Are you sure you want to revoke this diploma? This action is permanent and cannot be undone.
                            </p>
                        </Alert>

                        <div className="mb-4 p-3 bg-light rounded text-muted small">
                            <div className="d-flex justify-content-between mb-1">
                                <span>Student:</span>
                                <span className="fw-medium text-dark">{selectedDiploma?.studentName}</span>
                            </div>
                            <div className="d-flex justify-content-between">
                                <span>Diploma ID:</span>
                                <span className="fw-mono text-dark">{selectedDiploma?.diplomaId || selectedDiploma?.id}</span>
                            </div>
                        </div>

                        <Form.Group className="mb-3">
                            <Form.Label className="small fw-bold text-muted">File Hash <span className="text-danger">*</span></Form.Label>
                            <Form.Control
                                type="text"
                                name="fileHash"
                                defaultValue={selectedDiploma?.fileHash || ''}
                                placeholder="Enter SHA-256 hash of the diploma"
                                className="font-monospace small"
                                required
                            />
                            <Form.Text className="text-muted small">
                                This is the unique digital fingerprint of the diploma on the blockchain.
                            </Form.Text>
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label className="small fw-bold text-muted">Reason for Revocation <span className="text-danger">*</span></Form.Label>
                            <Form.Control
                                as="textarea"
                                rows={3}
                                value={revokeReason}
                                onChange={(e) => setRevokeReason(e.target.value)}
                                placeholder="Ex: Printing error, Plagiarism detected..."
                                required
                            />
                        </Form.Group>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button variant="outline-secondary" onClick={() => setShowRevokeModal(false)}>
                            Cancel
                        </Button>
                        <Button variant="danger" type="submit" disabled={revoking}>
                            {revoking ? 'Revoking...' : 'Confirm Revoke'}
                        </Button>
                    </Modal.Footer>
                </Form>
            </Modal>

            {/* Success Modal */}
            <SuccessModal
                show={showSuccessModal}
                onHide={() => setShowSuccessModal(false)}
                title="Thu hồi thành công!"
                message="Văn bằng này đã được đánh dấu là không còn hiệu lực trên hệ thống Blockchain."
                autoDismiss={true} // Enable clean mode without buttons
            />
        </Container>
    );
};

export default SchoolDiplomas;
