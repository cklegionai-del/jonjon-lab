// PDF Generator for Fawtara (using html-pdf-node)
// Usage: generateInvoicePDF(htmlString, outputPath)

import { Pdf } from 'html-pdf-node';
import { generateTEIFQR } from '../utils/qrGenerator.js';
import { extractSignatureHash } from '../utils/xmlUtils.js';

const pdf = new Pdf();

export async function generateInvoicePDF(htmlString, outputPath, invoice, signedXmlPath = null) {
  const options = { 
    format: 'A4',
    printBackground: true,
    margin: { top: '10mm', right: '10mm', bottom: '10mm', left: '10mm' }
  };

  try {
    // Generate QR code
    const vat = invoice.supplier.vat || invoice.supplier.taxId || '000000000';
    
    // Format timestamp as YYYYMMDDHHmmss
    const date = new Date(invoice.issueDate);
    let timestamp = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}${String(date.getHours()).padStart(2, '0')}${String(date.getMinutes()).padStart(2, '0')}${String(date.getSeconds()).padStart(2, '0')}`;
    
    const amount = invoice.legalMonetaryTotal.payableAmount.toFixed(3);
    const uuid = invoice.id || generateUUID();
    
    // Get real signature hash if signed XML is provided
    let sigHash = '';
    if (signedXmlPath) {
      sigHash = extractSignatureHash(signedXmlPath);
    }
    
    const qrBase64 = await generateTEIFQR({ vat, timestamp, amount, sigHash, uuid });
    
    // Convert base64 to buffer for pdf-lib
    const qrBuffer = Buffer.from(qrBase64, 'base64');
    
    // Inject QR code into HTML with better sizing and background
    const qrHtml = `
      <div style="position: absolute; bottom: 20px; right: 20px; width: 100px; height: 100px; background-color: white; padding: 2px;">
        <img src="data:image/png;base64,${qrBase64}" style="width: 100px; height: 100px;" alt="QR Code" />
        <div style="font-size: 7px; color: gray; text-align: center; margin-top: 2px;">امسح للتحقق</div>
      </div>
    `;
    
    const htmlWithQr = htmlString.replace('</body>', `${qrHtml}</body>`);
    
    const file = await pdf.generatePdf({ content: htmlWithQr }, options);
    
    // Save to file using Node.js fs
    import { writeFileSync, mkdirSync } from 'fs';
    import { dirname } from 'path';
    
    const dir = dirname(outputPath);
    mkdirSync(dir, { recursive: true });
    writeFileSync(outputPath, file);
    
    console.log(`✅ PDF saved to: ${outputPath}`);
    return true;
  } catch (error) {
    console.error('❌ PDF generation error:', error.message);
    return false;
  }
}

// Helper function to generate UUID (since it's not imported from qrGenerator.js)
function generateUUID() {
  return crypto.randomUUID();
}
