import QRCode from 'qrcode';
import crypto from 'crypto';

function tlv(tag, value) {
  const buf = Buffer.from(String(value), 'utf8');
  return Buffer.concat([Buffer.from([tag, buf.length]), buf]);
}

export function buildTLVPayload({ vat, timestamp, amount, sigHash, uuid }) {
  return Buffer.concat([
    tlv(0x01, vat),
    tlv(0x02, timestamp),
    tlv(0x03, amount),
    tlv(0x04, sigHash),
    tlv(0x05, uuid)
  ]);
}

export async function generateTEIFQR({ vat, timestamp, amount, sigHash, uuid }) {
  try {
    // Ensure timestamp is in correct format (YYYYMMDDHHmmss)
    let formattedTimestamp = timestamp;
    if (timestamp && timestamp.includes('/')) {
      // Handle DD/MM/YYYY format
      const parts = timestamp.split('/');
      if (parts.length === 3) {
        formattedTimestamp = `${parts[2]}${parts[1]}${parts[0]}000000`;
      }
    } else if (timestamp && timestamp.length === 8) {
      // Handle YYYYMMDD format
      formattedTimestamp = `${timestamp}000000`;
    }
    
    const tlvBuf = buildTLVPayload({ vat, timestamp: formattedTimestamp, amount, sigHash, uuid });
    
    // Generate QR code without data URI prefix
    const qrData = await QRCode.toDataURL(tlvBuf.toString('latin1'), {
      width: 300,
      margin: 1,
      errorCorrectionLevel: 'M'
    });
    
    // Remove data URI prefix if present
    if (qrData.startsWith('data:image/png;base64,')) {
      return qrData.substring('data:image/png;base64,'.length);
    }
    
    return qrData;
  } catch (error) {
    console.error('❌ Error generating QR code:', error.message);
    throw error;
  }
}

export function generateUUID() {
  return crypto.randomUUID();
}
