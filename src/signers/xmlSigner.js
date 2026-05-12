import fs from 'fs';
import { createRequire } from 'module';
import { generateTEIFQR, generateUUID } from '../utils/qrGenerator.js';

const require = createRequire(import.meta.url);
const { SignedXml } = require('xml-crypto');

function extractField(xml, tag) {
  const m = xml.match(new RegExp('<' + tag + '(?:\\s[^>]*)?>([^<]+)</' + tag + '>'));
  return m ? m[1] : '';
}

function extractSupplierVAT(xml) {
  const s = xml.match(/<Supplier>[\s\S]*?<\/Supplier>/);
  if (!s) return '';
  const v = s[0].match(/<ID[^>]*>([^<]+)<\/ID>/);
  return v ? v[1] : '';
}

export async function signInvoiceXML(xmlPath, certPath, keyPath) {
  let xml = fs.readFileSync(xmlPath, 'utf8');
  const certRaw = fs.readFileSync(certPath, 'utf8');
  const key = fs.readFileSync(keyPath, 'utf8');

  const certB64 = certRaw
    .replace(/-----BEGIN CERTIFICATE-----/g, '')
    .replace(/-----END CERTIFICATE-----/g, '')
    .replace(/\n/g, '').replace(/\r/g, '').trim();

  // Extract invoice metadata for QR generation (BEFORE signing)
  const supplierVAT = extractSupplierVAT(xml);
  const issueDate = extractField(xml, 'IssueDate');
  const issueTime = extractField(xml, 'IssueTime') || '12:00:00';
  const timestamp = issueDate.replace(/-/g, '') + issueTime.replace(/:/g, '');
  const totalAmount = extractField(xml, 'PayableAmount') || extractField(xml, 'TaxInclusiveAmount') || '0';
  const invoiceId = extractField(xml, 'ID');

  // Remove existing Signature + VisibleElectronicSeal
  xml = xml.replace(/<[a-z0-9-]+:Signature[^>]*>[\s\S]*?<\/[a-z0-9-]+:Signature>/g, '');
  xml = xml.replace(/<Signature[^>]*>[\s\S]*?<\/Signature>/g, '');
  xml = xml.replace(/<VisibleElectronicSeal>[\s\S]*?<\/VisibleElectronicSeal>/g, '');
  xml = xml.replace(/<!--[\s\S]*?-->/g, '');

  // Compute XMLDSig
  const sig = new SignedXml();
  sig.signingKey = key;
  sig.signatureAlgorithm = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256';

  sig.keyInfoProvider = {
    getKeyInfo: function () {
      return '<X509Data><X509Certificate>' + certB64 + '</X509Certificate></X509Data>';
    }
  };

  sig.addReference(
    '/*',
    [
      'http://www.w3.org/2000/09/xmldsig#enveloped-signature',
      'http://www.w3.org/2001/10/xml-exc-c14n#'
    ],
    'http://www.w3.org/2001/04/xmlenc#sha256'
  );

  sig.computeSignature(xml);

  // Get the computed signature XML and extract SignatureValue hash
  const sigXml = sig.getSignatureXml();
  const sigValue = extractField(sigXml, 'SignatureValue');
  const sigHash = sigValue.substring(0, 32);

  // Generate TLV QR code
  const uuid = generateUUID();
  const qrDataUri = await generateTEIFQR({
    vat: supplierVAT,
    timestamp,
    amount: totalAmount,
    sigHash,
    uuid
  });

  // Build the VisibleElectronicSeal with real QR
  const sealXml = `<VisibleElectronicSeal>
    <QRCode>${qrDataUri}</QRCode>
    <VerificationURL>https://verify.elfatoora.tn</VerificationURL>
  </VisibleElectronicSeal>`;

  // Insert seal before </Invoice> (Signature is already appended by xml-crypto)
  let signedXml = sig.getSignedXml();
  signedXml = signedXml.replace('</Invoice>', '  ' + sealXml + '\n</Invoice>');

  return signedXml;
}
