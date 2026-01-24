import React, { useEffect, useState } from 'react';
import { Container, Card, Table, Badge, Button, Modal, Form, Alert, Spinner } from 'react-bootstrap';
import { FaUniversity, FaBan, FaExclamationTriangle } from 'react-icons/fa';
import { ministryAPI } from '../../services/api';
import SuccessModal from '../Common/SuccessModal';

const MinistrySchools = () => {
    const [schools, setSchools] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Revoke Modal State
    const [showRevokeModal, setShowRevokeModal] = useState(false);
    const [showSuccessModal, setShowSuccessModal] = useState(false);
    const [selectedSchool, setSelectedSchool] = useState(null);
    const [revokeReason, setRevokeReason] = useState('');
    const [revoking, setRevoking] = useState(false);

    useEffect(() => {
        fetchSchools();
    }, []);

    const fetchSchools = async () => {
        try {
            setLoading(true);
            const response = await ministryAPI.listSchools();
            // Backend returns data: { schools: [...], total: N }
            setSchools(response.data.data.schools || []);
        } catch (err) {
            console.error('Error fetching schools:', err);
            setError('Failed to load schools list.');
        } finally {
            setLoading(false);
        }
    };

    const handleRevokeClick = (school) => {
        setSelectedSchool(school);
        setRevokeReason('');
        setShowRevokeModal(true);
    };

    const handleRevokeSubmit = async (e) => {
        e.preventDefault();
        if (!selectedSchool || !revokeReason) return;

        try {
            setRevoking(true);
            await ministryAPI.revokeSchool(selectedSchool.id, revokeReason);

            // Success
            setShowRevokeModal(false);
            setShowSuccessModal(true);

            // Auto dismiss and refresh
            setTimeout(() => {
                setShowSuccessModal(false);
                fetchSchools();
            }, 1500);

        } catch (err) {
            console.error('Revoke failed:', err);
            alert('Failed to revoke school: ' + (err.response?.data?.detail || err.message));
        } finally {
            setRevoking(false);
        }
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'ACTIVE':
                return <Badge bg="success">ACTIVE</Badge>;
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
                <p className="mt-2">Loading schools...</p>
            </Container>
        );
    }

    return (
        <Container className="py-5">
            <h2 className="mb-4 fw-bold">
                <FaUniversity className="me-2" />
                Manage Schools
            </h2>

            {error && <Alert variant="danger">{error}</Alert>}

            <Card className="shadow-sm border-0">
                <Card.Body className="p-0">
                    <Table responsive hover className="mb-0">
                        <thead className="bg-light">
                            <tr>
                                <th className="py-3 ps-4">School Name</th>
                                <th className="py-3">Status</th>
                                <th className="py-3 text-end pe-4">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {schools.length > 0 ? (
                                schools.map((school) => (
                                    <tr key={school.id}>
                                        <td className="ps-4 align-middle">
                                            <div className="fw-bold">{school.name}</div>
                                            <div className="text-muted small">ID: {school.id}</div>
                                        </td>
                                        <td className="align-middle">
                                            {getStatusBadge(school.status)}
                                        </td>
                                        <td className="text-end pe-4 align-middle">
                                            {school.status === 'ACTIVE' && (
                                                <Button
                                                    variant="outline-danger"
                                                    size="sm"
                                                    onClick={() => handleRevokeClick(school)}
                                                    title="Revoke School License"
                                                >
                                                    <FaBan /> Revoke License
                                                </Button>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="3" className="text-center py-5">
                                        <p className="text-muted">No schools found.</p>
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
                        <FaExclamationTriangle className="me-2" />
                        Revoke School License
                    </Modal.Title>
                </Modal.Header>
                <Form onSubmit={handleRevokeSubmit}>
                    <Modal.Body>
                        <Alert variant="danger" className="border-danger bg-danger-subtle">
                            <p className="mb-0 small">
                                <strong>CRITICAL WARNING:</strong> Revoking a school's license will prevent them from issuing any new diplomas. This action is recorded on the blockchain and cannot be easily undone.
                            </p>
                        </Alert>

                        <div className="mb-4 p-3 bg-light rounded text-muted small">
                            <div className="d-flex justify-content-between mb-1">
                                <span>School Name:</span>
                                <span className="fw-bold text-dark">{selectedSchool?.name}</span>
                            </div>
                            <div className="d-flex justify-content-between">
                                <span>School ID:</span>
                                <span className="font-monospace text-dark">{selectedSchool?.id}</span>
                            </div>
                        </div>

                        <Form.Group className="mb-3">
                            <Form.Label className="small fw-bold text-muted">Reason for Revocation <span className="text-danger">*</span></Form.Label>
                            <Form.Control
                                as="textarea"
                                rows={3}
                                value={revokeReason}
                                onChange={(e) => setRevokeReason(e.target.value)}
                                placeholder="State the reason for revoking this school's license..."
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
                title="School Revoked Successfully!"
                message="The school's license has been revoked and recorded on the blockchain."
                autoDismiss={true}
            />
        </Container>
    );
};

export default MinistrySchools;
