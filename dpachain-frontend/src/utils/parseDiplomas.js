const parseDiploma = require('../utils/parseDiploma');

function parseDiplomas(data) {
    const order = [
        { key: '_id', label: 'Block ID' },
        { key: 'diploma_type', label: 'Diploma Type' },
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
        { key: 'hash', label: 'Hash' },
    ];

    const labels = order.map(item => item.label);
    const blocks = data.map(block =>
        order.map(item => ({
            value: block[item.key] !== undefined ? block[item.key] : ''
        }))
    );

    return [labels, blocks];
}

module.exports = parseDiplomas;
