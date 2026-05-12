import fs from 'fs';

export function extractSignatureHash(xmlPath) {
  try {
    const xml = fs.readFileSync(xmlPath, 'utf8');
    const match = xml.match(/<SignatureValue>([^<]+)<\/SignatureValue>/);
    if (!match) {
      console.warn('⚠️  Warning: No SignatureValue found in XML');
      return '';
    }
    const sigValue = match[1];
    return sigValue.substring(0, 32);
  } catch (error) {
    console.error('❌ Error extracting signature hash:', error.message);
    return '';
  }
}
