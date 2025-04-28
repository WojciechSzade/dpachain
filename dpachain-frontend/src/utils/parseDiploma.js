const order = [
    { key: '_id', label: 'Block ID' },
    { key: 'timestamp', label: 'Timestamp' },
    { key: 'diploma_type', label: 'Diploma Type' },
    { key: 'pdf_hash', label: 'PDF Hash' },
    { key: 'authors', label: 'Authors' },
    { key: 'authors_id', label: 'Authors IDs' },
    { key: 'title', label: 'Title' },
    { key: 'language', label: 'Language' },
    { key: 'discipline', label: 'Discipline' },
    { key: 'is_defended', label: 'Is Defended' },
    { key: 'date_of_defense', label: 'Date of Defense' },
    { key: 'university', label: 'University' },
    { key: 'faculty', label: 'Faculty' },
    { key: 'supervisor', label: 'Supervisor' },
    { key: 'reviewer', label: 'Reviewer' },
    { key: 'additional_info', label: 'Additional Info' },
    { key: 'peer_author', label: 'Peer Author' },
    { key: 'chain_version', label: 'Chain Version' },
    { key: 'hash', label: 'Hash' },
    { key: 'signed_hash', label: 'Signed Hash' },
    { key: 'jwt_token', label: 'JWT Token' },
];


const orderSummary = [
    { key: 'title', label: 'Title' },
    { key: 'diploma_type', label: 'Diploma Type' },
    { key: 'authors', label: 'Authors' },
    { key: 'date_of_defense', label: 'Date of Defense' },
    { key: 'faculty', label: 'Faculty' },
    { key: 'supervisor', label: 'Supervisor' },
    { key: 'university', label: 'University' },
    { key: 'reviewer', label: 'Reviewer' },
    { key: 'pdf_hash', label: 'PDF Hash' },
];

function parseDiplomaSummary(block) {
    const obj = (block && typeof block === 'object') ? block : {};
    return orderSummary.map(item => {
        let value = obj[item.key] != null ? obj[item.key] : '';
        if (item.key === 'authors' && Array.isArray(value)) {
            const ids = Array.isArray(obj.authors_id) ? obj.authors_id : [];
            value = value.map((name, i) => `${name} (${ids[i] || ''})`).join(', ');
        }
        if (item.key === 'date_of_defense' && typeof value === 'string') {
            value = value.split('T')[0];
        }
        return { label: item.label, value };
    });
}

function parseDiplomaDetails(block) {
    const obj = (block && typeof block === 'object') ? block : {};
    return order.map(item => ({
        label: item.label,
        value: obj[item.key] != null ? obj[item.key] : ''
    }));
}

module.exports = { parseDiplomaSummary, parseDiplomaDetails };