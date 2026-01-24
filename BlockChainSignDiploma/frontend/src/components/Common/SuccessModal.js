import React from 'react';
import { Modal, Button } from 'react-bootstrap';
import { FaCheckCircle } from 'react-icons/fa';

const SuccessModal = ({
    show,
    onHide,
    title = "Chúc mừng! Thao tác thành công 🎓",
    message,
    primaryBtnText,
    secondaryBtnText,
    onPrimaryAction,
    onSecondaryAction,
    autoDismiss = false // New prop to indicate auto-dismiss mode
}) => {
    return (
        <Modal
            show={show}
            onHide={onHide}
            centered
            backdrop="static"
            keyboard={false}
            contentClassName={autoDismiss ? "border-0 shadow-lg text-center" : ""}
            size={autoDismiss ? "sm" : undefined}
        >
            {!autoDismiss && (
                <Modal.Header className="bg-success text-white">
                    <Modal.Title className="fw-bold fs-5">
                        <FaCheckCircle className="me-2" />
                        {title}
                    </Modal.Title>
                </Modal.Header>
            )}

            <Modal.Body className={`py-4 ${autoDismiss ? 'text-center' : ''}`}>
                {autoDismiss && (
                    <div className="mb-3">
                        <FaCheckCircle className="text-success" size={50} />
                    </div>
                )}

                <h4 className="text-success mb-2 fw-bold">{autoDismiss ? title : "Thành công!"}</h4>

                <div className="text-muted mb-3">
                    {message || "Thao tác đã được thực hiện thành công."}
                </div>

                {/* Only show buttons if text is provided */}
                {(primaryBtnText || secondaryBtnText) && (
                    <div className="d-grid gap-2 d-md-block mt-4">
                        {secondaryBtnText && (
                            <Button variant="outline-secondary" className="me-md-2" onClick={onSecondaryAction || onHide}>
                                {secondaryBtnText}
                            </Button>
                        )}

                        {primaryBtnText && (
                            <Button variant="primary" onClick={onPrimaryAction || onHide}>
                                {primaryBtnText}
                            </Button>
                        )}
                    </div>
                )}
            </Modal.Body>
        </Modal>
    );
};

export default SuccessModal;
