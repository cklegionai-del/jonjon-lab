// PDF Generator for Fawtara (using html-pdf-node)
// Usage: generateInvoicePDF(htmlString, outputPath)

import { Pdf } from 'html-pdf-node';

const pdf = new Pdf();

export async function generateInvoicePDF(htmlString, outputPath) {
  const options = { 
    format: 'A4',
    printBackground: true,
    margin: { top: '10mm', right: '10mm', bottom: '10mm', left: '10mm' }
  };

  try {
    const file = await pdf.generatePdf({ content: htmlString }, options);
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