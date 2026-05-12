// XML Generator for Tunisian Electronic Invoicing (TEIF v1.8.7 compliant)
import { writeFileSync, mkdirSync } from 'fs';
import path from 'path';

export function generateInvoiceXML(invoiceObject) {
  // Safe number formatter with 3 decimal places
  const safeNum = (val) => {
    const n = Number(val);
    return isNaN(n) ? '0.000' : n.toFixed(3);
  };

  // Format date to YYYY-MM-DD
  const formatDate = (dateString) => {
    return dateString;
  };

  // Get VAT code based on rate
  const getVatCode = (rate) => {
    if (rate === 0) return 'Z';
    if (rate === 19) return 'S';
    return 'E'; // Exempt
  };

  // Handle fallbacks for GRAND TOTALS (match both naming conventions)
  const totalHT = safeNum(invoiceObject.totalHT ?? invoiceObject.totalAmount ?? 0);
  const totalVAT = safeNum(invoiceObject.totalTVA ?? invoiceObject.vatAmount ?? 0);
  const totalTTC = safeNum(invoiceObject.totalTTC ?? invoiceObject.totalWithVat ?? 0);

  // Generate issue date and due date
  const issueDate = formatDate(invoiceObject.date);
  const issueTime = invoiceObject.issueTime || "12:00:00";
  
  // Calculate due date (30 days from issue date)
  const dueDate = new Date(issueDate);
  dueDate.setDate(dueDate.getDate() + 30);
  const formattedDueDate = dueDate.toISOString().split('T')[0];

  // Determine invoice type code
  const invoiceTypeCode = invoiceObject.invoiceTypeCode || "380"; // 380 = Invoice, 381 = Credit Note

  // Generate XML structure
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:tn:gov:dgi:teif:1.8"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="urn:tn:gov:dgi:teif:1.8 TEIF_v1.8.7.xsd">
  <ID>${invoiceObject.invoiceNumber}</ID>
  <IssueDate>${issueDate}</IssueDate>
  <IssueTime>${issueTime}</IssueTime>
  <InvoiceTypeCode>${invoiceTypeCode}</InvoiceTypeCode>
  <DocumentCurrencyCode>TND</DocumentCurrencyCode>
  <TaxCurrencyCode>TND</TaxCurrencyCode>
  <DueDate>${formattedDueDate}</DueDate>
  
  <Parties>
    <Supplier>
      <PartyIdentification>
        <ID schemeID="TN_MF">${invoiceObject.supplier.vatNumber}</ID>
      </PartyIdentification>
      <PartyName>
        <Name>${invoiceObject.supplier.name}</Name>
      </PartyName>
      <PostalAddress>
        <StreetName>${invoiceObject.supplier.address}</StreetName>
        <CityName>Tunis</CityName>
        <PostalZone>1000</PostalZone>
        <CountrySubentity>Tunis</CountrySubentity>
        <Country>
          <IdentificationCode>TN</IdentificationCode>
        </Country>
      </PostalAddress>
    </Supplier>
    <Customer>
      <PartyIdentification>
        <ID schemeID="TN_MF">${invoiceObject.customer.vatNumber}</ID>
      </PartyIdentification>
      <PartyName>
        <Name>${invoiceObject.customer.name}</Name>
      </PartyName>
      <PostalAddress>
        <StreetName>${invoiceObject.customer.address}</StreetName>
        <CityName>Tunis</CityName>
        <PostalZone>1000</PostalZone>
        <CountrySubentity>Tunis</CountrySubentity>
        <Country>
          <IdentificationCode>TN</IdentificationCode>
        </Country>
      </PostalAddress>
    </Customer>
  </Parties>
  
  <InvoiceLines>
    ${invoiceObject.items.map((item, index) => {
      // Handle fallbacks for item totals
      const itemTotal = item.totalHT ?? item.total ?? 0;
      const vatCode = getVatCode(item.vatRate);
      
      return `
    <InvoiceLine>
      <ID>${index + 1}</ID>
      <InvoicedQuantity unitCode="HUR">${safeNum(item.quantity)}</InvoicedQuantity>
      <LineExtensionAmount currencyID="TND">${safeNum(itemTotal)}</LineExtensionAmount>
      <Item>
        <Name>${item.description}</Name>
        <ClassifiedTaxCategory>
          <ID>${vatCode}</ID>
          <Percent>${item.vatRate}</Percent>
          <TaxScheme>
            <ID>TVA</ID>
          </TaxScheme>
        </ClassifiedTaxCategory>
      </Item>
      <Price>
        <PriceAmount currencyID="TND">${safeNum(item.unitPrice)}</PriceAmount>
        <BaseQuantity unitCode="HUR">1</BaseQuantity>
      </Price>
    </InvoiceLine>`;
    }).join('')}
  </InvoiceLines>
  
  <TaxTotal>
    <TaxAmount currencyID="TND">${totalVAT}</TaxAmount>
    <TaxSubtotal>
      <TaxableAmount currencyID="TND">${totalHT}</TaxableAmount>
      <TaxAmount currencyID="TND">${totalVAT}</TaxAmount>
      <TaxCategory>
        <ID>S</ID>
        <Percent>19</Percent>
        <TaxScheme>
          <ID>TVA</ID>
        </TaxScheme>
      </TaxCategory>
    </TaxSubtotal>
  </TaxTotal>
  
  <LegalMonetaryTotal>
    <LineExtensionAmount currencyID="TND">${totalHT}</LineExtensionAmount>
    <TaxExclusiveAmount currencyID="TND">${totalHT}</TaxExclusiveAmount>
    <TaxInclusiveAmount currencyID="TND">${totalTTC}</TaxInclusiveAmount>
    <PayableAmount currencyID="TND">${totalTTC}</PayableAmount>
  </LegalMonetaryTotal>
  
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#" Id="placeholder">
    <SignedInfo>
      <CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
      <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
    </SignedInfo>
    <SignatureValue>PLACEHOLDER_REPLACE_BY_SIGNER</SignatureValue>
    <KeyInfo>
      <X509Data>
        <X509Certificate>PLACEHOLDER_REPLACE_BY_SIGNER</X509Certificate>
      </X509Data>
    </KeyInfo>
  </Signature>

  <VisibleElectronicSeal>
    <QRCode>data:image/png;base64,PLACEHOLDER_REPLACE_BY_SIGNER</QRCode>
    <VerificationURL>https://verify.elfatoora.tn</VerificationURL>
  </VisibleElectronicSeal>
</Invoice>`;

  return xml;
}

// Save XML to file
export function saveXMLToFile(xmlString, filePath) {
  const absPath = path.resolve(filePath);
  const dir = path.dirname(absPath);
  mkdirSync(dir, { recursive: true });
  writeFileSync(absPath, xmlString, 'utf8');
  console.log(`✅ XML saved to: ${absPath}`);
}
