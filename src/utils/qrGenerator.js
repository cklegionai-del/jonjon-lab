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
  const tlvBuf = buildTLVPayload({ vat, timestamp, amount, sigHash, uuid });
  // Latin1 preserves all byte values for QR byte-mode encoding
  const dataUri = await QRCode.toDataURL(tlvBuf.toString('latin1'), {
    width: 200,
    margin: 2,
    errorCorrectionLevel: 'M'
  });
  return dataUri;
}

export function generateUUID() {
  return crypto.randomUUID();
}
