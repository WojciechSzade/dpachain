/**
 * Parses a diploma (block) object and returns an array of fields in the desired order.
 * Adjust the `order` array below to change which fields appear and in what order.
 */
function parseDiploma(block) {
    // Define the desired order and labels for each field
    const order = [
        { key: '_id', label: 'Block ID' },
        { key: 'timestamp', label: 'Timestamp' },
        { key: 'diploma_type', label: 'Diploma Type' },
        { key: 'pdf_hash', label: 'PDF Hash' },
        { key: 'authors', label: 'Authors' },
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
        { key: 'signed_hash', label: 'Signed Hash' }
    ];

    // Map each field to an object containing its label and value.
    // If a field is missing, we show an empty string.
    const parsed = order.map(item => ({
        label: item.label,
        value: block[item.key] !== undefined ? block[item.key] : ''
    }));
    return parsed;
}

module.exports = parseDiploma;
