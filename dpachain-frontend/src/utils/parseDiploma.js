function parseDiploma(block) {
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
        { key: 'signed_hash', label: 'Signed Hash' }
    ];

    const parsed = order.map(item => ({
        label: item.label,
        value: block[item.key] !== undefined ? block[item.key] : ''
    }));
    return parsed;
}



module.exports = parseDiploma;
