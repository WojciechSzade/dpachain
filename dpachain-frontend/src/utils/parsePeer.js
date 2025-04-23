module.exports = function parsePeer(raw) {
    return {
        nickname: raw.nickname || '',
        address: raw.adress || raw.address || '',
        status: raw.status || '',
        is_authorized: raw.is_authorized,
        public_key: raw.public_key || ''
    };
};