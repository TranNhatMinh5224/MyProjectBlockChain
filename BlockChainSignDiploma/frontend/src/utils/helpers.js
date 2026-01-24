// Format date
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// Truncate hash for display
export const truncateHash = (hash, startChars = 8, endChars = 8) => {
  if (!hash) return '';
  if (hash.length <= startChars + endChars) return hash;
  return `${hash.slice(0, startChars)}...${hash.slice(-endChars)}`;
};

// Get status badge color
export const getStatusColor = (status) => {
  switch (status) {
    case 'ACTIVE':
    case 'APPROVED':
      return 'success';
    case 'PENDING':
      return 'warning';
    case 'REJECTED':
    case 'REVOKED':
      return 'danger';
    default:
      return 'secondary';
  }
};

// Get role badge color
export const getRoleColor = (role) => {
  switch (role) {
    case 'MINISTRY':
      return 'primary';
    case 'SCHOOL':
      return 'info';
    default:
      return 'secondary';
  }
};

// Copy to clipboard
export const copyToClipboard = (text) => {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text);
    return true;
  }
  return false;
};

// Download text as file
export const downloadText = (text, filename) => {
  const blob = new Blob([text], { type: 'text/plain' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};
