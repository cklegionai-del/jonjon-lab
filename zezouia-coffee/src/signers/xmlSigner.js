import fs from 'fs';
import { SignedXml } from 'xml-crypto';
import { DOMParser } from '@xmldom/xmldom';

export function signInvoiceXML(xmlPath, certPath, keyPath) {
  const xml = fs.readFileSync(xmlPath, 'utf8');
  const doc = new DOMParser().parseFromString(xml);
  const sig = new SignedXml();
  sig.signingKey = fs.readFileSync(keyPath);
  sig.x509Certificate = fs.readFileSync(certPath, 'utf8').replace(/-----BEGIN CERTIFICATE-----|-----END CERTIFICATE-----|\n/g, '');
  sig.addReference({ xpath: "//*[local-name(.)='Invoice']", transforms: ['http://www.w3.org/2000/09/xmldsig#enveloped-signature'], digestAlgorithm: 'http://www.w3.org/2001/04/xmlenc#sha256' });
  sig.signatureAlgorithm = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256';
  sig.canonicalizationAlgorithm = 'http://www.w3.org/2001/10/xml-exc-c14n#';
  sig.keyInfoProvider = { getKeyInfo: () => `<X509Data><X509Certificate>${sig.x509Certificate}</X509Certificate></X509Data>` };
  sig.computeSignature(doc);
  return sig.getSignedXml();
}
